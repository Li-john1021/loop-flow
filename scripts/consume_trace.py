#!/usr/bin/env python3
"""Consume append-only loop-flow Trace files and propose bounded optimizations."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


EVENT_ID_RE = re.compile(r"^EVT-[0-9]{3,}$")
ROOT_CAUSES = {"prompt", "decomposition", "workflow", "capability_mismatch", "environment", "insufficient_evidence"}
EVENT_KINDS = {"plan_drafted", "plan_annotated", "plan_reconciled", "plan_approved", "spec_frozen", "unit_dispatched", "unit_completed", "unit_failed", "unit_blocked", "review_started", "review_completed", "repair_created", "build_completed", "build_not_applicable", "test_completed", "test_not_available", "cycle_reconciled", "user_decision", "retrospective_requested", "optimization_proposed", "optimization_rolled_back"}
STATUSES = {"observed", "requested", "succeeded", "failed", "blocked", "approved", "not_available"}
TRIGGER_KINDS = {"unit_failed", "unit_blocked", "review_completed", "test_completed"}
FAILURE_STATUSES = {"failed", "blocked"}
PROPOSAL_TYPES = {
    "prompt": "prompt_change",
    "decomposition": "split_unit",
    "workflow": "review_rule_change",
    "capability_mismatch": "model_upgrade",
    "environment": "environment_fix",
    "insufficient_evidence": "no_change",
}


class ConsumerFailure(ValueError):
    pass


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ConsumerFailure(f"invalid JSON: {path}: {exc}") from exc


def trace_files(trace_path: Path) -> list[Path]:
    if trace_path.is_file():
        return [trace_path]
    if not trace_path.is_dir():
        raise ConsumerFailure(f"trace path does not exist: {trace_path}")
    files = sorted(set(trace_path.glob("*.jsonl")) | set(trace_path.glob("*.ndjson")))
    if not files:
        raise ConsumerFailure(f"no .jsonl or .ndjson Trace files found: {trace_path}")
    return files


def load_events(files: Iterable[Path]) -> tuple[list[tuple[Path, dict[str, Any]]], list[str]]:
    events: list[tuple[Path, dict[str, Any]]] = []
    unresolved: list[str] = []
    for path in files:
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except OSError as exc:
            unresolved.append(f"{path.name}: cannot read Trace file ({exc})")
            continue
        for line_number, line in enumerate(lines, 1):
            if not line.strip():
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError as exc:
                unresolved.append(f"{path.name}:{line_number}: invalid JSON ({exc.msg})")
                continue
            if not isinstance(event, dict):
                unresolved.append(f"{path.name}:{line_number}: event is not an object")
                continue
            events.append((path, event))
    return events, unresolved


def validate_event_shape(event: dict[str, Any]) -> None:
    for key in ("schema_version", "event_id", "event_kind", "at", "actor", "status", "refs"):
        if key not in event:
            raise ConsumerFailure(f"event missing {key}")
    if event.get("schema_version") != "1.0":
        raise ConsumerFailure("unsupported Trace schema_version")
    if not isinstance(event.get("event_id"), str) or not EVENT_ID_RE.fullmatch(event["event_id"]):
        raise ConsumerFailure("invalid event_id")
    if event.get("event_kind") not in EVENT_KINDS:
        raise ConsumerFailure("invalid event_kind")
    if event.get("status") not in STATUSES:
        raise ConsumerFailure("invalid event status")
    if not isinstance(event.get("refs"), list):
        raise ConsumerFailure("refs must be an array")
    if "capability_requirements" in event and not isinstance(event["capability_requirements"], list):
        raise ConsumerFailure("capability_requirements must be an array")
    if "capability_source" in event and event["capability_source"] not in {"host_reported", "task_declared", "user_declared", "observed", "unknown"}:
        raise ConsumerFailure("invalid capability_source")
    if "attempts" in event and (not isinstance(event["attempts"], int) or event["attempts"] < 1):
        raise ConsumerFailure("attempts must be a positive integer")
    if "root_cause_hint" in event and event["root_cause_hint"] not in ROOT_CAUSES:
        raise ConsumerFailure("invalid root_cause_hint")


def actual_model_id(events: list[dict[str, Any]]) -> str | None:
    actual_model = next((event.get("actual_model_id") for event in events if event.get("actual_model_id")), None)
    if actual_model:
        return actual_model
    return next((event.get("usage", {}).get("model_id") for event in events if isinstance(event.get("usage"), dict) and event["usage"].get("model_id")), None)


def capability_evidence_complete(events: list[dict[str, Any]]) -> bool:
    sources = {event.get("capability_source") for event in events}
    requirements = [item for event in events for item in event.get("capability_requirements", []) if isinstance(item, str) and item.strip()]
    expected = any(event.get("expected_model_tier") for event in events)
    actual = actual_model_id(events)
    selected = any(isinstance(event.get("selection_reason"), str) and event["selection_reason"].strip() for event in events)
    return bool(requirements) and bool(sources & {"host_reported", "task_declared", "user_declared", "observed"}) and expected and bool(actual) and selected


def confidence_for(events: list[dict[str, Any]], hint: str) -> str:
    if hint == "insufficient_evidence":
        return "low"
    attempts = max((event.get("attempts", 1) for event in events), default=1)
    corroborated = len(events) >= 2 and attempts >= 2
    if hint == "capability_mismatch":
        if not capability_evidence_complete(events):
            return "low"
        if corroborated:
            return "high"
        return "medium"
    if corroborated:
        return "high"
    return "medium"


def candidate_for(events: list[dict[str, Any]], candidate_number: int, *, hint_override: str | None = None) -> dict[str, Any]:
    hint = hint_override or events[0].get("root_cause_hint", "insufficient_evidence")
    unit_ref = next((event.get("unit_ref") for event in events if event.get("unit_ref")), None)
    expected_tier = next((event.get("expected_model_tier") for event in events if event.get("expected_model_tier")), None)
    actual_model = actual_model_id(events)
    capabilities = sorted({item for event in events for item in event.get("capability_requirements", []) if isinstance(item, str)})
    source_refs = [event["event_id"] for event in events]
    observed_facts = [f"{event['event_id']}: {event.get('plan_ref', '-')}/{event.get('spec_ref', '-')}/{event.get('unit_ref', '-')}: {event.get('event_kind')}/{event.get('status')}" for event in events]
    attempts = [event.get("attempts") for event in events if isinstance(event.get("attempts"), int)]
    if attempts:
        observed_facts.append(f"attempts_max={max(attempts)}")
    label = unit_ref or "current cycle"
    proposal_type = PROPOSAL_TYPES[hint]
    proposal_text = {
        "prompt": "收紧当前任务合同，而不是增加全局叙述。",
        "decomposition": "缩小或拆分当前 Work Unit，保持每个单元可独立验收。",
        "workflow": "调整当前周期的 Review、测试或恢复顺序。",
        "capability_mismatch": "在合同不变的前提下升级模型或切换专职 Agent，不把失败归咎于提示词。",
        "environment": "补齐当前任务需要的工具、权限或依赖，并保留阻断证据。",
        "insufficient_evidence": "先补充可观察证据，不提出全局流程修改。",
    }[hint]
    changes = {
        "prompt": ["增加与该失败直接对应的允许路径、Acceptance 或停止条件。"],
        "decomposition": ["将当前单元拆为更小的有界单元，并为每个单元定义独立 Acceptance。"],
        "workflow": ["调整当前周期的阶段顺序或门控，不改变用户批准权。"],
        "capability_mismatch": ["使用更高模型层级或专职 Agent 重跑同一合同。", "保留原模型结果作为对照。"],
        "environment": ["在任务范围内补齐缺失能力，或明确记录不可用并停止。"],
        "insufficient_evidence": ["补充实际 Artifact、Evidence、退出码或宿主能力声明。"],
    }[hint]
    return {
        "schema_version": "1.0",
        "candidate_id": f"OPT-{candidate_number:03d}",
        "source_trace_refs": source_refs,
        "root_cause_class": hint,
        "confidence": confidence_for(events, hint),
        "observed_facts": observed_facts,
        "hypothesis": f"{label} 的失败事件显式标记为 {hint}；该标记是待验证假设，不是因果证明。",
        "proposal_type": proposal_type,
        "proposal": {"summary": proposal_text, "changes": changes, "scope": "unit" if unit_ref else "cycle"},
        "evaluation_plan": {
            "held_out": ["在未使用本次失败样本的同类任务上重跑。"],
            "adversarial": ["构造越界、缺证据或错误状态输入，确认门控仍拒绝。"],
            "regression": ["重跑当前周期原有验收和已有回归测试。"],
            "success_criteria": ["质量不下降，且候选对应的失败现象消失或被诚实阻断。"],
        },
        **({"expected_model_tier": expected_tier} if expected_tier else {}),
        **({"actual_model_id": actual_model} if actual_model else {}),
        **({"capability_requirements": capabilities} if capabilities else {}),
        "risk": "high" if hint in {"workflow", "capability_mismatch"} else "medium",
        "status": "proposed",
        "user_approval_required": True,
    }


def consume_trace(trace_path: Path, root: Path, *, require_jsonschema: bool = False) -> dict[str, Any]:
    files = trace_files(trace_path)
    raw_events, unresolved = load_events(files)
    schema_validator = None
    schema_engine = "structural_only"
    try:
        from jsonschema import Draft202012Validator  # type: ignore
    except ImportError:
        if require_jsonschema:
            raise ConsumerFailure("jsonschema is not installed; rerun without --require-jsonschema or install it")
    else:
        schema_engine = "draft2020-12"
        schema = load_json(root / "schemas" / "trace-event.schema.json")
        Draft202012Validator.check_schema(schema)
        schema_validator = Draft202012Validator(schema)
    valid_events: list[dict[str, Any]] = []
    for path, event in raw_events:
        try:
            validate_event_shape(event)
            if schema_validator is not None:
                schema_validator.validate(event)
        except Exception as exc:
            unresolved.append(f"{path.name}:{event.get('event_id', '?')}: {exc}")
            continue
        valid_events.append(event)
    groups: dict[tuple[str, str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for event in valid_events:
        if event.get("event_kind") not in TRIGGER_KINDS or event.get("status") not in FAILURE_STATUSES:
            continue
        hint = event.get("root_cause_hint")
        grouping_hint = hint
        if hint is None:
            unresolved.append(f"{event['event_id']}: no actionable root_cause_hint; no workflow change proposed")
            continue
        if hint == "insufficient_evidence":
            unresolved.append(f"{event['event_id']}: insufficient evidence; no workflow change proposed")
            continue
        if hint == "capability_mismatch" and not capability_evidence_complete([event]):
            unresolved.append(f"{event['event_id']}: capability_mismatch lacks complete capability selection facts; downgraded to insufficient_evidence")
            grouping_hint = "insufficient_evidence"
        groups[(grouping_hint, event.get("plan_ref") or "-", event.get("spec_ref") or "-", event.get("unit_ref") or "cycle")].append(event)
    candidates = [candidate_for(groups[key], index, hint_override=key[0]) for index, key in enumerate(sorted(groups), 1)]
    return {
        "schema_version": "1.0",
        "report_id": f"trace-consumer-{trace_path.name}",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "trace_files": [path.name for path in files],
        "event_count": len(valid_events),
        "candidate_count": len(candidates),
        "schema_engine": schema_engine,
        "candidates": candidates,
        "unresolved": unresolved,
        "status": "revise" if unresolved else "pass",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trace-dir", type=Path, required=True)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path)
    parser.add_argument("--require-jsonschema", action="store_true")
    args = parser.parse_args()
    try:
        report = consume_trace(args.trace_dir, args.root, require_jsonschema=args.require_jsonschema)
    except ConsumerFailure as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        return 2
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        try:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(rendered, encoding="utf-8")
        except OSError as exc:
            print(json.dumps({"ok": False, "error": f"cannot write report: {exc}"}, ensure_ascii=False))
            return 2
    print(rendered, end="")
    return 2 if report["unresolved"] else 0


if __name__ == "__main__":
    sys.exit(main())

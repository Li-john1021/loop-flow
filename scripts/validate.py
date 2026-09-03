#!/usr/bin/env python3
"""Optional offline validator for the loop-flow resource bundle."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


SHA256_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
TRACE_RE = re.compile(r"^EVT-[0-9]{3,}$")
REQ_RE = re.compile(r"^REQ-[0-9]{3,}$")
AC_RE = re.compile(r"^AC-[0-9]{3,}$")
WU_RE = re.compile(r"^WU-[0-9]{3,}$")


class ValidationFailure(ValueError):
    pass


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValidationFailure(f"invalid JSON: {path}: {exc}") from exc


def canonical_plan_fingerprint(plan: dict[str, Any]) -> str:
    value = json.loads(json.dumps(plan, ensure_ascii=False))
    value.pop("approval", None)
    value.pop("plan_fingerprint", None)
    payload = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationFailure(message)


def validate_annotations(plan: dict[str, Any]) -> None:
    annotations = plan.get("annotations", [])
    require(isinstance(annotations, list), "plan annotations must be an array")
    plan_id = plan.get("plan_id")
    plan_version = plan.get("plan_version")
    closed_statuses = {"accepted", "rejected", "resolved"}
    pending_statuses = {"open", "answered"}
    for annotation in annotations:
        require(isinstance(annotation, dict), "plan annotation must be an object")
        require(annotation.get("plan_ref") == plan_id, f"annotation plan_ref mismatch: {annotation.get('annotation_id')}")
        require(annotation.get("plan_version") == plan_version, f"annotation plan_version mismatch: {annotation.get('annotation_id')}")
        options = annotation.get("options", [])
        require(isinstance(options, list) and len(options) >= 2, f"annotation needs at least two options: {annotation.get('annotation_id')}")
        require(all(isinstance(item, dict) for item in options), f"annotation options must be objects: {annotation.get('annotation_id')}")
        option_ids = [item.get("id") for item in options]
        require(len(option_ids) == len(set(option_ids)), f"annotation option ids must be unique: {annotation.get('annotation_id')}")
        status = annotation.get("status")
        answer = annotation.get("answer")
        other = annotation.get("other")
        has_answer = answer is not None
        has_other = isinstance(other, str) and bool(other.strip())
        if has_answer:
            require(any(isinstance(item, dict) and item.get("value") == answer for item in options), f"annotation answer is not one of its options: {annotation.get('annotation_id')}")
        if status == "answered" or status == "accepted" or status == "resolved":
            require(has_answer != has_other, f"answered annotation needs exactly one answer or other: {annotation.get('annotation_id')}")
        elif status == "rejected":
            require(not has_answer and has_other, f"rejected annotation needs an explanation in other: {annotation.get('annotation_id')}")
        elif status == "open":
            require(not has_answer and not has_other, f"open annotation cannot contain an answer: {annotation.get('annotation_id')}")
        else:
            require(isinstance(status, str) and status in closed_statuses | pending_statuses, f"invalid annotation status: {annotation.get('annotation_id')}")
    approval = plan.get("approval")
    approval_status = approval.get("status") if isinstance(approval, dict) else None
    approved = plan.get("status") == "approved" or plan.get("approval_status") == "approved" or approval_status == "approved"
    if approved:
        require(all(not item.get("required") or item.get("status") in closed_statuses for item in annotations), "approved plan has unresolved required annotations")


def validate_plan_semantics(plan: dict[str, Any]) -> None:
    require(isinstance(plan, dict), "plan must be a JSON object")
    validate_annotations(plan)
    if plan.get("mode") == "tier1":
        require(isinstance(plan.get("goal"), str) and bool(plan["goal"].strip()), "tier1 goal must be non-empty")
        require(isinstance(plan.get("acceptance"), str) and bool(plan["acceptance"].strip()), "tier1 acceptance must be non-empty")
        require(isinstance(plan.get("forbidden"), list), "tier1 forbidden must be an array")
        approval_status = plan.get("approval_status", "not_requested")
        require(isinstance(approval_status, str) and approval_status in {"not_requested", "requested", "approved", "rejected"}, "invalid tier1 approval_status")
        return
    require(plan.get("plan_id", "").startswith("plan:"), "plan_id must start with plan:")
    approval = plan.get("approval", {})
    require(isinstance(approval, dict), "plan approval must be an object")
    status = plan.get("status")
    approval_status = approval.get("status")
    require(status == "approved" or approval_status != "approved", "approved approval requires approved plan status")
    require(approval_status == "approved" or status != "approved", "approved plan requires approved approval status")
    if approval_status == "approved":
        for key in ("approved_by", "approved_at", "approved_plan_fingerprint"):
            require(approval.get(key), f"approved plan missing {key}")
        expected = canonical_plan_fingerprint(plan)
        require(approval["approved_plan_fingerprint"] == expected, "approved plan fingerprint mismatch")
    for req in plan.get("requirements", []):
        require(isinstance(req, dict), "plan requirement must be an object")
        require(REQ_RE.fullmatch(req.get("id", "")), f"invalid requirement id: {req.get('id')}")
    requirement_ids = {item["id"] for item in plan.get("requirements", [])}
    for item in plan.get("acceptance", []):
        require(isinstance(item, dict), "plan acceptance must be an object")
        require(AC_RE.fullmatch(item.get("id", "")), f"invalid acceptance id: {item.get('id')}")
        require(set(item.get("proves", [])) <= requirement_ids, f"acceptance references unknown requirement: {item.get('id')}")


def validate_cycle_semantics(cycle: dict[str, Any], plan: dict[str, Any] | None = None) -> None:
    require(isinstance(cycle, dict), "cycle spec must be a JSON object")
    requirements = cycle.get("requirements", [])
    acceptances = cycle.get("acceptance", [])
    units = cycle.get("units", [])
    require(isinstance(requirements, list), "cycle requirements must be an array")
    require(isinstance(acceptances, list), "cycle acceptance must be an array")
    require(isinstance(units, list), "cycle units must be an array")
    requirement_ids = {item.get("id") for item in requirements if isinstance(item, dict)}
    acceptance_ids = {item.get("id") for item in acceptances if isinstance(item, dict)}
    unit_ids = {item.get("id") for item in units if isinstance(item, dict)}
    require(cycle.get("spec_id", "").startswith("spec:"), "spec_id must start with spec:")
    require(cycle.get("plan_ref", "").startswith("plan:"), "plan_ref must start with plan:")
    if plan is not None:
        require(cycle.get("plan_ref") == plan.get("plan_id"), "cycle plan_ref does not match plan_id")
        cycle_version = cycle.get("plan_version")
        plan_version = plan.get("plan_version")
        if isinstance(cycle_version, int) and isinstance(plan_version, int) and cycle_version < plan_version:
            raise ValidationFailure("cycle spec is stale; run spec again for the current Plan version")
        require(cycle_version == plan_version, "cycle plan_version mismatch")
        require(cycle.get("plan_fingerprint") == canonical_plan_fingerprint(plan), "cycle plan_fingerprint mismatch")
        plan_req_ids = {item.get("id") for item in plan.get("requirements", []) if isinstance(item, dict)}
        plan_ref_prefix = plan.get("plan_id", "") + "#"
        for item in requirements:
            require(isinstance(item, dict), "cycle requirement must be an object")
            source_refs = set(item.get("source_refs", []))
            require(bool(source_refs & plan_req_ids) or any(ref.startswith(plan_ref_prefix) and ref.removeprefix(plan_ref_prefix) in plan_req_ids for ref in source_refs), f"cycle requirement has no Plan source: {item.get('id')}")
    for item in acceptances:
        require(isinstance(item, dict), "cycle acceptance must be an object")
        require(set(item.get("proves", [])) <= requirement_ids, f"cycle acceptance references unknown requirement: {item.get('id')}")
    for unit in units:
        require(isinstance(unit, dict), "work unit must be an object")
        unit_id = unit.get("id", "")
        require(WU_RE.fullmatch(unit_id), f"invalid work unit id: {unit.get('id')}")
        require(set(unit.get("requirement_refs", [])) <= requirement_ids, f"unknown requirement ref in {unit_id}")
        require(set(unit.get("acceptance_refs", [])) <= acceptance_ids, f"unknown acceptance ref in {unit_id}")
        require(set(unit.get("depends_on", [])) <= unit_ids, f"unknown dependency in {unit_id}")
        impact = unit.get("code_impact")
        policy = unit.get("code_review_policy")
        sequence = unit.get("review_sequence")
        if impact in {"critical", "material"}:
            require(policy == "required" and sequence == "code_review_then_spec_review", f"important code review mismatch in {unit_id}")
        elif impact == "limited":
            require(policy in {"required", "optional"}, f"limited code cannot be not_applicable in {unit_id}")
        else:
            require(impact == "none", f"unknown code impact in {unit_id}")
            require(policy == "not_applicable" and sequence == "spec_review_only", f"none code review mismatch in {unit_id}")
    edges = {item.get("id"): set(item.get("depends_on", [])) for item in units if isinstance(item, dict)}
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str) -> None:
        require(node not in visiting, f"work unit dependency cycle at {node}")
        if node in visited:
            return
        visiting.add(node)
        for dependency in edges.get(node, set()):
            visit(dependency)
        visiting.remove(node)
        visited.add(node)

    for node in edges:
        visit(node)
    require(requirement_ids <= {ref for unit in units for ref in unit.get("requirement_refs", []) if isinstance(unit, dict)}, "not every cycle requirement is covered by a work unit")


def validate_work_log(path: Path) -> None:
    log = load_json(path)
    for section in ("units", "reviews", "tests", "decisions"):
        for item in log.get(section, []):
            for event_id in item.get("trace_event_refs", []):
                require(TRACE_RE.fullmatch(event_id), f"invalid trace event ref: {event_id}")


def validate_command_manifest(root: Path) -> list[str]:
    manifest_path = root / "commands" / "manifest.json"
    manifest = load_json(manifest_path)
    require(isinstance(manifest, dict), "command manifest must be an object")
    require(manifest.get("schema_version") == "1.0", "unsupported command manifest schema_version")
    require(manifest.get("skill") == "loop-flow", "command manifest skill must be loop-flow")
    commands = manifest.get("commands")
    require(isinstance(commands, list) and commands, "command manifest commands must be a non-empty array")
    ids: list[str] = []
    for command in commands:
        require(isinstance(command, dict), "command manifest entry must be an object")
        command_id = command.get("id")
        prompt_ref = command.get("prompt")
        require(isinstance(command_id, str) and re.fullmatch(r"[a-z][a-z0-9-]*", command_id), f"invalid command id: {command_id}")
        require(command_id not in ids, f"duplicate command id: {command_id}")
        require(isinstance(prompt_ref, str) and prompt_ref.startswith("prompts/"), f"invalid prompt ref for {command_id}")
        require((root / "commands" / prompt_ref).is_file(), f"missing command prompt: {prompt_ref}")
        ids.append(command_id)
    return ids


def validate_bundle(root: Path, *, require_jsonschema: bool) -> dict[str, Any]:
    schemas_dir = root / "schemas"
    schemas = {
        schema_path.name: load_json(schema_path)
        for schema_path in sorted(schemas_dir.glob("*.json"))
    }
    schema_engine = "structural_only"
    schema_validator = None
    try:
        from jsonschema import Draft202012Validator  # type: ignore
    except ImportError:
        if require_jsonschema:
            raise ValidationFailure("jsonschema is not installed; rerun without --require-jsonschema or install it")
    else:
        schema_engine = "draft2020-12"
        schema_validator = Draft202012Validator
        for schema_path in sorted(schemas_dir.glob("*.json")):
            Draft202012Validator.check_schema(load_json(schema_path))
    annotation_schema = schemas["plan-annotation.schema.json"]
    annotation_contract = {key: value for key, value in annotation_schema.items() if key not in {"$schema", "$id", "title", "description"}}
    require(schemas["plan.schema.json"].get("$defs", {}).get("plan_annotation") == annotation_contract, "plan annotation contract drift between standalone and full Plan schemas")
    require(schemas["plan-lite.schema.json"].get("properties", {}).get("annotations", {}).get("items") == annotation_contract, "plan annotation contract drift between standalone and Tier 1 schemas")
    command_ids = validate_command_manifest(root)
    examples_dir = root / "examples"
    example_map = {
        "tier1-plan.example.json": "plan-lite.schema.json",
        "full-plan.example.json": "plan.schema.json",
        "cycle-spec.example.json": "cycle-spec.schema.json",
        "plan-annotation.example.json": "plan-annotation.schema.json",
    }
    if schema_validator is not None:
        for example_name, schema_name in example_map.items():
            schema_validator(schemas[schema_name]).validate(load_json(examples_dir / example_name))
    plan = load_json(examples_dir / "full-plan.example.json")
    cycle = load_json(examples_dir / "cycle-spec.example.json")
    validate_plan_semantics(plan)
    validate_cycle_semantics(cycle, plan)
    return {"schema_engine": schema_engine, "schemas": len(list(schemas_dir.glob("*.json"))), "examples": ["tier1-plan", "full-plan", "cycle-spec", "plan-annotation"], "commands": command_ids}


def validate_external_schema(root: Path, record: Any, schema_name: str, *, required: bool) -> None:
    try:
        from jsonschema import Draft202012Validator, ValidationError as JsonSchemaValidationError  # type: ignore
    except ImportError:
        if required:
            raise ValidationFailure("jsonschema is not installed; cannot validate external record")
        return
    schema = load_json(root / "schemas" / schema_name)
    Draft202012Validator.check_schema(schema)
    try:
        Draft202012Validator(schema).validate(record)
    except JsonSchemaValidationError as exc:
        raise ValidationFailure(f"schema validation failed: {exc.message}") from exc


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--plan", type=Path, help="optional plan JSON to validate")
    parser.add_argument("--cycle-spec", type=Path, help="optional cycle spec JSON to validate")
    parser.add_argument("--work-log", type=Path, help="optional work log JSON to validate")
    parser.add_argument("--fingerprint-plan", type=Path, help="print the canonical SHA-256 fingerprint for a Plan JSON")
    parser.add_argument("--require-jsonschema", action="store_true")
    args = parser.parse_args()
    try:
        if args.fingerprint_plan:
            plan = load_json(args.fingerprint_plan)
            require(isinstance(plan, dict), "fingerprint plan must be a JSON object")
            print(canonical_plan_fingerprint(plan))
            return 0
        result = validate_bundle(args.root, require_jsonschema=args.require_jsonschema)
        external_plan = None
        if args.plan:
            external_plan = load_json(args.plan)
            plan_schema = "plan-lite.schema.json" if isinstance(external_plan, dict) and external_plan.get("mode") == "tier1" else "plan.schema.json"
            validate_external_schema(args.root, external_plan, plan_schema, required=args.require_jsonschema)
            validate_plan_semantics(external_plan)
        if args.cycle_spec:
            external_cycle = load_json(args.cycle_spec)
            validate_external_schema(args.root, external_cycle, "cycle-spec.schema.json", required=args.require_jsonschema)
            validate_cycle_semantics(external_cycle, external_plan)
        if args.work_log:
            validate_work_log(args.work_log)
    except ValidationFailure as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        return 2
    print(json.dumps({"ok": True, **result}, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())

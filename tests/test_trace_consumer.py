import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("loop_flow_consumer", ROOT / "scripts" / "consume_trace.py")
CONSUMER = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(CONSUMER)


def event(**overrides):
    value = {
        "schema_version": "1.0",
        "event_id": "EVT-001",
        "event_kind": "unit_failed",
        "at": "2026-09-03T00:00:00Z",
        "actor": "worker:unit-1",
        "status": "failed",
        "unit_ref": "WU-001",
        "refs": ["plan:example", "spec:example:1"],
    }
    value.update(overrides)
    return value


class TraceConsumerTests(unittest.TestCase):
    def write_trace(self, directory: Path, events: list[dict]) -> Path:
        path = directory / "cycle.jsonl"
        path.write_text("".join(json.dumps(item, ensure_ascii=False) + "\n" for item in events), encoding="utf-8")
        return path

    def test_prompt_failure_produces_candidate(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            trace_path = self.write_trace(Path(directory), [event(root_cause_hint="prompt")])
            report = CONSUMER.consume_trace(trace_path, ROOT, require_jsonschema=True)
        self.assertEqual(report["status"], "pass")
        self.assertEqual(report["candidate_count"], 1)
        candidate = report["candidates"][0]
        self.assertEqual(candidate["root_cause_class"], "prompt")
        self.assertEqual(candidate["proposal_type"], "prompt_change")
        schema = json.loads((ROOT / "schemas" / "optimization-candidate.schema.json").read_text(encoding="utf-8"))
        Draft202012Validator(schema).validate(candidate)

    def test_capability_failure_preserves_selection_facts(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            trace_path = self.write_trace(Path(directory), [event(
                root_cause_hint="capability_mismatch",
                capability_requirements=["filesystem_write"],
                capability_source="host_reported",
                expected_model_tier="economy",
                actual_model_id="provider/model",
                attempts=2,
            )])
            report = CONSUMER.consume_trace(trace_path, ROOT, require_jsonschema=True)
        candidate = report["candidates"][0]
        self.assertEqual(candidate["proposal_type"], "model_upgrade")
        self.assertEqual(candidate["expected_model_tier"], "economy")
        self.assertEqual(candidate["actual_model_id"], "provider/model")
        self.assertEqual(candidate["capability_requirements"], ["filesystem_write"])

    def test_missing_root_cause_is_not_inferred(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            trace_path = self.write_trace(Path(directory), [event()])
            report = CONSUMER.consume_trace(trace_path, ROOT, require_jsonschema=True)
        self.assertEqual(report["status"], "revise")
        self.assertEqual(report["candidate_count"], 0)
        self.assertTrue(any("no actionable root_cause_hint" in item for item in report["unresolved"]))

    def test_invalid_event_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            trace_path = self.write_trace(Path(directory), [event(refs="invalid")])
            report = CONSUMER.consume_trace(trace_path, ROOT, require_jsonschema=True)
        self.assertEqual(report["status"], "revise")
        self.assertEqual(report["event_count"], 0)
        self.assertTrue(report["unresolved"])

    def test_unknown_event_kind_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            trace_path = self.write_trace(Path(directory), [event(event_kind="invented_event")])
            report = CONSUMER.consume_trace(trace_path, ROOT, require_jsonschema=False)
        self.assertEqual(report["status"], "revise")
        self.assertEqual(report["event_count"], 0)


if __name__ == "__main__":
    unittest.main()

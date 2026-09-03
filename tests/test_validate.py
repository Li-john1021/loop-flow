import copy
import importlib.util
import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("loop_flow_validate", ROOT / "scripts" / "validate.py")
VALIDATOR = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(VALIDATOR)


def load_example(name: str) -> dict:
    return json.loads((ROOT / "examples" / name).read_text(encoding="utf-8"))


class ValidateTests(unittest.TestCase):
    def test_bundle_and_command_manifest(self) -> None:
        result = VALIDATOR.validate_bundle(ROOT, require_jsonschema=True)
        self.assertEqual(result["commands"], ["plan", "annotate", "ready", "approve", "spec", "run", "status", "validate", "resume", "retro", "cancel"])
        manifest = json.loads((ROOT / "commands" / "manifest.json").read_text(encoding="utf-8"))
        retro = next(item for item in manifest["commands"] if item["id"] == "retro")
        self.assertEqual(retro["gate"], "explicit_user_invocation_after_cycle")
        self.assertEqual(retro["consumer_model_tier"], "frontier")

    def test_fake_approved_fingerprint_is_rejected(self) -> None:
        plan = load_example("full-plan.example.json")
        plan["status"] = "approved"
        plan["approval"] = {
            "status": "approved",
            "approved_by": "test",
            "approved_at": "2026-09-03T00:00:00Z",
            "approved_plan_fingerprint": "sha256:" + "0" * 64,
        }
        with self.assertRaisesRegex(VALIDATOR.ValidationFailure, "approved plan fingerprint mismatch"):
            VALIDATOR.validate_plan_semantics(plan)

    def test_open_required_annotation_blocks_approval(self) -> None:
        plan = load_example("tier1-plan.example.json")
        annotation = load_example("plan-annotation.example.json")
        annotation["plan_ref"] = plan["plan_id"]
        annotation["plan_version"] = plan["plan_version"]
        plan["annotations"] = [annotation]
        plan["approval_status"] = "approved"
        with self.assertRaisesRegex(VALIDATOR.ValidationFailure, "unresolved required annotations"):
            VALIDATOR.validate_plan_semantics(plan)

    def test_stale_spec_is_rejected(self) -> None:
        plan = load_example("full-plan.example.json")
        current_plan = copy.deepcopy(plan)
        current_plan["plan_version"] += 1
        cycle = load_example("cycle-spec.example.json")
        with self.assertRaisesRegex(VALIDATOR.ValidationFailure, "cycle spec is stale"):
            VALIDATOR.validate_cycle_semantics(cycle, current_plan)

    def test_dependency_cycle_is_rejected(self) -> None:
        plan = load_example("full-plan.example.json")
        cycle = load_example("cycle-spec.example.json")
        cycle["units"][0]["depends_on"] = ["WU-002"]
        cycle["units"][1]["depends_on"] = ["WU-001"]
        with self.assertRaisesRegex(VALIDATOR.ValidationFailure, "dependency cycle"):
            VALIDATOR.validate_cycle_semantics(cycle, plan)

    def test_high_numbered_cycle_ids_are_supported(self) -> None:
        plan = load_example("full-plan.example.json")
        cycle = load_example("cycle-spec.example.json")
        cycle["requirements"][0]["id"] = "REQ-1000"
        cycle["requirements"][0]["source_refs"] = ["REQ-001"]
        cycle["acceptance"][0]["proves"] = ["REQ-1000"]
        cycle["units"][0]["id"] = "WU-1000"
        cycle["units"][0]["requirement_refs"] = ["REQ-1000"]
        cycle["units"][1]["depends_on"] = ["WU-1000"]
        schema = json.loads((ROOT / "schemas" / "cycle-spec.schema.json").read_text(encoding="utf-8"))
        Draft202012Validator(schema).validate(cycle)
        VALIDATOR.validate_cycle_semantics(cycle, plan)


if __name__ == "__main__":
    unittest.main()

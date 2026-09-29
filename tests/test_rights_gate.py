import json
import unittest
from pathlib import Path

from rights_gate import evaluate, validate_registry


FIXTURE = Path(__file__).resolve().parents[1] / "examples" / "sources.json"


class RightsGateTests(unittest.TestCase):
    def setUp(self):
        self.sources = validate_registry(json.loads(FIXTURE.read_text(encoding="utf-8")))

    def test_internal_metadata_allowed(self):
        result = evaluate(self.sources[0], "internal", "metadata")
        self.assertTrue(result["allowed"])

    def test_internal_review_does_not_allow_public_use(self):
        result = evaluate(self.sources[0], "public", "public")
        self.assertFalse(result["allowed"])
        self.assertIn("public_review_required", result["reasons"])

    def test_public_approval_still_respects_individual_permissions(self):
        self.assertTrue(evaluate(self.sources[1], "public", "public")["allowed"])
        self.assertFalse(evaluate(self.sources[1], "public", "fulltext")["allowed"])

    def test_pending_source_fails_closed(self):
        self.assertFalse(evaluate(self.sources[2], "internal", "metadata")["allowed"])

    def test_duplicate_ids_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicate source id"):
            validate_registry({"sources": [self.sources[0], self.sources[0]]})

    def test_inconsistent_fulltext_rights_rejected(self):
        source = json.loads(json.dumps(self.sources[0]))
        source["rights"]["store_fulltext"] = True
        with self.assertRaisesRegex(ValueError, "storing fulltext"):
            validate_registry({"sources": [source]})


if __name__ == "__main__":
    unittest.main()

import json
import tempfile
import unittest
from pathlib import Path

from paper_recommender.domain import Paper, classify_paper, load_interest_profile


class InterestProfileTests(unittest.TestCase):
    def test_load_interest_profile_from_json(self):
        profile = self._write_profile(
            {
                "name": "Quantum Systems",
                "core_categories": ["quant-ph"],
                "expansion_categories": ["cs.LG"],
                "sections": [
                    {
                        "id": "quantum_control",
                        "label": "Quantum Control",
                        "weight": 5.0,
                        "keywords": ["quantum control", "pulse optimization"],
                    }
                ],
                "negative_rules": [
                    {
                        "id": "software-noise",
                        "penalty": 4.0,
                        "keywords": ["web framework"],
                    }
                ],
            }
        )

        self.assertEqual(profile.name, "Quantum Systems")
        self.assertEqual(profile.sections[0].id, "quantum_control")
        self.assertEqual(profile.sections[0].label, "Quantum Control")

    def test_custom_profile_drives_classification_without_code_changes(self):
        profile = self._write_profile(
            {
                "name": "Quantum Systems",
                "core_categories": ["quant-ph"],
                "expansion_categories": ["cs.LG"],
                "sections": [
                    {
                        "id": "quantum_control",
                        "label": "Quantum Control",
                        "weight": 5.0,
                        "keywords": ["quantum control", "pulse optimization"],
                    }
                ],
                "negative_rules": [],
            }
        )
        paper = Paper(
            paper_id="quantum-1",
            title="Learning Pulse Optimization for Quantum Control",
            abstract="A reinforcement learning method for quantum control.",
            authors=["Q. Researcher"],
            categories=["cs.LG"],
        )

        result = classify_paper(paper, profile=profile)

        self.assertTrue(result.accepted)
        self.assertEqual(result.sections, ("quantum_control",))

    def _write_profile(self, payload):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "interests.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            return load_interest_profile(path)


if __name__ == "__main__":
    unittest.main()


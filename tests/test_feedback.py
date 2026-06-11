import json
import tempfile
import unittest
from pathlib import Path

from paper_recommender.feedback import (
    FeedbackEvent,
    feedback_events_from_records,
    load_feedback_json,
    section_feedback_weights,
)


class FeedbackTests(unittest.TestCase):
    def test_feedback_events_from_records_normalizes_valid_rows(self):
        events = feedback_events_from_records(
            [
                {
                    "paper_id": "p1",
                    "rating": "like",
                    "section": "agentic_architecture",
                    "source": "email",
                },
                {"paper_id": "p2", "rating": "skip", "section": "noise"},
            ]
        )

        self.assertEqual(
            events,
            [
                FeedbackEvent(
                    paper_id="p1",
                    rating="like",
                    section="agentic_architecture",
                    source="email",
                )
            ],
        )

    def test_section_feedback_weights_counts_likes_and_dislikes(self):
        weights = section_feedback_weights(
            [
                FeedbackEvent("p1", "like", "agentic_architecture", "page"),
                FeedbackEvent("p2", "like", "agentic_architecture", "email"),
                FeedbackEvent("p3", "dislike", "hpc_cross_over", "page"),
            ]
        )

        self.assertEqual(weights["agentic_architecture"], 2.0)
        self.assertEqual(weights["hpc_cross_over"], -1.0)

    def test_load_feedback_json_reads_supabase_export(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "feedback.json"
            path.write_text(
                json.dumps([{"paper_id": "p1", "rating": "dislike", "section": "hpc_cross_over"}]),
                encoding="utf-8",
            )

            events = load_feedback_json(path)

        self.assertEqual(events[0].paper_id, "p1")
        self.assertEqual(events[0].rating, "dislike")


if __name__ == "__main__":
    unittest.main()


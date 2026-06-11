import unittest

from paper_recommender.email_delivery import build_email_message


class EmailDeliveryTests(unittest.TestCase):
    def test_build_email_message_sets_headers_and_html_body(self):
        message = build_email_message(
            subject="Daily Recommendations",
            sender="sender@example.com",
            receiver="receiver@example.com",
            html="<h1>Hello</h1>",
        )

        self.assertEqual(message["Subject"], "Daily Recommendations")
        self.assertEqual(message["From"], "sender@example.com")
        self.assertEqual(message["To"], "receiver@example.com")
        self.assertEqual(message.get_content_type(), "text/html")
        self.assertIn("<h1>Hello</h1>", message.get_content())


if __name__ == "__main__":
    unittest.main()


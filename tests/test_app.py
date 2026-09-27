import json
import os
import unittest
from io import BytesIO
from unittest.mock import patch
from urllib.error import HTTPError

from frontend.backend.app import GeminiAPIError, app


class TouristGuideTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    @patch("frontend.backend.app._photo_for_place", return_value=None)
    def test_homepage_shows_curated_places(self, _photo_lookup):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Taj Mahal", response.data)
        self.assertIn(b"Jaipur", response.data)

    @patch(
        "frontend.backend.app._photo_for_place",
        return_value={
            "url": "https://upload.wikimedia.org/taj-mahal.jpg",
            "source_url": "https://commons.wikimedia.org/wiki/File:Taj_Mahal.jpg",
            "title": "Taj Mahal.jpg",
            "artist": "Example Photographer",
            "license": "CC BY-SA 4.0",
        },
    )
    def test_photo_is_shown_with_attribution(self, _photo_lookup):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"upload.wikimedia.org/taj-mahal.jpg", response.data)
        self.assertIn(b"Example Photographer", response.data)
        self.assertIn(b"CC BY-SA 4.0", response.data)

    @patch("frontend.backend.app._photo_for_place", return_value=None)
    @patch("frontend.backend.app._search_gemini")
    def test_search_includes_every_ai_match_and_curated_match(self, search, _photo_lookup):
        search.return_value = [
            {
                "name": "Jaipur",
                "state": "Rajasthan",
                "description": "Pink City.",
                "attractions": ["Amer Fort"],
                "hotel": [],
                "food": [],
                "itinerary": {"day_1": [], "day_2": []},
            },
            {
                "name": "Amer Fort",
                "state": "Rajasthan",
                "description": "Historic hill fort.",
                "attractions": ["Palace"],
                "hotel": [],
                "food": [],
                "itinerary": {"day_1": [], "day_2": []},
            },
            {
                "name": "Hawa Mahal",
                "state": "Rajasthan",
                "description": "Palace of Winds.",
                "attractions": ["Facade"],
                "hotel": [],
                "food": [],
                "itinerary": {"day_1": [], "day_2": []},
            },
        ]

        response = self.client.get("/?search=Jaipur")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Amer Fort", response.data)
        self.assertIn(b"Hawa Mahal", response.data)
        self.assertEqual(search.call_count, 1)

    @patch("frontend.backend.app._photo_for_place", return_value=None)
    @patch("frontend.backend.app._search_gemini", side_effect=GeminiAPIError("AI service unavailable."))
    def test_search_surfaces_ai_error_and_keeps_local_matches(self, _search, _photo_lookup):
        response = self.client.get("/?search=Jaipur")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"AI service unavailable.", response.data)
        self.assertIn(b"Jaipur", response.data)

    @patch("frontend.backend.app._photo_for_place", return_value=None)
    @patch("frontend.backend.app._gemini_json")
    def test_generated_place_has_itinerary_and_travel_details(self, generate, _photo_lookup):
        generate.return_value = {
            "name": "Udaipur",
            "state": "Rajasthan",
            "description": "A lakeside city.",
            "history": "A historic city in Rajasthan.",
            "attractions": ["City Palace"],
            "hotel": ["Old City"],
            "food": ["Dal baati"],
            "best_time": "October to March.",
            "itinerary": {
                "day_1": [{"time": "Morning", "activity": "Visit City Palace."}],
                "day_2": [{"time": "Evening", "activity": "Walk by Lake Pichola."}],
            },
            "travel_tips": ["Check boat schedules."],
        }

        response = self.client.get("/place?name=Udaipur&state=Rajasthan")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Two-Day Travel Plan", response.data)
        self.assertIn(b"Visit City Palace.", response.data)
        self.assertIn(b"Check boat schedules.", response.data)

    @patch.dict(os.environ, {}, clear=True)
    @patch("frontend.backend.app._photo_for_place", return_value=None)
    def test_missing_key_is_explained_without_exposing_credentials(self, _photo_lookup):
        response = self.client.get("/?search=Udaipur")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Add GEMINI_API_KEY to the server environment.", response.data)
        self.assertNotIn(b"AQ.", response.data)

    @patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"})
    @patch("frontend.backend.app.urlopen")
    def test_gemini_key_is_sent_in_a_header_not_the_url(self, urlopen):
        class Response:
            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return False

            def read(self):
                return json.dumps({
                    "candidates": [{
                        "content": {"parts": [{"text": '{"places": []}'}]}
                    }]
                }).encode()

        urlopen.return_value = Response()
        from frontend.backend.app import _gemini_json

        self.assertEqual(_gemini_json("find places", {"type": "OBJECT"}), {"places": []})
        request = urlopen.call_args.args[0]
        self.assertNotIn("test-key", request.full_url)
        self.assertEqual(request.get_header("X-goog-api-key"), "test-key")

    @patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"})
    @patch("frontend.backend.app.urlopen")
    def test_gemini_http_errors_include_safe_provider_details(self, urlopen):
        urlopen.side_effect = HTTPError(
            "https://example.test",
            404,
            "Not Found",
            {},
            BytesIO(json.dumps({
                "error": {
                    "message": "Model not found; attempted key test-key"
                }
            }).encode()),
        )
        from frontend.backend.app import _gemini_json

        with self.assertRaisesRegex(GeminiAPIError, "Model not found") as raised:
            _gemini_json("find places", {"type": "OBJECT"})

        self.assertIn("[redacted]", str(raised.exception))
        self.assertNotIn("test-key", str(raised.exception))

    @patch("frontend.backend.app._photo_for_place", return_value=None)
    def test_detail_pages_include_itinerary(self, _photo_lookup):
        response = self.client.get("/place/1")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Two-Day Travel Plan", response.data)
        self.assertIn(b"Visit the Taj Mahal", response.data)

    def test_unknown_curated_place_returns_404(self):
        response = self.client.get("/place/9999")

        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()

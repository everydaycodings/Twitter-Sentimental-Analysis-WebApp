from io import BytesIO
import importlib.util
import unittest

from xquik_import import XquikImportError, build_twitter_dataframe, load_xquik_texts


class XquikImportTest(unittest.TestCase):
    def test_loads_csv_text_column(self):
        payload = BytesIO(b"Tweet Text,Tweet ID\nGreat update #AI,1\nNeeds work,2\n")

        self.assertEqual(load_xquik_texts(payload), ["Great update #AI", "Needs work"])

    def test_loads_nested_json_export(self):
        payload = BytesIO(
            b'{"data":[{"tweet":{"tweetText":"Hello @team"}},{"content":"Second"}]}'
        )

        self.assertEqual(load_xquik_texts(payload), ["Hello @team", "Second"])

    def test_loads_json_lines(self):
        payload = BytesIO(b'{"tweetText":"First"}\n{"text":"Second"}\n')

        self.assertEqual(load_xquik_texts(payload), ["First", "Second"])

    @unittest.skipIf(
        importlib.util.find_spec("pandas") is None
        or importlib.util.find_spec("textblob") is None,
        "dashboard dataframe dependencies are not installed",
    )
    def test_builds_dashboard_columns(self):
        data = build_twitter_dataframe(["Great update #AI https://example.com"])

        self.assertEqual(
            list(data.columns),
            [
                "Tweets",
                "mentions",
                "hastags",
                "links",
                "retweets",
                "Subjectivity",
                "Polarity",
                "Analysis",
            ],
        )
        self.assertEqual(data.loc[0, "hastags"], ["#AI"])

    def test_rejects_export_without_text(self):
        payload = BytesIO(b"id,url\n1,https://example.com\n")

        with self.assertRaises(XquikImportError):
            load_xquik_texts(payload)

    def test_rejects_non_utf8_export(self):
        payload = BytesIO(b"\xff\xfe")

        with self.assertRaisesRegex(XquikImportError, "UTF-8"):
            load_xquik_texts(payload)


if __name__ == "__main__":
    unittest.main()

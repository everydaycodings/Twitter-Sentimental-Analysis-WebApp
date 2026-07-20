import unittest
from unittest.mock import Mock, patch

import helper


class TwitterConnectionTest(unittest.TestCase):
    @patch.object(helper.tweepy, "API")
    @patch.object(helper.tweepy, "OAuthHandler")
    @patch.object(helper.configparser, "ConfigParser")
    def test_configures_access_token_secret(
        self,
        config_parser,
        oauth_handler,
        twitter_api,
    ):
        config = Mock()
        config.__getitem__ = Mock(
            return_value={
                "api_key": "api-key",
                "api_key_secret": "api-secret",
                "access_token": "access-token",
                "access_token_secret": "access-secret",
            }
        )
        config_parser.return_value = config
        auth = oauth_handler.return_value

        result = helper.twitter_connection()

        config.read.assert_called_once_with("config.ini")
        oauth_handler.assert_called_once_with("api-key", "api-secret")
        auth.set_access_token.assert_called_once_with("access-token", "access-secret")
        twitter_api.assert_called_once_with(auth)
        self.assertIs(result, twitter_api.return_value)


if __name__ == "__main__":
    unittest.main()

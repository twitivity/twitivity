import unittest
from unittest.mock import patch, MagicMock
from twitivity import Activity
import os

class TestActivityV2(unittest.TestCase):

    @patch.dict(os.environ, {
        "consumer_key": "test_ck",
        "consumer_secret": "test_cs",
        "access_token": "test_at",
        "access_token_secret": "test_ats",
    })
    @patch("requests.Session")
    def test_subscribe_v2(self, mock_session_cls):
        mock_response = MagicMock()
        mock_response.status_code = 204 # Twitter API often returns 204 for successful subscription

        mock_session_instance = MagicMock()
        mock_session_instance.request.return_value = mock_response
        mock_session_cls.return_value.__enter__.return_value = mock_session_instance

        activity = Activity()
        response = activity.subscribe()

        self.assertEqual(response.status_code, 204)
        mock_session_instance.request.assert_called_once_with(
            url="https://api.twitter.com/2/account_activity/subscriptions",
            method="POST",
            auth=unittest.mock.ANY, # Auth object is complex to match exactly here
            data=None
        )

    @patch.dict(os.environ, {
        "consumer_key": "test_ck",
        "consumer_secret": "test_cs",
        "access_token": "test_at",
        "access_token_secret": "test_ats",
    })
    @patch("requests.Session")
    def test_refresh_webhook_v2(self, mock_session_cls): # Renamed from test_remove_subscription
        mock_response = MagicMock()
        mock_response.status_code = 204 # PUT for refresh/CRC might return 204

        mock_session_instance = MagicMock()
        mock_session_instance.request.return_value = mock_response
        mock_session_cls.return_value.__enter__.return_value = mock_session_instance

        activity = Activity()
        webhook_id = "1234567890"
        response = activity.refresh(webhook_id=webhook_id)

        self.assertEqual(response.status_code, 204)
        mock_session_instance.request.assert_called_once_with(
            url=f"https://api.twitter.com/2/webhooks/{webhook_id}",
            method="PUT",
            auth=unittest.mock.ANY,
            data=None
        )

    @patch.dict(os.environ, {
        "consumer_key": "test_ck",
        "consumer_secret": "test_cs",
        "access_token": "test_at",
        "access_token_secret": "test_ats",
    })
    @patch("requests.Session")
    def test_register_webhook_v2(self, mock_session_cls):
        mock_json_response = {"webhook_id": "123", "url": "https://example.com/webhook", "valid": True}
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_json_response

        mock_session_instance = MagicMock()
        mock_session_instance.request.return_value = mock_response
        mock_session_cls.return_value.__enter__.return_value = mock_session_instance

        activity = Activity()
        callback_url = "https://example.com/webhook"
        response_json = activity.register_webhook(callback_url=callback_url)

        self.assertEqual(response_json, mock_json_response)
        mock_session_instance.request.assert_called_once_with(
            url="https://api.twitter.com/2/webhooks",
            method="POST",
            auth=unittest.mock.ANY,
            data={"url": callback_url}
        )

    @patch.dict(os.environ, {
        "consumer_key": "test_ck",
        "consumer_secret": "test_cs",
        "access_token": "test_at",
        "access_token_secret": "test_ats",
    })
    @patch("requests.Session")
    def test_delete_webhook_v2(self, mock_session_cls):
        mock_response = MagicMock()
        mock_response.status_code = 204 # Successful deletion often returns 204

        mock_session_instance = MagicMock()
        mock_session_instance.request.return_value = mock_response
        mock_session_cls.return_value.__enter__.return_value = mock_session_instance

        activity = Activity()
        webhook_id = "1234567890"
        response = activity.delete(webhook_id=webhook_id)

        self.assertEqual(response.status_code, 204)
        mock_session_instance.request.assert_called_once_with(
            url=f"https://api.twitter.com/2/webhooks/{webhook_id}",
            method="DELETE",
            auth=unittest.mock.ANY,
            data=None
        )

    @patch.dict(os.environ, {
        "consumer_key": "test_ck",
        "consumer_secret": "test_cs",
        "access_token": "test_at",
        "access_token_secret": "test_ats",
    })
    @patch("requests.Session")
    def test_list_webhooks_v2(self, mock_session_cls):
        mock_json_response = [{"id": "123", "url": "https://example.com/webhook", "valid": True}]
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_json_response

        mock_session_instance = MagicMock()
        mock_session_instance.request.return_value = mock_response
        mock_session_cls.return_value.__enter__.return_value = mock_session_instance

        activity = Activity()
        response_json = activity.webhooks() # Corresponds to the 'webhooks' (list) method

        self.assertEqual(response_json, mock_json_response)
        mock_session_instance.request.assert_called_once_with(
            url="https://api.twitter.com/2/webhooks",
            method="GET",
            auth=unittest.mock.ANY,
            data=None
        )

    @patch.dict(os.environ, {
        "consumer_key": "test_ck",
        "consumer_secret": "test_cs",
        "access_token": "test_at",
        "access_token_secret": "test_ats",
        "TWITTER_BEARER_TOKEN": "dummy_bearer_token"
    })
    @patch("requests.Session")
    def test_get_subscription_count_v2(self, mock_session_cls):
        mock_json_response = {"count": 10, "timestamp": "..."}
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_json_response

        mock_session_instance = MagicMock()
        mock_session_instance.request.return_value = mock_response
        mock_session_cls.return_value.__enter__.return_value = mock_session_instance

        activity = Activity()
        response_json = activity.get_subscription_count()

        self.assertEqual(response_json, mock_json_response)
        mock_session_instance.request.assert_called_once_with(
            url="https://api.twitter.com/2/account_activity/subscriptions/count",
            method="GET",
            headers={"Authorization": "Bearer dummy_bearer_token"},
            auth=None,
            data=None
        )

    @patch.dict(os.environ, {
        "consumer_key": "test_ck",
        "consumer_secret": "test_cs",
        "access_token": "test_at",
        "access_token_secret": "test_ats",
    })
    @patch("requests.Session")
    def test_check_user_subscription_v2(self, mock_session_cls): # Renamed as per prompt, was list_webhook_subscriptions
        mock_json_response = [{"user_id": "123"}] # Example response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_json_response

        mock_session_instance = MagicMock()
        mock_session_instance.request.return_value = mock_response
        mock_session_cls.return_value.__enter__.return_value = mock_session_instance

        activity = Activity()
        webhook_id = "123"
        response_json = activity.check_user_subscription(webhook_id=webhook_id)

        self.assertEqual(response_json, mock_json_response)
        mock_session_instance.request.assert_called_once_with(
            url=f"https://api.twitter.com/2/account_activity/webhooks/{webhook_id}/subscriptions",
            method="GET",
            auth=unittest.mock.ANY, # User context auth
            headers=None,
            data=None
        )

    @patch.dict(os.environ, {
        "consumer_key": "test_ck",
        "consumer_secret": "test_cs",
        "access_token": "test_at",
        "access_token_secret": "test_ats",
        "TWITTER_BEARER_TOKEN": "dummy_bearer_token"
    })
    @patch("requests.Session")
    def test_list_subscribed_users_v2(self, mock_session_cls):
        mock_json_response = {"users": ["user1", "user2"]}
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_json_response

        mock_session_instance = MagicMock()
        mock_session_instance.request.return_value = mock_response
        mock_session_cls.return_value.__enter__.return_value = mock_session_instance

        activity = Activity()
        webhook_id = "123"
        response_json = activity.list_subscribed_users(webhook_id=webhook_id)

        self.assertEqual(response_json, mock_json_response)
        mock_session_instance.request.assert_called_once_with(
            url=f"https://api.twitter.com/2/account_activity/webhooks/{webhook_id}/subscriptions/list",
            method="GET",
            headers={"Authorization": "Bearer dummy_bearer_token"},
            auth=None,
            data=None
        )

    @patch.dict(os.environ, {
        "consumer_key": "test_ck",
        "consumer_secret": "test_cs",
        "access_token": "test_at",
        "access_token_secret": "test_ats",
        "TWITTER_BEARER_TOKEN": "dummy_bearer_token"
    })
    @patch("requests.Session")
    def test_delete_user_subscription_v2(self, mock_session_cls):
        mock_response = MagicMock()
        mock_response.status_code = 204 # No content for successful deletion

        mock_session_instance = MagicMock()
        mock_session_instance.request.return_value = mock_response
        mock_session_cls.return_value.__enter__.return_value = mock_session_instance

        activity = Activity()
        webhook_id = "123"
        user_id = "456"
        response = activity.delete_user_subscription(webhook_id=webhook_id, user_id=user_id)

        self.assertEqual(response.status_code, 204)
        mock_session_instance.request.assert_called_once_with(
            url=f"https://api.twitter.com/2/account_activity/webhooks/{webhook_id}/users/{user_id}/subscriptions",
            method="DELETE",
            headers={"Authorization": "Bearer dummy_bearer_token"},
            auth=None,
            data=None
        )

    @patch.dict(os.environ, {
        "consumer_key": "test_ck",
        "consumer_secret": "test_cs",
        "access_token": "test_at",
        "access_token_secret": "test_ats",
        "TWITTER_BEARER_TOKEN": "dummy_bearer_token"
    })
    @patch("requests.Session")
    def test_request_activity_replay_v2(self, mock_session_cls):
        mock_json_response = {"status": "replay_initiated"}
        mock_response = MagicMock()
        mock_response.status_code = 200 # Assuming 200 for accepted replay request
        mock_response.json.return_value = mock_json_response

        mock_session_instance = MagicMock()
        mock_session_instance.request.return_value = mock_response
        mock_session_cls.return_value.__enter__.return_value = mock_session_instance

        activity = Activity()
        webhook_id = "123"
        from_date = "202301010000"
        to_date = "202301012359"
        response_json = activity.request_activity_replay(webhook_id=webhook_id, from_date=from_date, to_date=to_date)

        self.assertEqual(response_json, mock_json_response)
        mock_session_instance.request.assert_called_once_with(
            url=f"https://api.twitter.com/2/account_activity/replay/webhooks/{webhook_id}/subscriptions",
            method="POST",
            data={"from_date": from_date, "to_date": to_date},
            headers={"Authorization": "Bearer dummy_bearer_token"},
            auth=None
        )

if __name__ == "__main__":
    unittest.main()

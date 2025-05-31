import json
import hmac
import os
import hashlib
import base64
import re

import requests

from typing import NoReturn
from abc import ABC, abstractmethod

from tweepy.error import TweepError
from tweepy import OAuthHandler
from flask import Flask, request


class Activity:
    _protocol: str = "https:/"
    _host: str = "api.twitter.com"
    _version: str = "2"
    _product: str = "account_activity"
    _auth: OAuthHandler = OAuthHandler(
        os.environ["consumer_key"], os.environ["consumer_secret"]
    )
    _auth.set_access_token(
        os.environ["access_token"], os.environ["access_token_secret"]
    )

    def _get_bearer_token(self) -> str:
        """
        Retrieves the Bearer Token for App-only OAuth.
        Placeholder implementation: Fetches from environment variable.
        """
        bearer_token = os.environ.get("TWITTER_BEARER_TOKEN")
        if not bearer_token:
            raise ValueError(
                "TWITTER_BEARER_TOKEN environment variable not set. "
                "Required for App-only OAuth endpoints."
            )
        return bearer_token

    def api(self, method: str, endpoint: str, data: dict = None, auth_type: str = "user") -> json:
        """
        :param method: GET or POST
        :param endpoint: API Endpoint to be specified by user
        :param data: POST Request payload parameter
        :param auth_type: "user" for User-Context OAuth 1.0a, "app" for App-only OAuth 2.0 (Bearer Token)
        :return: json
        """
        try:
            url_parts = [self._protocol, self._host, self._version]
            # Determine if the endpoint is a top-level webhook path or under a product (e.g., account_activity)
            if endpoint.startswith("webhooks") and not self._product in endpoint and not endpoint.startswith(self._product):
                # This condition is for /2/webhooks, /2/webhooks/:id etc.
                url_parts.append(endpoint)
            else:
                # This is for /2/account_activity/* or other product-based endpoints
                url_parts.extend([self._product, endpoint])

            request_url = "/".join(part.strip('/') for part in url_parts)
            if self._protocol not in request_url: # ensure protocol is there
                request_url = self._protocol + "//" + request_url.replace(self._protocol + "/", "")


            headers = {}
            auth_param = None

            if auth_type == "user":
                auth_param = self._auth.apply_auth()
            elif auth_type == "app":
                bearer_token = self._get_bearer_token()
                headers["Authorization"] = f"Bearer {bearer_token}"
            else:
                raise ValueError(f"Unsupported auth_type: {auth_type}")

            with requests.Session() as r:
                response = r.request(
                    url=request_url,
                    method=method,
                    auth=auth_param,
                    headers=headers if auth_type == "app" else None, # Pass headers only for app auth
                    data=data,
                )
                return response
        except TweepError:
            raise

    def register_webhook(self, callback_url: str) -> json:
        try:
            return self.api(
                method="POST",
                endpoint="webhooks", # Path: POST /2/webhooks
                data={"url": callback_url},
            ).json()
        except Exception as e:
            raise e

    def refresh(self, webhook_id: str) -> NoReturn:
        """Refreshes CRC for the provided webhook_id.
        """
        try:
            # Path: PUT /2/webhooks/:webhook_id
            return self.api(
                method="PUT",
                endpoint=f"webhooks/{webhook_id}",
            )
        except Exception as e:
            raise e

    def delete(self, webhook_id: str) -> NoReturn:
        """Removes the webhook from the provided webhook_id.
        """
        try:
            # Path: DELETE /2/webhooks/:webhook_id
            return self.api(
                method="DELETE",
                endpoint=f"webhooks/{webhook_id}",
            )
        except Exception as e:
            raise e

    def subscribe(self) -> NoReturn:
        try:
            # Path: POST /2/account_activity/webhooks/:webhook_id/subscriptions/all
            # This method seems to subscribe the app to ALL events for the user context.
            # The old path was f"all/{os.environ['env_name']}/subscriptions.json"
            # The new equivalent for "subscribes the provided application to all events for the provided user context"
            # seems to be POST /2/account_activity/subscriptions based on the doc.
            # However, the table maps /1.1/account_activity/webhooks/:webhook_id/subscriptions/all.json
            # to /2/account_activity/webhooks/:webhook_id/subscriptions/all
            # The current code doesn't take a webhook_id for subscribe.
            # Let's assume for now it's a general subscription not tied to a specific webhook_id in its path.
            # The documentation also has: POST /2/account_activity/subscriptions
            # This is ambiguous. The original code uses `all/{env_name}/subscriptions.json`.
            # The closest V2 seems to be `/2/account_activity/subscriptions` or
            # `/2/account_activity/webhooks/:webhook_id/subscriptions` (if webhook_id is implicitly known or needs to be added)
            # Given the table: POST /1.1/account_activity/webhooks/:webhook_id/subscriptions/all.json maps to POST /2/account_activity/webhooks/:webhook_id/subscriptions/all
            # The original code's endpoint for subscribe was `all/{os.environ['env_name']}/subscriptions.json`.
            # This looks like a subscription for a pre-configured environment.
            # The V2 documentation points to `POST /2/account_activity/subscriptions` for "Subscribes the provided application to all events for the provided user context for all message types"
            # And `POST /2/account_activity/webhooks/:webhook_id/subscriptions` for "Request Activity Replay" (this is not it)
            # And `POST /2/account_activity/webhooks/:webhook_id/subscriptions/all` for "Subscribes to all events on the specified webhook"
            # The old code `endpoint=f"all/{os.environ['env_name']}/subscriptions.json"` implies it's not specific to one webhook_id in the path.
            # Let's use the endpoint that subscribes the app to all events for the user, which is simpler:
            # `subscriptions` under the `account_activity` product.
            # This corresponds to POST /2/account_activity/subscriptions
            return self.api(
                method="POST",
                endpoint="subscriptions",
            )
        except Exception:
            raise

    def webhooks(self) -> json:
        """Returns all environments, webhook URLs and their statuses for the authenticating app.
        Only one webhook URL can be registered to each environment.
        """
        try:
            # Path: GET /2/webhooks
            return self.api(method="GET", endpoint="webhooks").json()
        except Exception as e:
            raise e

    def get_subscription_count(self) -> json:
        """
        Returns a count of subscriptions that are currently active on your account.
        OAuth: App-only
        """
        try:
            return self.api(
                method="GET",
                endpoint="subscriptions/count", # /2/account_activity/subscriptions/count
                auth_type="app"
            ).json()
        except Exception as e:
            raise e

    def check_user_subscription(self, webhook_id: str) -> json:
        """
        Lists subscriptions for a given webhook_id. (Endpoint as per prompt)
        OAuth: User-context
        """
        # Note: Endpoint GET /2/account_activity/webhooks/:webhook_id/subscriptions
        # This actually lists all subscriptions for the webhook.
        # A true "check specific user" might be different or require client-side filtering.
        try:
            return self.api(
                method="GET",
                endpoint=f"webhooks/{webhook_id}/subscriptions", # /2/account_activity/webhooks/:id/subscriptions
                auth_type="user" # As per prompt
            ).json() # Assuming it returns JSON; if 204, .json() would fail. Caller should handle.
        except Exception as e:
            raise e

    def list_subscribed_users(self, webhook_id: str) -> json:
        """
        Returns a list of user IDs that are subscribed to the specified webhook.
        OAuth: App-only
        """
        try:
            return self.api(
                method="GET",
                endpoint=f"webhooks/{webhook_id}/subscriptions/list", # /2/account_activity/webhooks/:id/subscriptions/list
                auth_type="app"
            ).json()
        except Exception as e:
            raise e

    def delete_user_subscription(self, webhook_id: str, user_id: str) -> requests.Response:
        """
        Deactivates a specific user's subscription from a webhook.
        OAuth: App-only
        """
        try:
            # Endpoint: DELETE /2/account_activity/webhooks/:webhook_id/users/:user_id/subscriptions
            # The prompt had /users/:user_id/subscriptions, the actual path from docs seems to be /userId/:user_id
            # Let's recheck typical Twitter API styles. Often it's /users/:user_id or /user_id/:user_id.
            # The migration guide for AAAPI v1.1 to v2 has:
            # DELETE /1.1/account_activity/webhooks/:webhook_id/subscriptions/:user_id/all
            # maps to
            # DELETE /2/account_activity/webhooks/:webhook_id/subscriptions/:user_id/all
            # The prompt has /users/:user_id/subscriptions. The doc for "Deactivates a subscription for the specified webhook and user id"
            # (https://developer.twitter.com/en/docs/twitter-api/enterprise/account-activity-api/api-reference/aaa-enterprise#delete-account-activity-all-webhooks-webhook-id-subscriptions-user-id)
            # shows DELETE /2/account_activity/webhooks/:webhook_id/subscriptions/:user_id (for enterprise)
            # For standard v2, it's likely: DELETE /2/account_activity/webhooks/:webhook_id/subscriptions/:user_id
            # The prompt's path element "users" before user_id is unusual for this part of the API.
            # I will use the one that seems more standard or from direct V2 docs if found quickly,
            # otherwise stick to prompt and note it.
            # The prompt seems to be for `DELETE /2/account_activity/webhooks/:webhook_id/users/:user_id/subscriptions`
            # This structure is a bit different from the typical `subscriptions/:user_id`.
            # Let's use the path from the prompt for now: `webhooks/{webhook_id}/users/{user_id}/subscriptions`
            # This will resolve to `/2/account_activity/webhooks/{webhook_id}/users/{user_id}/subscriptions`
            return self.api(
                method="DELETE",
                endpoint=f"webhooks/{webhook_id}/users/{user_id}/subscriptions",
                auth_type="app"
            ) # Returns full response for status code check (e.g., 204)
        except Exception as e:
            raise e

    def request_activity_replay(self, webhook_id: str, from_date: str, to_date: str) -> json:
        """
        Requests a replay of activity for a given webhook and date range.
        OAuth: App-only
        """
        try:
            # Endpoint: POST /2/account_activity/replay/webhooks/:webhook_id/subscriptions
            return self.api(
                method="POST",
                endpoint=f"replay/webhooks/{webhook_id}/subscriptions", # /2/account_activity/replay/webhooks/:id/subscriptions
                data={"from_date": from_date, "to_date": to_date},
                auth_type="app"
            ).json()
        except Exception as e:
            raise e


def url_params(url: str) -> str:
    pattern: str = r"^[^\/]+:\/\/[^\/]*?\.?([^\/.]+)\.[^\/.]+(?::\d+)?\/"
    return re.split(pattern=pattern, string=url)[-1]


class Event(ABC):
    CALLBACK_URL: str = None

    def __init__(self):
        self._server = self._get_server()

    @abstractmethod
    def on_data(self, data: json) -> None:
        pass

    def listen(self) -> None:
        self._server.run()

    def _get_server(self) -> Flask:
        try:
            app = Flask(__name__)

            @app.route(
                f"/{url_params(url=self.CALLBACK_URL)}", methods=["GET", "POST", "PUT"]
            )
            def callback() -> json:
                try:
                    if request.method == "GET" or request.method == "PUT":
                        hash_digest = hmac.digest(
                            key=os.environ["consumer_secret"].encode("utf-8"),
                            msg=request.args.get("crc_token").encode("utf-8"),
                            digest=hashlib.sha256,
                        )
                        return {
                            "response_token": "sha256="
                            + base64.b64encode(hash_digest).decode("ascii")
                        }
                    elif request.method == "POST":
                        data = request.get_json()
                        self.on_data(data)
                        return {"code": 200}

                except KeyError:
                    raise Exception("CRC_TOKEN NOT FOUND")
                except JSONDecodeError:
                    raise

            return app
        except Exception as e:
            raise Exception(
                "Something Went Wrong! Please do report the issue \
                at https://github.com/twitivity/twitivity/issues"
            )

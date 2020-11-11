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
    _version: str = "1.1"
    _product: str = "account_activity"
    _auth: OAuthHandler = OAuthHandler(
        os.environ["consumer_key"], os.environ["consumer_secret"]
    )
    _auth.set_access_token(
        os.environ["access_token"], os.environ["access_token_secret"]
    )

    def api(self, method: str, endpoint: str, data: dict = None) -> json:
        """
        :param method: GET or POST
        :param endpoint: API Endpoint to be specified by user
        :param data: POST Request payload parameter
        :return: json
        """
        try:
            with requests.Session() as r:
                response = r.request(
                    url="/".join(
                        [
                            self._protocol,
                            self._host,
                            self._version,
                            self._product,
                            endpoint,
                        ]
                    ),
                    method=method,
                    auth=self._auth.apply_auth(),
                    data=data,
                )
                return response
        except TweepError:
            raise

    def register_webhook(self, callback_url: str) -> json:
        try:
            return self.api(
                method="POST",
                endpoint=f"all/{os.environ['env_name']}/webhooks.json",
                data={"url": callback_url},
            ).json()
        except Exception as e:
            raise e

    def refresh(self, webhook_id: str) -> NoReturn:
        """Removes the webhook from the provided webhook_id.
        """
        try:
            return self.api(
                method="DELETE",
                endpoint=f"all/{os.environ['env_name']}/webhooks/{webhook_id}.json",
            )
        except Exception as e:
            raise e

    def subscribe(self) -> NoReturn:
        try:
            return self.api(
                method="POST",
                endpoint=f"all/{os.environ['env_name']}/subscriptions.json",
            )
        except Exception:
            raise

    def webhooks(self) -> json:
        """Returns all environments, webhook URLs and their statuses for the authenticating app. 
        Only one webhook URL can be registered to each environment.
        """
        try:
            return self.api(method="GET", endpoint=f"all/webhooks.json").json()
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

            return app
        except Exception:
            raise

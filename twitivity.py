import json
import hmac
import os
import hashlib
import base64

import requests

from abc import ABC, abstractmethod
from pprint import pprint

from tweepy.error import TweepError
from tweepy import OAuthHandler
from flask import Flask, request


class Activity:

    _protocol: str = "https://"
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
                    url=os.path.join(
                        self._protocol,
                        self._host,
                        self._version,
                        self._product,
                        endpoint,
                    ),
                    method=method,
                    auth=self._auth.apply_auth(),
                    data=data,
                )
                return response.json()
        except TweepError:
            raise

    def register_webhook(self, env: str, callback: str, method: str = "POST") -> json:
        try:
            return self.api(
                method=method,
                endpoint=f"all/{env}/webhooks.json",
                data={"url": callback},
            )
        except Exception:
            raise

    def subscribe(self, env: str, method: str = "POST") -> json:
        try:
            return self.api(method=method, endpoint=f"all/{env}/subscriptions.json")
        except Exception:
            raise


class Event(ABC):

    callback: str = None
    env: str = None

    def __init__(self):
        self.server = self._get_server()
        self._activity = Activity()

    @abstractmethod
    def on_data(self, data: dict) -> None:
        pass

    def _get_server(self) -> Flask:
        try:
            app = Flask(__name__)

            @app.route("/listener", methods=["GET", "POST"])
            def callback() -> json:
                if request.method == "GET":
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
                    data = request.get_json(force=True)
                    self.on_data(data)
                    return {"code": 200}

            return app
        except Exception:
            raise

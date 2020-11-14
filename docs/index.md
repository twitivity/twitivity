# Twitivity - Account Acitivity API

Twitivity does all the heavy lifting under the hood. So that you can focus on what's really important — building your app.

## Quick Start

Get the comprehensive guide to get started on the [README.md page](https://github.com/saadmanrafat/twitivity/blob/master/README.md)
 
## Deploying On Web Server

Here's a simple guide to deploy it in a web server.

```python
# app.py

import flask
import json
import hmac
import os
import hashlib
import base64
import logging
import flask

logging.basicConfig(
    filename="app.log",
    filemode="w",
    level=logging.INFO,
)

app = flask.Flask(__name__)

os.environ["consumer_secret"] = f"{consumer_secret}"


@app.route("/webhook/twitter", methods=["GET", "POST"])
def callback() -> json:
    if flask.request.method == "GET" or flask.request.method == "PUT":
        hash_digest = hmac.digest(
            key=os.environ["consumer_secret"].encode("utf-8"),
            msg=flask.request.args.get("crc_token").encode("utf-8"),
            digest=hashlib.sha256,
        )
        return {
            "response_token": "sha256="
            + base64.b64encode(hash_digest).decode("ascii")
        }
    elif flask.request.method == "POST":
        data = flask.request.get_json()
        logging.info(data)
        return {"code": 200}

```

Once the code running on the server. You can register and subscribe
to events from your local machine. 

```python
# activity.py

from pprint import pprint
from twitivity import Activity


if __name__ == '__main__':
    activity = Activity()
    pprint(activity.register_webhook(
        "https://domain.com/webhook/twitter"))
    pprint(activity.subscribe())

```

### How do you view account activies in real-time? 

From your server, execute the following command.

```
~$ tail -f app.log
```

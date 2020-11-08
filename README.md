# Twitivity
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/imgur-scraper) [![Downloads](https://pepy.tech/badge/twitivity)](https://pepy.tech/project/twitivity) ![PyPI - License](https://img.shields.io/pypi/l/imgur-scraper)

Twitter [Accounts Activity](https://developer.twitter.com/en/docs/accounts-and-users/subscribe-account-activity/overview) API Client Library for Python. 

![](demo.gif)

Account Activity API allows you to subscribe to user activities. Unlike Twitter's REST API or the Streaming API, the Account Activity API delivers data through webhook connections. Which makes it faster and allows it to deliver Twitter data to you in real-time. [You can subscribe to these user activities](https://developer.twitter.com/en/docs/accounts-and-users/subscribe-account-activity/overview).

## Prerequisits
* A reverse proxy or web server that will support public endpoints, or if developing locally a tool similar to [Ngrok](https://ngrok.com/).

## Installation

```
~$ pip3 install twitivity
```

## Getting Started

* [Apply for a Twitter Developer Account](https://developer.twitter.com/en/account/get-started)
* [Create an application](https://developer.twitter.com/en/apps) - Fill in the required fields, the callback URL is your domain name with an added endpoint, for example `https://yourdomain.com/listener`, note it must be HTTPS. If you are using Ngrok, this will be your `https://{randomid}.ngrok.io` address with a URI specified by you e.g. `https://{randomid}.ngrok.io/listener` or `https://{randomid}.ngrok.io/twitter/callback`. Twitter will later use this URL to send you account activity data. Make sure to enable "Read, Write and Direct messages" permission.
     * Make sure you save your API Key & Secret, and Access Token & Secret somewhere safe as part of this step. You do not need to generate a Bearer Token to use Twitivity.
* [Create a dev environment](https://developer.twitter.com/en/account/environments) and `setup a dev environment` for the Account Activity API. Name a dev environment label of your choosing and select your app.

The next step is to register your webhook URL. Twitter will send a `GET` request with Challenge-Response Check or CRC token to verify you are the owner of the app and the webhook URL. To validate, an encrypted response token based on your consumer key and the CRC token has to be sent back to Twitter. Upon successful validation, registration of the webhook URL and subscription. Twitter will send data to this endpoint (the webhook URL) as a `POST` request.

## Why Twitivity?

`Twitivity` does all the heavy lifting under the hood. All you have to do is to create an app and set up a dev environment. Run the application and concentrate on what's really important — building your app.  

* Performs challenge-response check validation;
* Registers webhook URL;
* Subscribes to current user's context; and,
* Receives Twitter Account Activity in real-time.

## Usage

[Ngrok](https://ngrok.com/) is a handy tool to try out the API locally, on your machine. Twitivity uses Flask under the hood, which uses TCP port 5000 to run, so you need to make sure you specify this so requests get correctly forwarded to your app.

```terminal
~$ ./ngrok http 5000
```

### Add Credentials as Environment Variables.

[`App`](https://developer.twitter.com/en/apps) :arrow_right: `Details` :arrow_right: `Keys and Tokens`

```
~$ export consumer_key=API_KEY
~$ export consumer_secret=API_SECRET_KEY
~$ export access_token=ACCESS_TOKEN
~$ export access_token_secret=ACCESS_TOKEN_SECRET
~$ export env_name=ENV_NAME # this is the dev environment label name you choose.
```

## Configuration

You need to run the 'Register & Subscribe' code in **parallel** with the 'Stream Events' code **once** before running the application (first [`stream_events.py`](/examples/stream_events.py) then [`configure.py`](/examples/configure.py). This will register the webhook URL and subscribe to the user's activities. For example:

```python
from multiprocessing import Process

def configure():
    # put configure.py here
    continue
    
def stream_events():
    # put stream_events.py here
    continue

if __name__ == '__main__':
    p1 = Process(target=stream_events)
    p1.start()
    p2 = Process(target=configure)
    p2.start()
    p1.join()
    p2.join()
```

### Register & Subscribe

To register the webhook URL and subscribe to activities, run both programs (`stream_events.py` & `configure.py`) in **parallel**.

```python3
# configure.py
>>> from twitivity import Activity

>>> account_activity = Activity()
>>> account_activity.register_webhook("https://youdomain.com/listener")
>>> account_activity.subscribe()
```

Response:
```
{
  'id': '1198870971131686912', # webhook id
  'url': 'https://yourdomain.com/listener',
  'valid': True,
  'created_timestamp': '2019-11-25 07:48:08 +0000'
}
```

### Stream Events

```python3
# stream_events.py

>>> from twitivity import Event
>>> import json

>>> class StreamEvent(Event):
     CALLBACK_URL: str = "https://yourdomain.com/listener"

     def on_data(self, data: json) -> None:
         # process data

>>> stream_events = StreamEvent()
>>> stream_events.listen()
```

## Common Problems

### I was using ngrok to test my app and everything was working, but when I start ngrok again nothing is working?

Twitter webhooks are immutable by design, if your webhook URL is changed, there is a possibility that your application consumer key and consumer secret have been compromised. By requiring you to create a new webhook configuration, you are also required to re-subscribe to your user’s events. 

Additional to this, in the event that a response is not posted within 3 seconds or becomes invalid, events will cease to be sent to the registered webhook.

#### How can I check if my webhook is still valid?

In your terminal you can run the following curl command:

```
curl --request GET --url https://api.twitter.com/1.1/account_activity/all/webhooks.json --header 'authorization: Bearer {Bearer Token}'
```

**Example JSON Response**

```
{"environments":[{"environment_name":"prod","webhooks":[{"id":"1312681837941059599","url":"https://twitterwebhook.ngrok.io/twitter/callback","valid":false,"created_timestamp":"2020-10-04 09:11:54 +0000"}]}]}% 
```

Once you know your webhook ID and it's validity, you can go about deleting it using the `account_activity/webhooks/:webhook_id` API endpoint which will remove the webhook from the provided application's configuration.

`How-to in progress`

The other option that worked if you don't want to deal with OAuth was deleting the whole application and starting again. :grimacing:.

## References
* [GET account_activity/webhooks](https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/subscribe-account-activity/api-reference/aaa-enterprise#get-account-activity-webhooks)
* [Subscribe to account activity](https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/subscribe-account-activity/guides/securing-webhooks)
* [DELETE account_activity/webhooks/:webhook_id](https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/subscribe-account-activity/api-reference/aaa-enterprise#delete-account-activity-webhooks-webhook-id)

# Twitivity
[![Premium](https://img.shields.io/endpoint?url=https%3A%2F%2Ftwbadges.glitch.me%2Fbadges%2Fpremium)](https://developer.twitter.com/)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/imgur-scraper) [![Downloads](https://pepy.tech/badge/twitivity)](https://pepy.tech/project/twitivity) ![PyPI - License](https://img.shields.io/pypi/l/twitivity)

Twitter [Accounts Activity](https://developer.twitter.com/en/docs/accounts-and-users/subscribe-account-activity/overview) API Client Library for Python. 

![](assets/demo.gif)

Account Activity API allows you to subscribe to user activities. Unlike Twitter's REST API or the Streaming API, the Account Activity API delivers data through webhook connections. Which makes it faster and allows it to deliver Twitter data to you in real-time. [You can subscribe to these user activities](https://developer.twitter.com/en/docs/accounts-and-users/subscribe-account-activity/overview).

## Getting Started

* [Apply for a Twitter Developer Account](https://developer.twitter.com/en/account/get-started)
* [Create an application](https://developer.twitter.com/en/apps), fill in the required fields, the callback URL is your domain name with an added endpoint, for example `https://yourdomain.com/listener`. Twitter will later use this URL to send you account activity data. Make sure to enable "Read, Write and Direct messages" permission.
* Navigate to the [Dev environment section](https://developer.twitter.com/en/account/environments) and `setup a dev environment` for the Account Activity API. Name a dev environment label of your choosing and select your app.

The next step is to register your webhook URL. Twitter will send a `GET` request with Challenge-Response Check or CRC token to verify you are the owner of the app and the webhook URL. To validate, an encrypted response token based on your consumer key and the CRC token has to be sent back to Twitter. Upon successful validation, registration of the webhook URL and subscription. Twitter will send data to this endpoint (the webhook URL) as a `POST` request.

## Why Twitivity?

`Twitivity` does all the heavy lifting under the hood. All you have to do is to create an app and set up a dev environment. Run the application and concentrate on what's really important — building your app.  

* Performs challenge-response check validation
* Registers webhook URL.
* Subscribes to current user's context
* Receives Twitter Account Activity in real-time

## Usage

[Ngrok](https://ngrok.com/) is a handy tool to try out the API locally, on your machine. Install and run ngrok and replace your app's URL and callback URL with the link ngrok provides. Make sure to use the one with `https`.

```terminal
~$ ./ngrok http 5000
```
### Stream events in real time.

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

## Configuration

The configuration below only has to be done once before running the application for the first time.


#### Store the credentials as environment variables.

[`App`](https://developer.twitter.com/en/apps) :arrow_right: `Details` :arrow_right: `Keys and Tokens`

```
~$ export consumer_key=API_KEY
~$ export consumer_secret=API_SECRET_KEY
~$ export access_token=ACCESS_TOKEN
~$ export access_token_secret=ACCESS_TOKEN_SECRET
~$ export env_name=ENV_NAME # this is the dev environment label name you choose.
```

#### Register & Subscribe

To register the webhook URL and subscribe to activities, run both programs in **parallel** 
(first `stream_events.py` then `configure.py`). This will register the webhook URL and subscribe to the user's activities.

```python3
# configure.py
>>> from twitivity import Activity

>>> account_activity = Activity()
>>> account_activity.register_webhook("https://youdomain.com/listener")
>>> account_activity.subscribe()

# Response
{
  'id': '1198870971131686912', # webhook id
  'url': 'https://yourdomain.com/listener',
  'valid': True,
  'created_timestamp': '2019-11-25 07:48:08 +0000'
}
```

## Installation

```
~$ pip3 install twitivity
```

## Deploying

[Documentation](https://repo.twitivity.dev/) on how to deploy it on web servers.


Supported Versions: **Python 3.6**, **Python 3.7** and **Python 3.8**


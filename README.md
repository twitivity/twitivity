# Twitivity
[![Premium](https://img.shields.io/endpoint?url=https%3A%2F%2Ftwbadges.glitch.me%2Fbadges%2Fpremium)](https://developer.twitter.com/)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/imgur-scraper) [![Downloads](https://pepy.tech/badge/twitivity)](https://pepy.tech/project/twitivity) ![PyPI - License](https://img.shields.io/pypi/l/twitivity)

**Twitivity now uses the X Account Activity API v2.**

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
~$ export TWITTER_BEARER_TOKEN=YOUR_BEARER_TOKEN # Required for App-Only OAuth methods
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

### Additional Account Activity API v2 Methods

The `Activity` class also provides methods to interact with other Account Activity API v2 endpoints.

#### `get_subscription_count()`
- **Description**: Returns a count of subscriptions that are currently active on your account.
- **API Endpoint**: `GET /2/account_activity/subscriptions/count`
- **OAuth Type**: App-Only (Bearer Token)
- **Usage**:
  ```python
  activity = Activity()
  try:
      count_data = activity.get_subscription_count()
      print(count_data)
  except Exception as e:
      print(f"Error getting subscription count: {e}")
  ```

#### `check_user_subscription(webhook_id: str)`
- **Description**: Lists subscriptions for a given webhook ID. *Note: This endpoint lists all subscriptions for the webhook; a true check for a specific user might require client-side filtering or a different endpoint if available.*
- **API Endpoint**: `GET /2/account_activity/webhooks/:webhook_id/subscriptions`
- **OAuth Type**: User-Context
- **Usage**:
  ```python
  activity = Activity()
  webhook_id = "your_webhook_id"
  try:
      subscription_data = activity.check_user_subscription(webhook_id)
      print(subscription_data)
  except Exception as e:
      print(f"Error checking user subscription: {e}")
  ```

#### `list_subscribed_users(webhook_id: str)`
- **Description**: Returns a list of user IDs that are subscribed to the specified webhook.
- **API Endpoint**: `GET /2/account_activity/webhooks/:webhook_id/subscriptions/list`
- **OAuth Type**: App-Only (Bearer Token)
- **Usage**:
  ```python
  activity = Activity()
  webhook_id = "your_webhook_id"
  try:
      subscribed_users = activity.list_subscribed_users(webhook_id)
      print(subscribed_users)
  except Exception as e:
      print(f"Error listing subscribed users: {e}")
  ```

#### `delete_user_subscription(webhook_id: str, user_id: str)`
- **Description**: Deactivates a specific user's subscription from a webhook.
- **API Endpoint**: `DELETE /2/account_activity/webhooks/:webhook_id/users/:user_id/subscriptions`
- **OAuth Type**: App-Only (Bearer Token)
- **Usage**:
  ```python
  activity = Activity()
  webhook_id = "your_webhook_id"
  user_id_to_delete = "user_id_to_unsubscribe"
  try:
      response = activity.delete_user_subscription(webhook_id, user_id_to_delete)
      if response.status_code == 204:
          print(f"Successfully deleted subscription for user {user_id_to_delete} from webhook {webhook_id}.")
      else:
          print(f"Error deleting subscription: {response.status_code} - {response.text}")
  except Exception as e:
      print(f"Error deleting user subscription: {e}")
  ```

#### `request_activity_replay(webhook_id: str, from_date: str, to_date: str)`
- **Description**: Requests a replay of activity (subscriptions) for a given webhook and date range. `from_date` and `to_date` should be in `YYYYMMDDHHmm` format.
- **API Endpoint**: `POST /2/account_activity/replay/webhooks/:webhook_id/subscriptions`
- **OAuth Type**: App-Only (Bearer Token)
- **Usage**:
  ```python
  activity = Activity()
  webhook_id = "your_webhook_id"
  from_date = "202301010000" # Example: January 1, 2023, 00:00
  to_date = "202301012359"   # Example: January 1, 2023, 23:59
  try:
      replay_status = activity.request_activity_replay(webhook_id, from_date, to_date)
      print(replay_status)
  except Exception as e:
      print(f"Error requesting activity replay: {e}")
  ```

## Installation

This project uses `uv` for dependency management. Package metadata and dependencies are defined in `pyproject.toml`.

To install the package and its dependencies:
```bash
uv pip install .
```

To install development dependencies:
```bash
uv pip install .[dev]
```

## Deploying

[Documentation](https://repo.twitivity.dev/) on how to deploy it on web servers.


Supported Versions: **Python 3.6**, **Python 3.7** and **Python 3.8**


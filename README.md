# Twitivity 
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/imgur-scraper) ![PyPI - License](https://img.shields.io/pypi/l/imgur-scraper)
### Twitter [Accounts Activity](https://developer.twitter.com/en/docs/accounts-and-users/subscribe-account-activity/overview) API Client Library for Python

![Photo by Ingo Joseph from Pexels](assets/twitivity-banner.jpg)


## Usage
Create an [app](https://developer.twitter.com/en/apps) then assign [dev environment label](https://developer.twitter.com/en/account/environments) for the app.

[App](https://developer.twitter.com/en/apps) :arrow_right: Details :arrow_right: Keys and Tokens
 
Add the credentials as environment variables
 
```
~$ export consumer_key=API_KEY
~$ export consumer_secret=API_SECRET_KEY
~$ export access_token=ACCESS_TOKEN
~$ export access_token_secret=ACCESS_TOKEN_SECRET
~$ export env_name=APP_ENV_NAME
```
```python3
from twitivity import Event

class StreamEvent(Event):
    callback: str = "https://yourdomain.com/listener"
    
    def on_data(self, data: dict) -> None:
        # process data

stream_events = StreamEvent()
stream_events.register_webhook() # Register the callback url (first time only)
stream_events.subscribe() # subscribe to events (first time only)
```

## Installation
```
~$ pip install twitivity
```


# Twitivity

![PyPI - Python Version](https://img.shields.io/pypi/pyversions/imgur-scraper) ![PyPI - License](https://img.shields.io/pypi/l/imgur-scraper)

Twitter [Accounts Activity](https://developer.twitter.com/en/docs/accounts-and-users/subscribe-account-activity/overview) API Client Library for Python

## Usage

```python3
from twitivity import Event

class MyEvent(Event):
    callback: str = "https://yourdomain.com/listener"
    env: str = "YOUR ENV"    

    def on_data(self, data: dict) -> None:
        # process data
```

## Installation
TODO

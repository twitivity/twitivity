import json

from twitivity import Event
from pprint import pprint


class StreamEvent(Event):
    CALLBACK_URL: str = "https://1f4396a1.ngrok.io/twitter/callback"

    def on_data(self, data: json) -> None:
        pprint(data, indent=2)


if __name__ == "__main__":
    stream_event = StreamEvent()
    stream_event.listen()
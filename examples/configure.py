from twitivity import Activity

if __name__ == "__main__":
    activity = Activity()
    print(
        activity.register_webhook(
            callback_url="https://1f4396a1.ngrok.io/twitter/callback"
        ).json()
    )
    print(activity.subscribe())

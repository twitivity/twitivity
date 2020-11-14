from twitivity import Activity


def test_subscribe():
    activity = Activity()
    subscription = activity.subscribe()
    assert subscription.status_code == 204


def test_remove_subscription():
    activity = Activity()
    subscription_remove = activity.refresh(webhook_id='1327461535019532288')
    assert subscription_remove.status_code == 204

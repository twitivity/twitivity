from twitivity import url_params


def test_url_params():
    assert url_params("https://saadman.me/listener") == "listener"
    assert (
        url_params("https://www.youdomain.com/twitter/callback") == "twitter/callback"
    )

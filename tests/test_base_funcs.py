import pytest

from rotator import ProxyRotator, logger


logger.remove()


@pytest.mark.parametrize(
	"type_separator, urls_filepath, expected_exception",
	(
		(None, None, None),
		(",", None, ValueError),
		(None, "test.txt", FileNotFoundError),
		(",", "test.txt", FileNotFoundError)
	)
)
def test_init(type_separator, urls_filepath, expected_exception):
	if expected_exception is None:
		ProxyRotator(type_separator=type_separator, urls_filepath=urls_filepath)
	else:
		with pytest.raises(expected_exception):
			ProxyRotator(type_separator=type_separator, urls_filepath=urls_filepath)


def test_prop_proxies_empty_list():
	with pytest.raises(ValueError):
		r = ProxyRotator()
		r._proxy_urls = []
		_ = r.proxies


def test_prop_proxies_url_without_proxies():
	with pytest.raises(ValueError):
		r = ProxyRotator()
		r._proxy_urls = [("https://example.com/proxies.txt", "socks4")]
		_ = r.proxies


@pytest.mark.parametrize("url", ("test.com", "http://tdjkfajkslkdjflaskdjf.com/"))
def test_prop_proxies_error_url(url):
	with pytest.raises(ValueError):
		r = ProxyRotator()
		r._proxy_urls = [(url, "http")]
		_ = r.proxies

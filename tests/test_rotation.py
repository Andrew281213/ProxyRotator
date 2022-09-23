import pytest

from rotator import ProxyRotator, logger


logger.remove()
proxy_list = ["0.0.0.0:8000", "1.1.1.1:8000", "2.2.2.2:8000"]


def test_sync_get_proxy_rotation():
	rotator = ProxyRotator()
	rotator._proxy_list = proxy_list
	double_proxy_list = proxy_list + proxy_list
	for proxy in double_proxy_list:
		get_proxy = rotator.sync_get_proxy()
		assert get_proxy == proxy


@pytest.mark.asyncio
async def test_async_get_proxy_rotation():
	rotator = ProxyRotator()
	rotator._proxy_list = proxy_list
	double_proxy_list = proxy_list + proxy_list
	for proxy in double_proxy_list:
		get_proxy = await rotator.async_get_proxy()
		assert get_proxy == proxy

# ProxyRotator
Простой ротатор прокси. Подгружает прокси по списку ссылок и поочереди выдает 1 прокси при запросе.
Присутствует поддержка асинхронности

## Пример использования:
```python
from rotator import ProxyRotator


rotator = ProxyRotator()
print(rotator.sync_get_proxy())
# http://192.168.1.100:8000
```

## Пример использования с asyncio
```python
import asyncio

from rotator import ProxyRotator


async def start():
	rotator = ProxyRotator()
	print(await rotator.async_get_proxy())


asyncio.run(start())
# http://192.168.1.100:8000
```
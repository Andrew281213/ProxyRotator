import uvicorn

from fastapi import FastAPI

from rotator import ProxyRotator


app = FastAPI()
app.state.rotator = ProxyRotator()


@app.get("/proxy")
async def get_proxy_cnt(cnt: int = 1):
	"""Получает cnt случайных прокси"""
	proxy_list = [app.state.rotator.sync_get_proxy() for _ in range(cnt)]
	return proxy_list[0] if cnt == 1 else proxy_list


@app.get("/proxies")
async def proxies():
	"""Выводит все доступные прокси"""
	return {
		"len": len(app.state.rotator),
		"proxies": app.state.rotator.proxies
	}


if __name__ == '__main__':
	uvicorn.run(app)

import os
import uvicorn
import requests

from datetime import datetime
from fastapi import FastAPI

from rotator import ProxyRotator, logger


description = """
Простое api для получения прокси

TG: @tanf93
"""


app = FastAPI(
	title="Простое api для ротации прокси",
	description=description,
	version="1.0.0",
	contact={
		"name": "Андрей Домахин",
		"email": "andrey.domakhin8@ya.ru",
	},
	openapi_url="/help/openapi.json",
	redoc_url="/help/redoc",
	docs_url="/help/docs"
)
app.state.rotator = ProxyRotator()
app.state.start_time = datetime.now()


def send_tg_msg(msg):
	"""Отправляет сообщение в тг бот

	:param str msg: Текст сообщения
	"""
	tg_chat_id = os.environ.get("TG_CHAT_ID")
	tg_bot_token = os.environ.get("TG_BOT_TOKEN")
	logger.debug(f"Отправляю сообщение в тг бот пользователю {tg_chat_id}")
	url = f"https://api.telegram.org/bot{tg_bot_token}/sendmessage"
	if tg_chat_id is None or tg_bot_token is None:
		logger.warning("Id пользователя и токен бота не должны быть пустыми")
		return
	params = {
		"chat_id": tg_chat_id,
		"text": msg,
		"parse_mode": "HTML",
		"disable_web_page_preview": "true"
	}
	try:
		r = requests.get(url, params=params)
		r.raise_for_status()
		if r.status_code == 200:
			logger.debug(f"Сообщение \"{msg}\" в тг успешно отправлено")
	except Exception as e:
		logger.warning(f"Не удалось отправить сообщение в тг \"{msg}\", {e}")


send_tg_msg("Сервис <b>Proxy Rotator</b> успешно запущен")


@app.get("/proxy", status_code=200, tags=["proxy"])
async def get_proxy_cnt(cnt: int = 1) -> str or dict:
	"""Получает cnt случайных прокси"""
	proxy_list = [app.state.rotator.sync_get_proxy() for _ in range(cnt)]
	app.state.rotator.last_usage = datetime.now()
	return proxy_list[0] if cnt == 1 else proxy_list


@app.get("/proxies", status_code=200, tags=["proxy", "proxies"])
async def proxies():
	"""Выводит все доступные прокси"""
	app.state.rotator.last_usage = datetime.now()
	return {
		"len": len(app.state.rotator),
		"proxies": app.state.rotator.proxies
	}


@app.get("/stats", status_code=200, tags=["proxy", "proxies", "stats"])
async def stats():
	return {
		"proxies_cnt": len(app.state.rotator),
		"iteration_cnt": app.state.rotator.iteration_cnt,
		"uptime": str(datetime.now() - app.state.start_time),
		"last_update": app.state.rotator.last_update,
		"last_usage": app.state.rotator.last_usage,
		"stop_update_after": app.state.rotator.stop_update_after,
		"update_on": app.state.rotator.stop_update,
	}


@app.get("/stats/urls", status_code=200, tags=["urls", "stats"])
async def urls_stats():
	return {
		"total": len(app.state.rotator),
		"urls": app.state.rotator.proxy_urls_stats
	}


if __name__ == '__main__':
	uvicorn.run(app)

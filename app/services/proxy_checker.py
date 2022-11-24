import asyncio

import aiohttp
from aiohttp_socks import ProxyConnector
from fake_useragent import UserAgent
from loguru import logger


class ProxyChecker:
	def __init__(self, proxies, url, needed_text, timeout=20, attempts=3, threads=100):
		"""
		
		:param list[str] proxies: Список прокси для проверки
		:param str url: Ссылка на сайт для проверки
		:param str needed_text: Текст для поиска на сайте
		"""
		self._ua = UserAgent()
		self.proxies = list(set(proxies))
		self.url = url
		self.needed_text = needed_text
		self.timeout = aiohttp.ClientTimeout(total=timeout)
		self.attempts = attempts
		self.good_proxies = []
		self.semaphore = asyncio.BoundedSemaphore(threads)
		self.work = False
	
	@staticmethod
	def get_connector(proxy):
		try:
			return ProxyConnector.from_url(proxy)
		except Exception as e:
			logger.debug(f"Не удалось получить коннектор для прокси {proxy}, {e}")
			return None
	
	async def _get_request(self, connector):
		headers = {
			"user-agent": self._ua.random
		}
		try:
			async with aiohttp.ClientSession(connector=connector, timeout=self.timeout, headers=headers) as session:
				async with session.get(self.url, headers=headers) as resp:
					resp.raise_for_status()
					if resp.status == 200:
						return await resp.text()
		except Exception as e:
			logger.debug(f"Не удалось получить ответ {e}")
	
	async def _attempt_get(self, proxy):
		async with self.semaphore:
			connector = self.get_connector(proxy)
			for i in range(self.attempts):
				resp = await self._get_request(connector)
				if resp is None:
					if i == self.attempts - 1:
						logger.debug(f"Прокси {proxy} не работает на сайте {self.url}")
					continue
				if resp.find(self.needed_text) > -1:
					logger.debug(f"Прокси {proxy} работает на сайте {self.url}")
					self.good_proxies.append(proxy)
					break
			self.proxies.remove(proxy)
	
	async def check_proxies(self):
		try:
			logger.info(f"Начинаю проверку прокси для {self.url}")
			self.work = True
			tasks = [self._attempt_get(proxy) for proxy in self.proxies]
			await asyncio.gather(*tasks)
		finally:
			self.work = False
			logger.info(f"Проверка для {self.url} закончена. Найдено {len(self.good_proxies)} хороших проксей")


async def start():
	with open("proxies.txt") as file:
		proxies = ["socks4://" + row.strip("\n") for row in file]
	checker = ProxyChecker(
		proxies=proxies, url="https://azfilter.jp/catalogue/catalogue", needed_text="Catalogue Search"
	)
	await checker.check_proxies()

import os
import requests
import itertools

from dotenv import load_dotenv
from loguru import logger


class ProxyRotator:
	def __init__(self, type_separator=None, urls_filepath=None):
		self._proxy_urls = []
		load_dotenv()
		if type_separator is None:
			type_separator = os.environ.get("PROXY_TYPE_SEPARATOR")
		if urls_filepath is None:
			urls_filepath = os.environ.get("URLS_FILEPATH")
		logger.debug(f"Разделитель типов: {type_separator}, путь к файлу с прокси {urls_filepath}")
		self._load_urls(urls_filepath, type_separator)
		if len(self._proxy_urls) == 0:
			raise ValueError("Нет ссылок для загрузки прокси")
		self._proxy_list = None
		self._iter = None
	
	@property
	def proxies(self):
		"""Список прокси"""
		if self._proxy_list is None:
			logger.debug("Начинаю загрузку прокси")
			self._proxy_list = self._load_proxies_from_urls()
			cnt = len(self._proxy_list)
			self._proxy_list = list(set(self._proxy_list))
			logger.debug(f"Удалено {cnt - len(self._proxy_list)} дубликатов прокси")
			logger.info(f"Загружено {len(self._proxy_list)} прокси")
		if len(self._proxy_list) == 0:
			raise ValueError("Нет прокси для ротации")
		return self._proxy_list
	
	@property
	def __iter(self):
		"""Синхронный итератор"""
		if self._iter is None:
			self._iter = self.__next__()
		return self._iter
	
	def _load_urls(self, filepath, type_separator):
		"""Загрузка ссылок из файла"""
		logger.debug("Загружаю ссылки из файла")
		with open(filepath, "r") as file:
			urls = [row.strip("\n") for row in file]
		for url in urls:
			url_parts = url.split(type_separator)
			if len(url_parts) > 1:
				self._proxy_urls.append(url_parts)
				continue
			logger.debug(f"Неверно указана ссылка: {url}")
		logger.info(f"Загружено {len(self._proxy_urls)} ссылок")
	
	def __next__(self):
		"""Синхронно получить следующий прокси"""
		for proxy in itertools.cycle(self.proxies):
			logger.debug(f"Синхронно получен прокси {proxy}")
			yield proxy
	
	def __iter__(self):
		"""Получить синхронный итератор"""
		return self.__iter
	
	def sync_get_proxy(self):
		"""Синхронно получает прокси"""
		it = self.__iter__()
		return it.__next__()
	
	def _load_proxies_from_urls(self):
		"""Загрузка прокси по ссылкам"""
		proxy_list = []
		for url, proxy_type in self._proxy_urls:
			try:
				r = requests.get(url, timeout=10)
				r.raise_for_status()
				proxy_from_url = [f"{proxy_type}://{row.strip()}" for row in r.text.split("\n") if row.strip() != ""]
				proxy_list += proxy_from_url
				logger.debug(f"Загружено {len(proxy_from_url)} прокси с {url}")
			except Exception as e:
				logger.warning(f"Не удалось загрузить прокси с {url}")
				logger.debug(f"Не удалось загрузить прокси {e}")
		return proxy_list

import os
import requests
import itertools

from dotenv import load_dotenv
from datetime import datetime
from threading import Thread
from loguru import logger
from time import sleep


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
		self._aiter = None
		self.iteration_cnt = 0
		self.last_update = datetime(year=2000, month=1, day=1, hour=0, minute=0, second=0)
		self.last_usage = datetime(year=2000, month=1, day=1, hour=0, minute=0, second=0)
		self.proxy_urls_stats = []
		self.update_every = 60 * 10     # Каждые 10 мин
		self.stop_update = False
		self.stop_update_after = self.update_every * 3     # После 3‑х обновлений
		self.__update_thread = Thread(daemon=True)          # Поток для обновления прокси
	
	@property
	def proxies(self):
		"""Список прокси"""
		if self._proxy_list is None:
			if self.__update_thread._target is None:
				logger.debug("Создаю поток обновления прокси")
				# Обновляем дату последнего использования, чтобы обновление не выключилось
				self.last_usage = datetime.now()
				self.__update_thread._target = self.__update_proxies
				self.__update_thread.start()
			else:
				logger.info("Ура! Сервис снова используется. Включаю обновление прокси")
				self.last_usage = datetime.now()
				self.stop_update = False
			# Ждем несколько секунд для загрузки прокси
			sleep(8)
		# Если прокси не успели загрузить ждем еще какое-то время, затем бросаем исключение
		for _ in range(3):
			if len(self._proxy_list) == 0:
				sleep(2)
				continue
			break
		if len(self._proxy_list) == 0:
			raise ValueError("Нет прокси для ротации")
		return self._proxy_list
	
	@property
	def __iter(self):
		"""Синхронный итератор"""
		if self._iter is None:
			self._iter = self.__next__()
		return self._iter
	
	@property
	def __aiter(self):
		"""Асинхронный итератор"""
		if self._aiter is None:
			self._aiter = self.__anext__()
		return self._aiter
	
	def _load_urls(self, filepath, type_separator):
		"""Загрузка ссылок из файла"""
		logger.debug("Загружаю ссылки из файла")
		with open(filepath, "r") as file:
			urls = [row.strip("\n") for row in file]
		self.proxy_urls = []
		for url in urls:
			# Если в строке не найден тип прокси, отбрасываем
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
			self.iteration_cnt += 1
			yield proxy
	
	async def __anext__(self):
		"""Асинхронное получение прокси"""
		for proxy in itertools.cycle(self.proxies):
			logger.debug(f"Асинхронно получен прокси {proxy}")
			self.iteration_cnt += 1
			yield proxy
	
	def __iter__(self):
		"""Получить синхронный итератор"""
		return self.__iter
	
	def __aiter__(self):
		"""Получить асинхронный итератор"""
		return self.__aiter
	
	def sync_get_proxy(self):
		"""Синхронно получает прокси"""
		it = self.__iter__()
		return it.__next__()
	
	async def async_get_proxy(self):
		"""Асинхронно получает прокси"""
		it = self.__aiter__()
		return await it.__anext__()
	
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
				self.proxy_urls_stats.append({
					"url": url,
					"proxy_type": proxy_type,
					"proxies": len(proxy_from_url)
				})
			except Exception as e:
				logger.warning(f"Не удалось загрузить прокси с {url}")
				logger.debug(f"Не удалось загрузить прокси {e}")
		return proxy_list
	
	def __update_proxies(self):
		while True:
			if self.stop_update:
				# Проверяем флаг обновления каждые несколько секунд
				logger.debug("Авто обновление прокси остановлено")
				sleep(5)
				continue
			if (datetime.now() - self.last_usage).seconds >= self.stop_update_after:
				logger.info("Сервис давно не использовался. Останавливаю обновление прокси")
				# Устанавливаем флаг обновления на False и сбрасываем список прокси, чтобы при получении после включения
				# обновления прокси были новыми
				self.stop_update = True
				self._proxy_list = None
				continue
			self._proxy_list = self._load_proxies_from_urls()
			self._iter = None
			self._aiter = None
			self.last_update = datetime.now()
			i = 0
			while i <= self.update_every:
				sleep(1)
				i += 1
	
	def __len__(self):
		return len(self._proxy_list) if self._proxy_list is not None else 0

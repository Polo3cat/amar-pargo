import logging
import os
import re

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.action_chains import ActionChains

import numpy as np
import cv2


_MOZ_LOG_DIR = 'logs/'
_MOZ_LOG_FILE = os.path.join(_MOZ_LOG_DIR, 'firefox.log')

class FirefoxLoggigError(Exception):
	def __init__(self,message):
		self.message = message


class WebDriver:
	def __init__(self, url: str):
		try:
			logfiles = os.listdir(_MOZ_LOG_DIR)
			for logfile in logfiles:
				os.remove( os.path.join(_MOZ_LOG_DIR,logfile) )
		except OSError:
			os.mkdir(_MOZ_LOG_DIR)

		self.url = url
		firefox_options = Options()
		firefox_options.add_argument('--width=1920')
		firefox_options.add_argument('--height=1080')

		firefox_options.add_argument(f'-MOZ_LOG_FILE={_MOZ_LOG_FILE}')
		firefox_options.add_argument('-MOZ_LOG=timestamp,rotate:200,nsHttp:1')

		self.driver = webdriver.Firefox(options=firefox_options)
		self.driver.get(url)

	def __del__(self):
		self.driver.quit()

	def take_screenshot(self, region):
		screenshot = self.driver.get_screenshot_as_png()
		bytes_as_np_array = np.frombuffer(screenshot, dtype=np.uint8)
		image = cv2.imdecode(bytes_as_np_array, cv2.IMREAD_COLOR)
		grey_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
		return grey_image
	
	def click(self, coords):
		top_left_element = self.driver.find_element_by_tag_name('html')
		actions = ActionChains(self.driver)
		actions.move_to_element_with_offset(top_left_element, *coords)
		actions.click()
		actions.perform()

	def is_playing(self):
		try:
			logfiles = os.listdir(_MOZ_LOG_DIR)
		except OSError as e:
			logging.exception(e)
			raise FirefoxLoggigError(f"Logging dir {_MOZ_LOG_DIR} does not exist")
		
		if not logfiles:
			raise FirefoxLoggigError(f"No logging files in {_MOZ_LOG_DIR}")
		
		hosted_file_regexp = re.compile(r'((http|https)://)?(\w+\.)+\w+(/\w+)*/(\w+((_|-)+\w+)*\.)+(mp4|flv|mov|avi|mkv|webm)')
		youtube_regexp = re.compile(r'(\w|-)+\.googlevideo.com/videoplayback')
		
		for logfile in logfiles:
			filename = os.path.join(_MOZ_LOG_DIR, logfile)
			with open(filename, 'r') as file:
				log = file.read()
				match = hosted_file_regexp.search(log)
				youtube_match = youtube_regexp.search(log)
			if match:
				return match.group(0)
			elif youtube_match:
				youtube_id_regex = re.compile(r'video_id=(?P<youtube_id>(\w|_)+)&')
				youtube_id_match = youtube_id_regex.search(log)
				youtube_id = youtube_id_match.group('youtube_id')
				return f'https://www.youtube.com/watch?v={youtube_id}'
		return False

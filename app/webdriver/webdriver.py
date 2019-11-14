from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.action_chains import ActionChains

import numpy as np
import cv2


class WebDriver:
	def __init__(self, url: str):
		self.url = url
		firefox_options = Options()
		firefox_options.add_argument('--width=1920')
		firefox_options.add_argument('--height=1080')
		self.driver = webdriver.Firefox(options=firefox_options)
		self.driver.get(url)

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
		return True

	def __del__(self):
		self.driver.quit()
		
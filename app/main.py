import argparse
import time

from webdriver.webdriver import WebDriver
from tools import dummy_tool


def main(url: str, buffer_time: int):
	tools = [dummy_tool]
	web_driver = WebDriver(url)
	region = None
	playing = False
	while not playing:
		screenshot = web_driver.take_screenshot(region)
		high_score = 0
		high_tool = None
		for tool in tools:
			score = tool.evaluate(screenshot)
			if score > high_score:
				high_score = score
				high_tool = tool
		do, what = high_tool.act(screenshot)
		if do == 'wait':
			time.sleep(what)
		elif do == 'click':
			web_driver.click(what)
		elif do == 'focus':
			region = what
		time.sleep(buffer_time)
		playing = web_driver.is_playing()


if __name__ == '__main__':
	parser = argparse.ArgumentParser('Amaro Pargo, the corsair of the seven seas')
	parser.add_argument('url', type=str)
	parser.add_argument('buffer_time', type=int)
	args = parser.parse_args()
	main(args.url, args.buffer_time)
import argparse
import time
import logging

from webdriver.webdriver import WebDriver
from tools.dummy_tool import DummyTool
from tools.triangle_detection import TriangleDetector
import cv2

from tools.tool import NothingError


FORMAT = '%(levelname)s %(asctime)s (%(module)s:%(lineno)d) %(message)s'
logging.basicConfig(format=FORMAT, level=logging.INFO)


def main(url: str, buffer_time: int, tools: list, patience: int, **kwargs):
	web_driver = WebDriver(url)
	region = None
	playing = False
	give_up = False
	nothing = 0
	while not playing and not give_up:
		screenshot = web_driver.take_screenshot(region)
		high_score = 0
		high_tool = None
		for tool in tools:
			score = tool.evaluate(screenshot)
			if score >= high_score:
				high_score = score
				high_tool = tool
		try:
			do, what = high_tool.act(screenshot)
			if do == 'wait':
				time.sleep(what)
			elif do == 'click':
				web_driver.click(what)
			elif do == 'focus':
				region = what
			nothing = 0
		except NothingError as e:
			logging.info(e)
			nothing += 1

		time.sleep(buffer_time)
		playing = web_driver.is_playing()
		give_up = nothing > patience
	if give_up:
		logging.info('We gave up')
	else:
		logging.info('The video is playing')


def parse_arguments():
	parser = argparse.ArgumentParser('Amaro Pargo, the corsair of the seven seas')
	parser.add_argument('url', type=str)
	parser.add_argument('--buffer_time', type=int, default=3)
	parser.add_argument('--binarization', 
						type=str, 
						choices=['gt','amt','agt'],
						default='agt',
						help='gt: Global Thresholding\namt: Adaptive Mean Thresholding\nagt: Adaptive Gaussian Thresholding')
	parser.add_argument('--triangle_size', type=str, choices=['small','medium','big'], default='medium')
	parser.add_argument('--patience', type=int, default=3, help='Consecutive times that tools can report as having done nothing')
	return vars(parser.parse_args())
	

def set_up_tools(binarization: str, triangle_size: str, **kwargs):
	tools = []
	tools.append(DummyTool())
	tools.append(TriangleDetector(binarization, triangle_size))
	kwargs['tools'] = tools
	return kwargs


if __name__ == '__main__':
	arguments = parse_arguments()
	arguments = set_up_tools(**arguments)
	main(**arguments)

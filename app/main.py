import argparse
import time

from webdriver.webdriver import WebDriver
from tools.dummy_tool import DummyTool
from tools.triangle_detection import TriangleDetector
import cv2


def main(url: str, buffer_time: int, tools: list, **kwargs):
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

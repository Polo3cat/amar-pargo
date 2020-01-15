import argparse
import time
import logging

from webdriver.webdriver import WebDriver, FirefoxLoggigError
from tools.dummy_tool import DummyTool
from tools.triangle_detection import TriangleDetector, PrintTriangleDetector
from tools.debug_tool import DebugTool
import cv2

from tools.tool import NothingError


FORMAT = '%(levelname)s %(asctime)s (%(module)s:%(lineno)d) %(message)s'
logging.basicConfig(format=FORMAT, level=logging.INFO)


def main(url: str, buffer_time: int, tools: list, patience: int, presentation: bool, **kwargs):
	"""
		Orchestrates the pipeline responsible for playing and detecting a video playing
	"""
	web_driver = WebDriver(url)
	region = None
	give_up = False
	nothing = 0
	try:
		playing = web_driver.is_playing()
	except FirefoxLoggigError as e:
		raise e

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
			logging.info(f'{do} {what}')
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
		except AttributeError as e:
			logging.exception(e)

		give_up = nothing > patience
		time.sleep(buffer_time)
		try:
			playing = web_driver.is_playing()
		except FirefoxLoggigError as e:
			raise e

	if give_up:
		logging.info('We gave up')
	if playing:
		logging.info(f'The video is very likely playing from {playing}')
	if presentation:
		logging.info('Presentation mode on, waiting for SIGKILL [Ctrl+C]')
		while True:
			pass


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
	parser.add_argument('--presentation', action='store_true', help='One click and leave playing')
	parser.add_argument('--debug', action='store_true')
	parser.add_argument('--print', action='store_true')
	return vars(parser.parse_args())
	

def set_up_tools(binarization: str, triangle_size: str, debug: bool, print: bool, **kwargs):
	tools = []
	if debug:
		logging.info('Debug mode --- Loading only Debug Tool')
		tools.append(DebugTool())
	elif print:
		tools.append(PrintTriangleDetector(binarization, triangle_size))
		kwargs['patience'] = -1
	else:
		tools.append(TriangleDetector(binarization, triangle_size))

	kwargs['tools'] = tools
	return kwargs


if __name__ == '__main__':
	arguments = parse_arguments()
	arguments = set_up_tools(**arguments)
	main(**arguments)

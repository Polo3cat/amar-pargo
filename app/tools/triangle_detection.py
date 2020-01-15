from math import sqrt
import pickle
import os
import sys

import cv2
import numpy as np

from .tool import NothingError, Tool


class BinarizationMethodError(Exception):
	pass

class TriangleSizeError(Exception):
	pass


class TriangleDetector(Tool):
	def __init__(self, binarization, triangle_size):
		super().__init__()
		if binarization == 'gt':
			def tmp(img):
				_,ret = cv2.threshold(img,127,255,cv2.THRESH_OTSU)
				return ret
			self.threshold = tmp
		elif binarization == 'amt':
			self.threshold = lambda img: cv2.adaptiveThreshold(img,255,cv2.ADAPTIVE_THRESH_MEAN_C,
	            								   			   cv2.THRESH_BINARY,11,2)
		elif binarization == 'agt':
			self.threshold = lambda img: cv2.adaptiveThreshold(img,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
	            											   cv2.THRESH_BINARY,11,2)
		else:
			raise BinarizationMethodError()

		triangle_detector_data = os.path.dirname(os.path.abspath(sys.modules[__name__].__file__))
		with open(os.path.join(triangle_detector_data, 'triangle_detection_data/gmm_triangle_area_model.pkl'), 'rb') as f:
			self.gmm_triangle_area = pickle.load(f)
		means_ = list(enumerate(self.gmm_triangle_area.means_))
		means_ = [x[0] for x in sorted(means_, key=lambda x: x[1])]
		self.triangle_size_class = dict(zip(['small', 'medium', 'big'], means_))[triangle_size]


	def best_softmaxed_triangle(self, screenshot):
		total_area = len(screenshot) * len(screenshot[0])

		blur = cv2.medianBlur(screenshot, 5)
		threshold = self.threshold(blur)
		contours, _ = cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
		areas, triangles = zip(*[cv2.minEnclosingTriangle(c) for c in contours])
		too_small = 0
		bad_ratio = 0
		bad_shape = 0
		filtered_triangles = []
		for contour, triangle, area in zip(contours, triangles, areas):
			if triangle is None or area == 0:
				too_small += 1
				continue

			area_class = self.gmm_triangle_area.predict(np.array(area).reshape(-1,1))
			if area_class != self.triangle_size_class:
				continue

			difference = 0
			for point in contour:
				d = cv2.pointPolygonTest(triangle, (point[0,0],point[0,1]), True)
				difference += d*d
			difference = sqrt(difference)/len(contour)

			p1 = (triangle[0,0,0],triangle[0,0,1])
			p2 = (triangle[1,0,0],triangle[1,0,1])
			p3 = (triangle[2,0,0],triangle[2,0,1])

			# Is the left side perpendicular and the right vertice between the other two?
			# Does it look like a Play button triangle...?
			if p1[0] != p2[0] or p2[1] - (p2[1]-p1[1])/2 != p3[1]:
				bad_shape += 1
				continue

			filtered_triangles.append((triangle, difference))
		total = sum((difference for _,difference in filtered_triangles)) + 1
		softmaxed = ((triangle, difference/total) for triangle,difference in filtered_triangles)
		try:
			return min(softmaxed, key=lambda x: x[1])
		except ValueError:
			return (None, 1)


	def evaluate(self, screenshot):
		"""
			Is there a triangle or a set of triangles that might be play buttons?

			Return value between 0 and 1 
		"""
		_, score = self.best_softmaxed_triangle(screenshot)
		return 1-score


	def act(self, screenshot):
		"""
			What do we do?
			We 'click' on the best scoring triangle
		"""
		triangle, _ = self.best_softmaxed_triangle(screenshot)
		if triangle is None:
			raise NothingError('No triangles passed the filters')
		p1 = (triangle[0,0,0],triangle[0,0,1])
		p2 = (triangle[1,0,0],triangle[1,0,1])
		p3 = (triangle[2,0,0],triangle[2,0,1])
		center = (p3[0] - (p3[0]-p1[0])/2 , p2[1] - (p2[1]-p1[1])/2)
		return 'click', center


class PrintTriangleDetector(TriangleDetector):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

	def best_softmaxed_triangle(self, screenshot):
		total_area = len(screenshot) * len(screenshot[0])

		blur = cv2.medianBlur(screenshot, 5)
		threshold = self.threshold(blur)
		cv2.imwrite('screenshot.png', screenshot)
		cv2.imwrite('threshold.png', threshold)
		contours, _ = cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

		img1 = screenshot.copy()
		img1 = cv2.cvtColor(img1, cv2.COLOR_GRAY2BGR)
		img1 = cv2.drawContours(img1, contours, -1, (0,255,0), 2)
		cv2.imwrite('contours.png', img1)

		areas, triangles = zip(*[cv2.minEnclosingTriangle(c) for c in contours])

		img1 = screenshot.copy()
		img1 = cv2.cvtColor(img1, cv2.COLOR_GRAY2BGR)
		color = (0,0,255)
		for triangle in triangles:
			p1 = (triangle[0,0,0],triangle[0,0,1])
			p2 = (triangle[1,0,0],triangle[1,0,1])
			p3 = (triangle[2,0,0],triangle[2,0,1])
			cv2.line(img1, p1,p2, color,2)
			cv2.line(img1, p2,p3, color,2)
			cv2.line(img1, p3,p1, color,2)

		cv2.imwrite('triangles.png', img1)

		too_small = 0
		bad_ratio = 0
		bad_shape = 0
		filtered_triangles = []
		for contour, triangle, area in zip(contours, triangles, areas):
			if triangle is None or area == 0:
				too_small += 1
				continue

			area_class = self.gmm_triangle_area.predict(np.array(area).reshape(-1,1))
			if area_class != self.triangle_size_class:
				continue

			difference = 0
			for point in contour:
				d = cv2.pointPolygonTest(triangle, (point[0,0],point[0,1]), True)
				difference += d*d
			difference = sqrt(difference)/len(contour)

			p1 = (triangle[0,0,0],triangle[0,0,1])
			p2 = (triangle[1,0,0],triangle[1,0,1])
			p3 = (triangle[2,0,0],triangle[2,0,1])

			# Is the left side perpendicular and the right vertice between the other two?
			# Does it look like a Play button triangle...?
			if p1[0] != p2[0] or p2[1] - (p2[1]-p1[1])/2 != p3[1]:
				bad_shape += 1
				continue

			filtered_triangles.append((triangle, difference))
		total = sum((difference for _,difference in filtered_triangles)) + 1
		softmaxed = [(triangle, difference/total) for triangle,difference in filtered_triangles]

		img1 = screenshot.copy()
		img1 = cv2.cvtColor(img1, cv2.COLOR_GRAY2BGR)
		color = (0,0,255)
		for triangle, score in softmaxed:
			p1 = (triangle[0,0,0],triangle[0,0,1])
			p2 = (triangle[1,0,0],triangle[1,0,1])
			p3 = (triangle[2,0,0],triangle[2,0,1])
			cv2.line(img1, p1,p2, color,2)
			cv2.line(img1, p2,p3, color,2)
			cv2.line(img1, p3,p1, color,2)
			cv2.putText(img1, f'{score:.3f}', p3, cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2, cv2.LINE_AA)

		cv2.imwrite('filtered_triangles.png', img1)

		try:
			return min(softmaxed, key=lambda x: x[1])
		except ValueError:
			return (None, 1)


	def evaluate(self, screenshot):
		"""
			Is there a triangle or a set of triangles that might be play buttons?

			Return value between 0 and 1 
		"""
		_, score = self.best_softmaxed_triangle(screenshot)
		return 1-score

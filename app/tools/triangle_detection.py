from math import sqrt
import cv2

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

		if triangle_size == 'small':
			self.triangle_size = 1/6
		elif triangle_size == 'medium':
			self.triangle_size = 3/6
		elif triangle_size == 'big':
			self.triangle_size = 5/6
		else:
			raise TriangleSizeError()
		self.area_epsilon = 1/6


	def best_softmaxed_triangle(self, screenshot):
		area_epsilon = self.area_epsilon
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

			area_ratio = area/total_area
			if area_ratio > self.triangle_size + area_epsilon or area_ratio < self.triangle_size - area_epsilon:
				bad_ratio += 1
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
		area_epsilon = self.area_epsilon
		total_area = len(screenshot) * len(screenshot[0])

		blur = cv2.medianBlur(screenshot, 5)
		threshold = self.threshold(blur)
		cv2.imwrite('thresh.png', threshold)
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

			area_ratio = area/total_area
			if area_ratio > self.triangle_size + area_epsilon or area_ratio < self.triangle_size - area_epsilon:
				bad_ratio += 1
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
		total = sum((difference for _,difference in filtered_triangles))
		softmaxed = [(triangle, difference/(total+1)) for triangle,difference in filtered_triangles]
		for triangle, score in softmaxed:
			p1 = (triangle[0,0,0],triangle[0,0,1])
			p2 = (triangle[1,0,0],triangle[1,0,1])
			p3 = (triangle[2,0,0],triangle[2,0,1])
			center = (p3[0] - (p3[0]-p1[0])/2 , p2[1] - (p2[1]-p1[1])/2)
			cv2.circle(screenshot, p1, 5, (255,0,0), -1)
			cv2.circle(screenshot, p2, 5, (0,255,0), -1)
			cv2.circle(screenshot, p3, 5, (0,0,255), -1)
			cv2.putText(screenshot, f'{score:.4f}', tuple(map(int, center)), cv2. FONT_HERSHEY_SIMPLEX, 1, (255,255,0))
		cv2.imwrite('test.png', screenshot)

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

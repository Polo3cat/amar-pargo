from math import sqrt
import cv2


class BinarizationMethodError(Exception):
	pass

class TriangleSizeError(Exception):
	pass


class TriangleDetector:
	def __init__(self, binarization, triangle_size):
		if binarization == 'gt':
			self.threshold = lambda img: cv2.threshold(img,127,255,cv2.THRESH_BINARY)
		elif binarization == 'amt':
			self.threshold = lambda img: cv2.adaptiveThreshold(img,255,cv2.ADAPTIVE_THRESH_MEAN_C,
	            								   			   cv2.THRESH_BINARY,11,2)
		elif binarization == 'agt':
			self.threshold = lambda img: cv2.adaptiveThreshold(img,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
	            											   cv2.THRESH_BINARY,11,2)
		else:
			raise BinarizationMethodError()

		if triangle_size == 'small':
			self.triangle_size = 1/9
		elif triangle_size == 'medium':
			self.triangle_size = 3/9
		elif triangle_size == 'big':
			self.triangle_size = 6/9
		else:
			raise TriangleSizeError()
		self.area_epsilon = 1/9


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
		total = sum((difference for _,difference in filtered_triangles))
		softmaxed = ((triangle, difference/total) for triangle,difference in filtered_triangles)
		return min(softmaxed, key=lambda x: x[1])


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
		p1 = (triangle[0,0,0],triangle[0,0,1])
		p2 = (triangle[1,0,0],triangle[1,0,1])
		p3 = (triangle[2,0,0],triangle[2,0,1])
		center = (p3[0] - (p3[0]-p1[0])/2 , p2[1] - (p2[1]-p1[1])/2)
		return 'click', center

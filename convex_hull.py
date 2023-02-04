from which_pyqt import PYQT_VER
if PYQT_VER == 'PYQT5':
	from PyQt5.QtCore import QLineF, QPointF, QObject
elif PYQT_VER == 'PYQT4':
	from PyQt4.QtCore import QLineF, QPointF, QObject
elif PYQT_VER == 'PYQT6':
	from PyQt6.QtCore import QLineF, QPointF, QObject
else:
	raise Exception('Unsupported Version of PyQt: {}'.format(PYQT_VER))



import time

# Some global color constants that might be useful
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)

# Global variable that controls the speed of the recursion automation, in seconds
#
PAUSE = 0.25

#
# This is the class you have to complete.
#
class ConvexHullSolver(QObject):

# Class constructor
	def __init__( self):
		super().__init__()
		self.pause = False

# Some helper methods that make calls to the GUI, allowing us to send updates
# to be displayed.

	def showTangent(self, line, color):
		self.view.addLines(line.copy(),color)
		if self.pause:
			time.sleep(PAUSE)

	def eraseTangent(self, line):
		self.view.clearLines(line.copy())

	def blinkTangent(self,line,color):
		self.showTangent(line,color)
		self.eraseTangent(line)

	def showHull(self, polygon, color):
		self.view.addLines(polygon.copy(),color)
		if self.pause:
			time.sleep(PAUSE)

	def eraseHull(self,polygon):
		self.view.clearLines(polygon)

	def showText(self,text):
		self.view.displayStatusText(text)

# This is the method that gets called by the GUI and actually executes
# the finding of the hull
	def compute_hull( self, points, pause, view):
		self.pause = pause
		self.view = view
		assert( type(points) == list and type(points[0]) == QPointF )

		t1 = time.time()
		points = sorted(points, key=lambda x:x.x())
		t2 = time.time()

		t3 = time.time()
		# this is a dummy polygon of the first 3 unsorted points
		#polygon = [QLineF(points[i],points[(i+1)%3]) for i in range(3)]
		polygon = self.solve_hull(points)
		t4 = time.time()

		# when passing lines to the display, pass a list of QLineF objects.  Each QLineF
		# object can be created with two QPointF objects corresponding to the endpoints
		self.showHull(polygon,RED)
		self.showText('Time Elapsed (Convex Hull): {:3.3f} sec'.format(t4-t3))

	def solve_hull(self, points): 
		count = len(points)
		if count <= 3:
			points = sortClockwise(points)
			return [QLineF(points[i],points[(i+1)%count]) for i in range(count)]
		
		left = self.solve_hull(points[:count//2])
		right = self.solve_hull(points[count//2:])

		self.showTangent(left, RED)
		self.showTangent(right, RED)

		comp = self.combine_hulls(left, right)

		self.eraseTangent(left)
		self.eraseTangent(right)

		return comp

	def combine_hulls(self, left, right):
		upper = self.findTangent(left, right, True)
		self.showTangent([upper], BLUE)
		lower = self.findTangent(left, right, False)
		self.showTangent([lower], BLUE)
		i = 0

	def findTangent(self, left, right, isUpper = True):
		leftCond = lambda now, next: slope(now) > slope(next)
		rightCond = lambda now, next: slope(now) < slope(next)

		if (not isUpper):
			temp = leftCond
			leftCond = rightCond
			rightCond = temp
			
		pi = getExtremePointIndex(left, False)
		qi = getExtremePointIndex(right, True)
		temp = QLineF(left[pi].p1(), right[qi].p1())
		self.showTangent([temp], BLUE)
		changed = True
		while changed:
			changed = False

			next = lambda left, right, pi, qi: QLineF(left[pi - 1 % len(left)].p1(), right[qi].p1())
			while leftCond(temp, next(left, right, pi, qi)):
				ri = pi - 1 % len(left)
				self.eraseTangent([temp])
				temp = QLineF(left[ri].p1(), right[qi].p1())
				self.showTangent([temp], BLUE)
				pi = ri
				changed = True

			self.eraseTangent([temp])
			next = lambda left, right, pi, qi: QLineF(left[pi].p1(), right[qi + 1 % len(right)].p1())

			while rightCond(temp, next(left, right, pi, qi)):
				ri = qi + 1 % len(right)
				self.eraseTangent([temp])
				temp = QLineF(left[pi].p1(), right[ri].p1())
				self.showTangent([temp], BLUE)
				qi = ri
				changed = True

			self.eraseTangent([temp])
		return temp
		
def sortClockwise(points):
	assert(len(points) > 0)

	p1 = points[0]

	arr = [QLineF(p1, points[i+1]) for i in range(len(points) - 1)]
	sort = sorted(arr, key=lambda x:slope(x), reverse=True)
	all = [sort[i].p2() for i in range(len(sort))]
	all.insert(0, p1)
	return all
def slope(line):
	return line.dy() / line.dx()
def getExtremePointIndex(lines, isLeft = True):
	points = [lines[i].p1() for i in range(len(lines))]
	val = -1
	passes = lambda x, y: x.x() > y.x() if isLeft else lambda x, y: x.x() < y.x()
	for i in range(len(points)):
		if val < 0 or passes(points[val], points[i]):
			val = i
	return val
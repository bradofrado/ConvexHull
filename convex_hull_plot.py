import matplotlib.pyplot as plt
from Proj2GUI import randomDistributed

from convex_hull import ConvexHullSolver
import time as t
import numpy as np

class ConvexHullPlot():
	def __init__(self, times) -> None:
		self.times = times
		self.solver = ConvexHullSolver()
		plt.xscale("log")
		self.m, = plt.plot([], [])

	def plotAll(self, C = 1):
		data = self.getTimesData()

		X = np.arange(0, self.times[-1], 10)
		self.m.set_xdata(X)

		plt.scatter(self.times, data)
		self.m.set_ydata(X * np.log(X) * C)

		plt.show()
	
	def getTimesData(self):
		data = []
		for time in self.times:
			points = randomDistributed(time)
			points = sorted(points, key=lambda x:x.x())
			t1 = t.time()
			self.solver.solve_hull(points)
			t2 = t.time()
			diff = t2 - t1
			data.append(diff)
		return data

plotter = ConvexHullPlot([10, 100, 1000, 10000, 100000])
plotter.plotAll(1/120000)
## import libraries and functions
``` py 
import numpy as np
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt
import os
``` 
## Profileplot
``` py 
class ProfilePlot:
	"""
    ProfilePlot class for creating and saving pressure vs. time plots.

    This class uses NumPy, SciPy, and Matplotlib to create and save a pressure vs. time plot
    based on input time and pressure data. The plot is customized with specific styling and
    saved as an image file.

    Attributes:
        time (np.ndarray): Array of time values.
        pressure (np.ndarray): Array of corresponding pressure values.
        touch_dpi (int): Dots per inch (DPI) for touchscreen display.
        graph_width (int): Width of the graph in pixels.
        graph_height (int): Height of the graph in pixels.
        interpolate_list (list): List for interpolated pressure values.
    """
	def __init__(self):
		"""
        Initialize ProfilePlot with default values and check for the existence of a previous graph image.
        """
		super().__init__()
		self.time = np.array([0,0,0,0,0,0,0])
		self.pressure = np.array([0,0,0,0,0,0,0])
		self.touch_dpi = 133
		self.graph_width = 800
		self.graph_height = 350
		self.interpolate_list = []
		if os.path.isfile("BrewGraph.png"):
			print('Removing Previous Graph Pic')
			os.remove("BrewGraph.png")
	def create_plot(self, time, pressure):
		"""
        Create and save a pressure vs. time plot.
        Args:
            time (list or np.ndarray): Time values for the x-axis.
            pressure (list or np.ndarray): Pressure values for the y-axis.
        """
		self.time = np.array(time)
		self.pressure = np.array(pressure)
		self.y_data = interp1d(self.time, self.pressure)
		for i in range(100000):
			try:
				self.interpolate_list.append(self.y_data[i])
			except:
				break
		fig = plt.figure(figsize = (self.graph_width/self.touch_dpi, self.graph_height/self.touch_dpi), dpi = self.touch_dpi, facecolor = '#04043B')
		ax = fig.add_subplot(111)
		ax.set_facecolor('#04043B')
		ax.set_xlabel('Time (sec)')
		ax.set_ylabel('Pressure (Bar)')
		ax.xaxis.label.set_color('#ff8c00')
		ax.yaxis.label.set_color('#ff8c00')
		ax.tick_params(axis = 'x', colors = '#ff8c00')
		ax.tick_params(axis = 'y', colors = '#ff8c00')
		ax.spines['left'].set_visible(False)
		ax.spines['right'].set_visible(False)
		ax.spines['top'].set_visible(False)
		ax.spines['bottom'].set_visible(False)
		#default_x_ticks = range(len(time))
		#plt.xticks(default_x_ticks, time)
		plt.plot(self.time,self.pressure, color = '#ff8c00', marker = 'o', label = "Desired Pressure")
		
		if os.path.isfile("BrewGraph.png"):
			print('Removing Previous Graph Pic')
			os.remove("BrewGraph.png")
		plt.savefig("BrewGraph.png")
		#plt.show()
	def getPressureTarg(self, elapsedTime):
		"""
        Get interpolated pressure value at a specific elapsed time.
        Args:
            elapsedTime (float): Elapsed time for which pressure value is requested.
        Returns:
            float: Interpolated pressure value at the specified elapsed time.
        """
		self.val = self.y_data(elapsedTime)
		return self.val
``` 


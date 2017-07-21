import numpy as np
from matplotlib.cm import jet
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from .masks import *

class RippleTank():
    """
    RippleTank objects are the core of the simulation. They contain both sources and masks.
    The class describes the space in which the waves will move and the force acting on them.
    """
    def __init__(self, xdim = (-15, 15), ydim = (-15, 15), deep = 1.0,
                n_cells_x = 100, n_cells_y = 100, mask = 1.0,
                bc = 'open', alpha = 0.45, units = 'cm'):
        posible_bcs = 'open', 'close'
        if not bc in posible_bcs:
            raise(Exception("'%s' is not a valid boundary condition."%bc))

        posible_units = 'cm', 'm'
        if not units in posible_units:
            raise(Exception("'%s' are not a valid units."%units))

        x = np.linspace(xdim[0], xdim[1], n_cells_x)
        y = np.linspace(ydim[0], ydim[1], n_cells_y)
        self.dx = x[1] - x[0]
        self.dy = y[1] - y[0]

        self.X, self.Y = np.meshgrid(x, y) #: two 2d arrays describing the coordinates of the tank

        self.xdim = xdim #: x dimensions of the grid
        self.ydim = ydim #: y dimensions of the grid

        self.n_cells_x = n_cells_x #: number of cells on x
        self.n_cells_y = n_cells_y #: number of cells on y
        self.units = units #: units used
        self.bc = bc #: boundary conditions, 'open' or 'close'

        self.mask = mask #: mask appplied to the tank
        if self.mask == 1:
            self.mask = np.ones_like(self.X)

        self.deep = deep #: deep of the tank, must be positive
        if self.deep < 0:
            raise(Exception('deep value must be positive.'))
        self.masked_deep = deep*self.mask #: deep on every point

        self.g = 9.8 #: gravity value
        if self.units == 'cm':
            self.g = 980
        self.speed = np.sqrt(self.g*deep) #: speed of propagation on each point

        self.dt = alpha*min(self.dx, self.dy)/self.speed #: dt value

        self.ratiox = (self.speed*self.dt/self.dx)**2 #: finite differences quotient on x
        self.ratioy = (self.speed*self.dt/self.dy)**2 #: finite differences quotient on y

        self.fig = None #: matplotlib figure
        self.ax = None #: matplotlib axes
        self.sources = [] #: stores sources
        self.masks = [] #: stores masks
        self.amplitude = None #: wave amplitude values
        self.complete_values = None #: wave amplitude + deep
        self.forbidden_pos = None #: positions where sources stand

        self.sim_duration = None #: time to simulate
        self.animation_speed = 1.0 #: relative reproduction speed
        self.fps = 24.0 #: frames per second value

        self.extent = [self.xdim[0], self.xdim[1], self.ydim[0], self.ydim[1]] #: matplotlib extent parameter

    def calcSpeed(self, values):
        """
        Calculates the propagation speed depending on the actual height of the wave.
        """
        deep = values + self.masked_deep
        speed = np.sqrt(self.g*deep)
        self.speed = speed
        # self.speed = np.sqrt(self.g*values)

    def solveBorders(self, i):
        """
        Determins the state i+1 of the boundaries using the state i.
        """
        ratiox = self.speed*self.dt/self.dx
        ratioy = self.speed*self.dt/self.dy
        self.amplitude[i+1, 0] = ratioy[0]*(self.amplitude[i, 1] - self.amplitude[i, 0]) + self.amplitude[i, 0]
        self.amplitude[i+1, -1] = -ratioy[-1]*(self.amplitude[i, -1] - self.amplitude[i, -2]) + self.amplitude[i, -1]

        self.amplitude[i+1, :, 0] = ratiox[:, 0]*(self.amplitude[i, :, 1] - self.amplitude[i, :, 0]) + self.amplitude[i, :, 0]
        self.amplitude[i+1, :, -1] = -ratioy[:, -1]*(self.amplitude[i, :, -1] - self.amplitude[i, :, -2]) + self.amplitude[i, :, -1]

    def solveInstant(self, i):
        """
        Solve the differential equation for a single instant of time, from i to i+1.
        """
        self.calcSpeed(self.amplitude[i+1])
        self.amplitude[i+1, 1:-1, 1:-1] = 2*self.amplitude[i, 1:-1, 1:-1] - self.amplitude[i-1, 1:-1, 1:-1]\
                                    + self.getSecondPartEquation(i)[1:-1, 1:-1]
        if self.bc == 'open':
            self.solveBorders(i)

        pos = self.speed == 0
        self.amplitude[i+1, pos] = 0

    def addSource(self, source):
        """
        Includes a source to the ripple tank.
        """
        self.sources += [source]
        if source.period < self.dt:
            self.setdt(0.1*source.period)

    def evaluateSources(self, i):
        """
        Evaluates all sources in the tank.

        Returns:
            np.ndarray: 2d array with the values of the source at the i instant.
        """
        initial = np.zeros_like(self.X)
        if len(self.sources) == 0:
            return initial
        for source in self.sources:
            initial = initial + source.evaluate(i)
        return initial

    def applySources(self, i):
        """
        Sets the sources values in the amplitude array of the waves.
        """
        values = self.evaluateSources(i)
        positions = self.forbidden_pos
        self.amplitude[i, positions] = values[positions] #+ self.masked_deep[positions] #self.deep
        # print(self.amplitude[i, positions])

    def getSourcesPositions(self):
        """
        Gets all the positions of the sources as a boolean array.

        Returns:
            np.ndarray: 2d boolean array.
        """
        positions = np.zeros_like(self.X, dtype=bool)
        if len(self.sources) == 0:
            return positions
        for source in self.sources:
            positions = positions + source.positions
        return positions

    def setdt(self, dt):
        """
        Sets the delta t value.
        """
        self.dt = dt
        self.ratiox = (self.speed*self.dt/self.dx)**2
        self.ratioy = (self.speed*self.dt/self.dy)**2

    def getSecondPartEquation(self, i):
        """
        Evaluates the central differences on x and y for the instant i+1.

        Returns:
            np.ndarray: 2d amplitude values at the instant i+1.
        """
        temp = np.zeros_like(self.X)
        ratiox = (self.speed*self.dt/self.dx)**2
        ratioy = (self.speed*self.dt/self.dy)**2

        if isinstance(self.speed, np.ndarray):
            ratiox = ratiox[1:-1, 1:-1]
            ratioy = ratioy[1:-1, 1:-1]
        # if (ratiox > 0.25).any() or (ratioy > 0.25).any():
        #     raise(Exception('Information transmitted faster than expected, please change alpha.'))
        temp[1:-1, 1:-1] = ratiox*(self.amplitude[i, 1:-1, :-2] - 2*self.amplitude[i, 1:-1, 1:-1] + self.amplitude[i, 1:-1, 2:])\
                    + ratioy*(self.amplitude[i, :-2, 1:-1] - 2*self.amplitude[i, 1:-1, 1:-1] + self.amplitude[i, 2:, 1:-1])

        return temp

    def simulateTime(self, sim_duration, animation_speed=1.0, fps=24.0):
        """
        Simulates an interval of time, if the animation_speed with the current fps value
        does not match the sim_duration, modifies the `dt` value.

        Returns:
            np.ndarray: 3d array, extra dimension represents time.
        """
        self.sim_duration = sim_duration
        self.animation_speed = animation_speed
        self.fps = fps

        frames = round(fps*sim_duration/animation_speed)
        required_dt = sim_duration/frames
        if required_dt < self.dt:
            self.setdt(required_dt)

        points = round(self.sim_duration/self.dt)
        return self.solvePoints(int(points))

    def solvePoints(self, n_instants):
        """
        Simulates `n_instants` of time.

        Returns:
            np.ndarray: 3d array, extra dimension represents time.
        """
        # self.amplitude = np.ones((n_instants, self.n_cells_y, self.n_cells_x)) * self.masked_deep
        self.amplitude = np.zeros((n_instants, self.n_cells_y, self.n_cells_x))
        self.amplitude[0] = self.evaluateSources(0)# + self.masked_deep
        self.amplitude[1] = self.amplitude[0] + self.getSecondPartEquation(1)# + self.masked_deep
        self.forbidden_pos = self.getSourcesPositions()

        for i in range(1, n_instants-1):
            self.solveInstant(i)
            self.applySources(i)
            self.applySources(i+1)

        self.complete_values = self.amplitude + self.masked_deep
        return self.complete_values

    def applyMask(self, frame):
        """
        Applies a numpy mask.

        Returns:
            np.ma: masked array.
        """
        if isinstance(self.mask, np.ndarray):
            return np.ma.masked_where(self.mask == 0, frame)
        return frame

    def addMask(self, mask):
        """
        Adds a mask to the ripple tank.
        """
        if isinstance(mask, Mask):
            self.masks += [mask]
        else:
            raise(Exception('Mask type is not valid.'))

    def applyMultipleMasks(self):
        """
        Calculates the whole effect of the masks by multiplying them.
        """
        if len(self.masks) > 1:
            masks = [mask.mask for mask in self.masks]
            self.mask = reduce(np.multiply, masks)
        else:
            self.mask = self.masks[0].mask
        self.masked_deep = self.mask*self.deep

    def animate(self, i, values, skip):
        """
        Function used by matplotlib's FuncAnimation.

        Returns:
            matplotlib object: imshow.
            matplotlib object: text.
        """
        i = i*skip
        temp = self.applyMask(values[i])
        self.wave_show.set_array(temp)

        t = i*self.dt
        self.time_label.set_text("%.3f s"%t)
        return self.wave_show, self.time_label,

    def configPlot(self, figsize=(6, 4.5), xlabel = None, ylabel = None, cmap = jet,
                    vmin = None, vmax = None, cbar_label = None, origin='lower'):
        """
        Configures the plot.

        Returns:
            matplotlib.figure: figure containing the main plot.
            matplotlib.axes: axes containing the imshow.
        """
        self.fig, self.ax = plt.subplots(figsize = figsize)

        if type(cmap) is str:
            exec("from matplotlib.cm import %s as cmap"%cmap, globals())
            exec("cmap.set_bad('black', 1.0)", globals())
        else:
            cmap.set_bad('black', 1.0)

        if xlabel == None:
            xlabel = "$x$ (%s)"%self.units

        if ylabel == None:
            ylabel = "$y$ (%s)"%self.units

        if cbar_label == None:
            cbar_label = "Deep (%s)"%self.units

        if type(self.amplitude) != type(None):
            binary_mask = not ((self.masked_deep > 0) & (self.masked_deep < 1)).any()
            if vmin == None:
                if binary_mask:
                    vmin = self.amplitude.min() + self.deep
                else:
                    vmin = self.complete_values.min()
            if vmax == None:
                if binary_mask:
                    vmax = self.amplitude.max() + self.deep
                else:
                    vmax = self.complete_values.max()


        self.time_label = self.ax.text(self.xdim[0] + 0.1*(self.xdim[1] - self.xdim[0]),
                    self.ydim[1] - 0.1*(self.ydim[1] - self.ydim[0]), "")
        #
        # temp = self.ax.imshow(self.mask, cmap = 'gray', origin = origin,
        #                 animated = True, extent = extent)

        self.wave_show = self.ax.imshow(np.zeros_like(self.X), cmap = cmap,
                        vmin = vmin, vmax = vmax, origin = origin, animated = True,
                        extent = self.extent)

        cbar = self.fig.colorbar(self.wave_show)
        cbar.set_label(cbar_label)
        # cbar.solids.set_edgecolor("face")

        self.ax.set_xlabel(xlabel)
        self.ax.set_ylabel(ylabel)

        return self.fig, self.ax

    def verifyData(self, data):
        """
        Verifies if parameter data is different from None. If no simulation has between
        run, simulates 100 instants of time.

        Returns:
            np.ndarray: 3d array, extra dimension represent time.
        """
        if type(data) == type(None):
            if type(self.complete_values) == type(None):
                return self.solvePoints(100)
            else:
                return self.complete_values
        return data

    def captureFrame(self, data=None, fig = None, frame=-1):
        """
        Uses the rippletank's to plot a single instant of time of `data`.

        Returns:
            matplotlib.figure: figure containing the main plot.
            matplotlib.axes: axes containing the imshow.
        """
        data = self.verifyData(data)[frame]
        if fig == None and self.fig == None:
            self.configPlot()

        self.wave_show.set_array(self.applyMask(data))
        return self.fig, self.ax

    def makeAnimation(self, data=None, fig = None, fps = None, duration = None):
        """
        Makes an animation of `data`, it only uses the required frames depending
        on the duration and fps value.

        Returns:
            matplotlib.animation.FuncAnimation: animation of the data.
        """
        data = self.verifyData(data)

        if fps == None:
            fps = self.fps
        else:
            self.fps = fps

        if duration == None:
            if self.sim_duration != None:
                duration = self.sim_duration
            else:
                duration = 10
        else:
            self.sim_duration = duration

        skip = self.animation_speed*data.shape[0]/(fps*duration)
        skip = round(skip)
        if skip == 0:
            skip = 1

        if fig == None and self.fig == None:
            self.configPlot()

        ani = FuncAnimation(self.fig, self.animate, frames = data.shape[0]//skip,
                interval=50, fargs=(data, skip), blit=True)

        return ani

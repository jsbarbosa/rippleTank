import numpy as np
from .masks import getPositions

class Source():
    """
    Sources create perturbations on the ripple tank.
    """
    def __init__(self, rippletank, function, xcorners = (-0.5, 0.5), ycorners=(-0.5, 0.5), freq = 1, phase = 0, amplitude = 0.1):

        self.rippletank = rippletank #: parent tank
        self.X_grid = rippletank.X #: x grid coordinates
        self.Y_grid = rippletank.Y #: y grid coordinates
        self.xcorners = xcorners #: xcorners of the source
        self.ycorners = ycorners #: ycorners of the source

        self.freq = freq #: frequency of the source
        self.period = 1.0/freq #: period of the source
        self.phase = phase #: phase of the source

        self.function = function #: function that describes source behavior
        self.positions = getPositions(self.X_grid, self.Y_grid, self.xcorners, self.ycorners) #: position of the source

        if amplitude < 0 or amplitude > 1:
            raise(Exception("Amplitude is not valid"))
        self.amplitude = amplitude #: relative amplitude of the source

        self.rippletank.addSource(self)

    def evaluate(self, i):
        """
        Receives an int number related with an iterator, evaluates `function` using that number.

        Returns:
            np.ndarray: source values.
        """
        answer = self.function(self, i)
        if type(answer) == type(None):
            return np.zeros_like(self.X_grid)
        return answer*self.amplitude*self.rippletank.deep

def dropSource(source, i):
    """
    Pulse function.

    Returns:
        np.ndarray: array with -1.0 values on source positions.
    """
    t = source.rippletank.dt*i
    if t != 0:
        return None

    answer = np.zeros_like(source.X_grid)
    answer[source.positions] = -1.0
    return answer

def sineSource(source, i):
    """
    Sine function.

    Returns:
        np.ndarray: array with sine values on source positions.
    """
    t = source.rippletank.dt*i
    answer = np.zeros_like(source.X_grid)
    value = np.sin(2*np.pi*source.freq*t + source.phase)
    # if value < 0:
    #     answer[source.positions] = value
    # else:
    #     # return None

    answer[source.positions] = value
    return answer

def squareSource(source, i):
    """
    Square function.

    Returns:
        np.ndarray: array with square values on source positions.
    """
    answer = sineSource(source, i)
    answer[answer > 0] = 1.0
    answer[answer < 0] = -1.0

    return answer

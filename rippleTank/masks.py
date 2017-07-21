import sys
import numpy as np

if sys.version_info[0] >= 3:
    from functools import reduce

class Mask():
    """
    Masks represent obstacules on the ripple tank. Depending on the `rel_deep`
    they can be seen as barriers (`rel_deep=0`) or simply objects that vary the deep of the tank.
    """
    def __init__(self, rippletank, rel_deep = None):
        self.rippletank = rippletank #: parent Tank object
        self.rippletank.addMask(self)

        self.rel_deep = rel_deep #: relative deep of the mask
        self.mask = np.ones_like(self.rippletank.X) #: mask array

    def fromFunc(self, func, args = (), kwargs = {}):
        """
        Mask array can be made by calling a function `func`, the first argument of the
        function needs to be the mask object, other arguments are send to the function
        with the `args` parameter, and the keyword arguments with `kwargs`.
        """
        self.mask = func(self, *args, **kwargs)
        if type(self.rel_deep) != type(None):
            self.mask[self.mask == 0] = self.rel_deep

        self.applyMask()

    def fromArray(self, array, rel_deep = None):
        """
        Mask array can assigned with and incoming 2d array.
        The array must have the same dimensions of the ripple tank, contain ones
        where no effect is wanted and zeros where the deep wants to be modified.
        If the mask object has a `rel_deep` or a value is set by parameter,
        zeros will be changed to `rel_deep`.

        Raises:
            Exception: "Input array does not have the ripple tank dimensions."
            Exception: "Deep must be between 0 and 1."
        """
        if array.shape != self.rippletank.X.shape:
            raise(Exception("Input array does not have the ripple tank dimensions."))
        self.mask = array
        if type(rel_deep) != type(None):
            self.rel_deep = rel_deep
        if type(self.rel_deep) != type(None):
            self.mask[self.mask == 0] = self.rel_deep
        if self.mask.max() > 1 or self.mask.min() < 0:
            raise(Exception("Deep must be between 0 and 1."))
        self.applyMask()

    def applyMask(self):
        """
        Applies the mask object to the `rippletank`.
        """
        self.rippletank.applyMultipleMasks()

    def __sum__(self, other):
        return self.mask + other

    def __sub__(self, other):
        return self.mask - other

    def __mul__(self, other):
        return self.mask * other

    def __rsum__(self, other):
        return self.mask + other

    def __rsub__(self, other):
        return self.mask - other

    def __rmul__(self, other):
        return self.mask * other

def getPositions(X_grid, Y_grid, xcorners, ycorners):
    """
    Using the coordinates in `X_grid` and `Y_grid` returns a 2d boolean array
    of a rectangle with `xcorners` and `ycorners`.

    Returns:
        np.ndarray: 2d boolean array.
    """
    xconditions = (X_grid >= min(xcorners)) & (X_grid <= max(xcorners))
    yconditions = (Y_grid >= min(ycorners)) & (Y_grid <= max(ycorners))
    return xconditions*yconditions

def circleMask(mask, x0, y0, r, width = 1):
    """
    Draws a circle centered on `x0, y0` with radious `r` and `width`. Background
    is made with ones and the circle with zeros.

    Returns:
        np.ndarray: 2d binary array.
    """
    X_grid, Y_grid = mask.rippletank.X, mask.rippletank.Y
    mask = np.ones_like(X_grid)
    R = np.sqrt((X_grid-x0)**2 + (Y_grid-y0)**2)
    mask[(R <= r) & (R > (r-width))] = 0

    return mask

def rectangleMask(mask, xcorners, ycorners):
    """
    Draws a rectangle with `xcorners` and `ycorners`. Background
    is made with ones and the rectangle with zeros.

    Returns:
        np.ndarray: 2d binary array.
    """
    X_grid, Y_grid = mask.rippletank.X, mask.rippletank.Y
    mask = np.ones_like(X_grid)

    positions = getPositions(X_grid, Y_grid, xcorners, ycorners)
    mask[positions] = 0
    return mask

def singleSlit(mask, xcorners, ycorners, width = -1, on = 'x'):
    """
    Draws a slit on the middle of a rectangle with `xcorners`, `ycorners` with `width`
    on the `on` direction. The `on` parameter can be: `x`, `y`, `X`, `Y`.

    Background is made with ones and the slit with zeros.

    Raises:
        Exception: "on is not a valud location."

    Returns:
        np.ndarray: 2d binary array.
    """
    posible_ons = ['x', 'X', 'y', 'Y']
    if not on in posible_ons:
        raise(Exception("'%s' is not a valid location."%on))

    middleX = sum(xcorners)/2.0
    middleY = sum(ycorners)/2.0
    if width == -1:
        if on in posible_ons[:2]:
            width = max(xcorners) - min(xcorners)
        else:
            width = max(ycorners) - min(ycorners)
        width *= 0.05

    X_grid, Y_grid = mask.rippletank.X, mask.rippletank.Y
    if on in posible_ons[:2]:
        first = rectangleMask(mask, (min(xcorners), middleX-width), ycorners)
        second = rectangleMask(mask, (middleX+width, max(xcorners)), ycorners)

    else:
        first = rectangleMask(mask, xcorners, (min(ycorners), middleY-width))
        second = rectangleMask(mask, xcorners, (middleY+width, max(ycorners)))

    return first*second

def halfCircleMask(mask, x0, y0, r, width=1, on="x", direction="upper"):
    """
    Draws half a circle centered on `x0, y0` with radious `r`, and `width`.
    The direction is set with the `on` parameter. The `direction` parameter tells where to point the half circle.
    The `on` parameter can be: `x`, `y`, `X`, `Y`. The `direction` parameter: `upper`, `lower`.

    Background is made with ones and the slit with zeros.

    Raises:
        Exception: "on is not a valud location."

        Exception: "direction is not a valud direction."

    Returns:
        np.ndarray: 2d binary array.
    """
    posible_ons = ['x', 'X', 'y', 'Y']
    posible_directions = ['upper', 'lower']
    if not on in posible_ons:
        raise(Exception("'%s' is not a valid location."%on))
    if not direction in posible_directions:
        raise(Exception("'%s' is not a valid direction."%upper))

    X_grid, Y_grid = mask.rippletank.X, mask.rippletank.Y
    mask = circleMask(mask, x0, y0, r, width)

    if on in posible_ons[:2]:
        if direction == 'upper':
            r = getPositions(X_grid, Y_grid, (X_grid.min(), X_grid.max()), (y0, Y_grid.max()))
            mask[r] = 1.0
        else:
            r = getPositions(X_grid, Y_grid, (X_grid.min(), X_grid.max()), (Y_grid.min(), y0))
            mask[r] = 1.0
    else:
        if direction == 'upper':
            r = getPositions(X_grid, Y_grid, (X_grid.min(), x0), (Y_grid.min(), Y_grid.max()))
            mask[r] = 1.0
        else:
            r = getPositions(X_grid, Y_grid, (x0, X_grid.max()), (Y_grid.min(), Y_grid.max()))
            mask[r] = 1.0
    return mask

def doubleSlit():
    pass

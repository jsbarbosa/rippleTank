import numpy as np
import rippleTank as rt
import matplotlib.pyplot as plt

# creates a ripple tank
tank = rt.RippleTank((-50, 50), (-50, 50), units='m')

# creates a source on the ripple tank
rt.Source(tank, rt.sineSource, xcorners = (-50, 50), ycorners = (25, 30), freq= 2/15.0)

# creates rectangular masks fom function
rt.Mask(tank).fromFunc(rt.rectangleMask,  ((0, 3), (-50, -20)) )
rt.Mask(tank).fromFunc(rt.rectangleMask, ((25, 28), (-50, -20)) )

x = np.linspace(0, 1, tank.X.shape[1])
y = np.linspace(0, 1, tank.X.shape[0])

X, Y = np.meshgrid(x, y)

# creates ocean floor
rt.Mask(tank).fromArray(Y)

tank.simulateTime(60.0, animation_speed=10.0)

ani = tank.makeAnimation()
# ani.save('breakwater.gif', writer='imagemagick')

plt.show()

import rippleTank as rt
import matplotlib.pyplot as plt

# creates a ripple tank
tank = rt.RippleTank(bc='close')

# creates a source on the ripple tank
rt.Source(tank, rt.sineSource, xcorners = (-tank.dx, tank.dx),
                                        ycorners = (10-tank.dy, 10+tank.dy), freq = 10.0)

width = (tank.dx**2 + tank.dy**2)**0.5
rt.Mask(tank).fromFunc(rt.halfCircleMask, (0, -4, 6, width, 'x', 'lower'))

tank.simulateTime(2.0, animation_speed=0.5)

ani = tank.makeAnimation()
# ani.save('halfCircle.gif', writer='imagemagick')

plt.show()

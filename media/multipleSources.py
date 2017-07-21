import rippleTank as rt
import matplotlib.pyplot as plt

# creates a ripple tank
tank = rt.RippleTank()

x0, y0 = -5, 0
# creates a source on the ripple tank
rt.Source(tank, rt.sineSource, xcorners = (x0-tank.dx, x0+tank.dx),
                                        ycorners = (y0-tank.dy, y0+tank.dy), freq = 10.0)
x1, y1 = 5, 0
rt.Source(tank, rt.sineSource, xcorners = (x1-tank.dx, x1+tank.dx),
                                        ycorners = (y1-tank.dy, y1+tank.dy), freq = 5.0)

tank.simulateTime(2.0, animation_speed=0.5)

ani = tank.makeAnimation()
# ani.save('multipleSources.gif', writer='imagemagick')

plt.show()

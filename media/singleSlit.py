import rippleTank as rt
import matplotlib.pyplot as plt

# creates a ripple tank
tank = rt.RippleTank()

# creates a source on the ripple tank
rt.Source(tank, rt.sineSource, xcorners = (-15, 15), ycorners = (10, 11), freq = 10.0)

rt.Mask(tank).fromFunc(rt.singleSlit, ((-15, 15), (0, tank.dy)))

tank.simulateTime(2.0, animation_speed=0.5)

ani = tank.makeAnimation()
# ani.save('singleSlit.gif', writer='imagemagick')

plt.show()

import rippleTank as rt
import matplotlib.pyplot as plt

# creates a ripple tank
tank = rt.RippleTank()

# creates a source on the ripple tank
rt.Source(tank, rt.sineSource, freq=10)

tank.simulateTime(2.0, animation_speed = 0.5)

ani = tank.makeAnimation()
# ani.save('simpleSource.gif', writer='imagemagick')

plt.show()

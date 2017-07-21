from rippleTank import *

tank = RippleTank()
mask = Mask(tank, 0)
mask.fromFunc(rectangleMask, ((-10, 10), (-10, 10)))

plt.xkcd()
fig = plt.figure()
plot = plt.imshow(mask.mask, extent = tank.extent)

plt.text(-2, 0, "mask")
plt.text(-4, -12, "background")
plt.colorbar(plot)

plt.xlabel('x (cm)')
plt.ylabel('y (cm)')
plt.tight_layout()
plt.savefig('mask.png')
# plt.show()

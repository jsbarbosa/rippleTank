from rippleTank import *

tank = RippleTank()
n = int(round(1/tank.dt))
source_drop = Source(tank, dropSource)
source_sine = Source(tank, sineSource)
source_square = Source(tank, squareSource)

drop = np.zeros(n)
sine = np.zeros(n)
square = np.zeros(n)
t = np.arange(0, n)*tank.dt
for i in range(n):
    drop[i] = source_drop.evaluate(i)[source_drop.positions].mean()
    sine[i] = source_sine.evaluate(i)[source_sine.positions].mean()
    square[i] = source_square.evaluate(i)[source_square.positions].mean()

plt.xkcd()
fig = plt.figure()
plt.plot(t, drop/source_drop.amplitude, label='drop')
plt.plot(t, sine/source_sine.amplitude, label='sine')
plt.plot(t, square/source_square.amplitude, label='square')

plt.ylabel('$f(t)/$amplitude')
plt.xlabel('$t/$period')
plt.legend()

plt.tight_layout()
plt.savefig('sources.png')
# plt.show()

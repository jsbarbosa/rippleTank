import numpy as np
import matplotlib.pyplot as plt

x = y = np.linspace(-2, 2, 10)
X, Y = np.meshgrid(x, y)

T = np.exp(-X**2 -Y**2)

T1 = T.copy()
T2 = T.copy()

T1[1:-1, 1:-1] = T[1:-1, 1:-1] + (T[1:-1, 2:] - 2*T[1:-1, 1:-1] + T[1:-1, :-2]) + (T[2:, 1:-1] - 2*T[1:-1, 1:-1] + T[:-2, 1:-1])
T2[1:-1, 1:-1] = 2*T1[1:-1, 1:-1] - T[1:-1, 1:-1] + (T1[1:-1, 2:] - 2*T1[1:-1, 1:-1] + T1[1:-1, :-2]) + (T1[2:, 1:-1] - 2*T1[1:-1, 1:-1] + T1[:-2, 1:-1])

T1[0] = (T[1] - T[0]) + T[0]
T1[-1] = -(T[-1] - T[-2]) + T[-1]
T1[:, 0] = (T[:, 1] - T[:, 0]) + T[:, 0]
T1[:, -1] = -(T[:, -1] - T[:, -2]) + T[:, -1]

T2[0] = (T1[1] - T1[0]) + T1[0]
T2[-1] = -(T1[-1] - T1[-2]) + T1[-1]
T2[:, 0] = (T1[:, 1] - T1[:, 0]) + T1[:, 0]
T2[:, -1] = -(T1[:, -1] - T1[:, -2]) + T1[:, -1]

plt.xkcd()

fig, axes = plt.subplots(1, 3, figsize=(16, 6))
titles = ['t-1', 't', 't+1']
data = [T, T1, T2]

for i in range(len(axes)):
    ax = axes[i]
    title = titles[i]
    t = data[i]

    ax.imshow(t, cmap='jet', vmin=-1, vmax=1)
    ax.set_ylabel('i')
    ax.set_xlabel('j')
    ax.set_title(title)
    ax.grid()

    ax.set_xticks(np.arange(-.5, 10, 1));
    ax.set_yticks(np.arange(-.5, 10, 1));
    ax.set_xticklabels(np.arange(0, 11, 1));
    ax.set_yticklabels(np.arange(0, 11, 1));

plt.tight_layout()
plt.savefig('finitedifferences.png')
# plt.show()

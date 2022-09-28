from itertools import cycle

import matplotlib
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('simdurations.csv')

fig, ax = plt.subplots()
N, bins, patches = ax.hist(
    df['SimDurationInSecs'],
    edgecolor='black',
    linewidth=1,
    bins=[0, 30, 60, 120, 200, 300, 400, 500, 700, 850, 1000, 1250, 1500, 2000, 2500, 3000, 3500, 4000]
)


fig.set_figwidth(20)
fig.set_figheight(10)
colors = cycle(['b', 'g', 'r', 'c', 'm', 'y', 'k'])
for i in range(len(patches) - 1):
    patches[i].set_facecolor(next(colors))
plt.xticks([0, 30, 60, 120, 200, 300, 400, 500, 700, 850, 1000, 1250, 1500, 2000, 2500, 3000, 3500, 4000], rotation=90)
plt.show()

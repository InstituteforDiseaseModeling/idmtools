import os
import sys

import pandas as pd

CURRENT_DIRECTORY = os.path.dirname(__file__)
LIBRARY_PATH = os.path.join(CURRENT_DIRECTORY, 'site_packages')  # Need to site_packages level!!!

sys.path.insert(0, LIBRARY_PATH)  # Very Important!
import seaborn as sns  # noqa

# Load the data
tips = pd.read_csv("./Assets/tips.csv")

# Create violinplot
sns_plot = sns.violinplot(x="total_bill", data=tips)

# Show the plot
fig = sns_plot.get_figure()
fig.savefig("tips.png")

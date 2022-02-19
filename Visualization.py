import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import pearsonr
import plotly.express as px

# load csv
df = pd.read_csv("addingBeaufort.csv", header=0, sep=',')
print(df)

# storm location map graph
fig = px.scatter_geo(df, lat='lat', lon='long',
                     color=df['beaufort_scale'])
fig.update_layout(title='Locations of storms by lat and long records',
                  title_x=0.5,
                  geo_scope='world')
fig.update_traces(marker=dict(size=3))
fig.show()

# pie chart and hist
ig = df['Ocean'].value_counts().sort_values().plot(kind='pie', autopct="%.2f%%")
plt.ylabel("")
fig.set_title("Amount records by Ocean", fontsize=20)


# hist by month
def histPerMonth(df):
    fig = df['Month'].hist()
    fig.set_title("Storms anount by month", fontsize=20)
    fig.set_xlabel("month")
    fig.set_ylabel("Records")

    fig = df[df['Ocean'] == 'Atlantic Ocean']['Month'].hist()
    plt.suptitle("Atlantic Ocean's storms per month", fontsize=20)
    fig = df[df['Ocean'] == 'Western Pacific']['Month'].hist()
    plt.suptitle("Western Pacific's storms per month", fontsize=20)
    fig = df[df['Ocean'] == 'East Pacific']['Month'].hist()
    plt.suptitle("East Pacific's storms per month", fontsize=20)
    fig = df[df['Ocean'] == 'Central Pacific']['Month'].hist()
    plt.suptitle("Central Pacific's storms per month", fontsize=20)
    fig = df[df['Ocean'] == 'Southern Hemisphere']['Month'].hist()
    plt.suptitle("Southern Hemisphere's storms per month", fontsize=20)
    fig = df[df['Ocean'] == 'Indian Ocean']['Month'].hist()
    plt.suptitle("Indian Ocean's storms per month", fontsize=20)


# mean wind power by ocean
fig = df.groupby(['Ocean']).mean()['wind_power'].plot(kind='bar')
fig.set_ylabel("Wind Power")
fig.set_title("Mean Wind Power by ocean", fontsize=20)
# scatter plot - wind power and air pressure
fig = plt.figure()
ax = plt.axes()
x = df.air_pressure
y = df.wind_power
ax.scatter(df.air_pressure, df.wind_power, linewidths=0.1)
plt.xlabel('air pressure')
plt.ylabel('wind power')
plt.suptitle("Correlation between air pressure and wind power", fontsize=20)
# draw cross linear line
m, b, _ = np.polyfit(x, y, 1)
plt.plot(x, m * x + b, c='black')
plt.show()
# Pearson correlation coefficient
corr, _ = pearsonr(df.air_pressure, df.wind_power)
print(corr)

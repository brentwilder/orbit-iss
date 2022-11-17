import pytz
import plotly.express as px
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
from skyfield.api import load, wgs84, EarthSatellite

ts = load.timescale()
#https://space.stackexchange.com/questions/58268/satellite-ground-track-calculation
# Updated version of the listed two-line elements
line1 = '1 25544U 98067A   22078.05453850  .00006165  00000+0  11806-3 0  9995'
line2 = '2 25544  51.6427  62.9786 0003909 284.2254 162.3984 15.49468773331209'
satellite = EarthSatellite(line1, line2, 'ISS (ZARYA)', ts)
print(satellite)

# Get the current time in a timezone-aware fashion.
tz = pytz.timezone('UTC')
dt = tz.localize(datetime.utcnow())
print(f"Exectution time: {dt:%Y-%m-%d %H:%M:%S %Z}\n")

# spaced Timescales (every two minutes, plus endpoints)
t0 = ts.utc(dt)
t1 = ts.utc(dt + relativedelta(minutes=43800))
timescales = ts.linspace(t0, t1, 1000000)

# calculate the subpoints.
geocentrics = satellite.at(timescales)
subpoints = wgs84.subpoint_of(geocentrics)

data = [timescales.astimezone(tz),subpoints.latitude.degrees,  subpoints.longitude.degrees]

df= pd.DataFrame({'Date': data[0], 'Lat': data[1], 'Lon': data[2]})

df['Hour'] = pd.to_datetime(df['Date']).dt.hour
df['Day'] = pd.to_datetime(df['Date']).dt.day

df = df[(df.Lat >= 40) & (df.Lat <= 45)]
df = df[(df.Lon >= -121) & (df.Lon <= -112)]
df = df[(df.Hour >= 16) & (df.Hour <= 22)]

df.to_csv(f'./data/ISS_{dt}.csv')

color_scale = [(0, 'orange'), (1,'red')]

fig = px.scatter_mapbox(df, 
                        lat='Lat', 
                        lon='Lon', 
                        hover_name='Date', 
                        hover_data=['Date','Lat','Lon'],
                        color='Day',
                        color_continuous_scale=color_scale,
                        zoom=6, 
                        height=800,
                        width=1200)

fig.update_layout(mapbox_style='stamen-terrain')
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
fig.show()
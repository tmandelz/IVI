# %%
import pandas as pd
import geopandas as gpd
import plotly.express as px
from dash_extensions.enrich import DashProxy, MultiplexerTransform
from dash import dcc, html
import os
import flask

dirname = os.path.dirname(__file__)
magnitudePath = os.path.join(
    dirname, './Plots/Plot_2/magnitude.csv')
CountryshapefilePath = os.path.join(
    dirname, './Shapefiles/ne_50m_admin_0_countries.shp')

# %%
df_countries = pd.read_csv(magnitudePath, delimiter=';', usecols=[
                           'GRID_NO', 'DAY', 'magnitude', 'geometry_y', 'country'])

df_countries['DAY'] = pd.to_datetime(df_countries['DAY'])

# %%
df_countries['geometry_y'] = gpd.GeoSeries.from_wkt(df_countries['geometry_y'])

# %%
df_countriesKosovo = df_countries[df_countries["country"] == "Kosovo"]
df_countriesKosovo = df_countries[df_countries["DAY"].dt.year == 1979]

shapefile_country = gpd.read_file(CountryshapefilePath).rename(
    columns={"SOVEREIGNT": "country"}).loc[:, ["geometry", "country"]]
shapefile_countryKosovo = shapefile_country[shapefile_country["country"] == "Kosovo"]
shapefile_countryKosovo = gpd.GeoDataFrame(
    shapefile_countryKosovo, geometry="geometry")

mergedf = gpd.GeoDataFrame(
    df_countriesKosovo, geometry="geometry_y", crs='epsg:4326')


# %%
Kosovodf = mergedf.overlay(shapefile_countryKosovo, how="intersection")
# %%
fig = px.choropleth(Kosovodf, geojson=Kosovodf.geometry,
                    locations=Kosovodf.index,
                    color="magnitude",
                    color_continuous_scale=px.colors.sequential.Blues,
                    scope="europe",
                    title= "Kosovo" +"<br><sup>Magnitude pro 25 x 25km Feld im Jahr "+str(1996) +"</sup>",
                    range_color=(0, 3),
                    height=768,
                    width=1024,
                    labels={'magnitude': 'Magnitude'},
                    )
fig.update_geos(fitbounds="locations", visible=False)

#%%
server = flask.Flask(__name__)

app = DashProxy(server=server,prevent_initial_callbacks=True,
                transforms=[MultiplexerTransform()])
app.layout = html.Div([
    dcc.Graph(figure=fig, id="country")
])

if __name__ == '__main__':
    app.run_server(host="127.0.0.1", debug=True)
# %%

from dash import dcc, html, Dash, callback
import dash
from dash.dependencies import Input, Output
import json
import plotly.express as px
import pandas as pd
import rasterio
from rasterio.plot import show
from rasterio.enums import Resampling
import numpy as np
from dash.exceptions import PreventUpdate
import xml.etree.ElementTree as ET
from fastkml import kml
from shapely.geometry import Polygon, Point
import dash_bootstrap_components as dbc

# app = dash.Dash(__name__)
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Load JSON data
with open('20231121_061209_SN28_L1_SR_MS_toa_factors.json') as f:
    toa_factors = json.load(f)

with open('20231121_061209_SN28_L1_SR_MS_metadata_stac.geojson') as f1:
    metadata_stac = json.load(f1)

with open('20231121_061209_SN28_L1_SR_MS_solar_and_viewing_angles.geojson') as f2:
    solar_viewing_angles = json.load(f2)

def extract_coordinates(features):
    coords = []
    for feature in features:
        geom_type = feature['geometry']['type']
        if geom_type == 'Point':
            # For points, just append the coordinates
            coords.append(feature['geometry']['coordinates'])
        elif geom_type in ['Polygon', 'LineString']:
            # For polygons and linestrings, take the first set of coordinates (change this as needed for your data)
            coords.append(feature['geometry']['coordinates'][0][0])
        else:
            raise ValueError(f"Unsupported geometry type: {geom_type}")
    return coords

# Process GeoJSON for Plotly
features = toa_factors['features']
data = {
    'coords': extract_coordinates(toa_factors['features'])
}
df = pd.DataFrame(data)
df[['lon', 'lat']] = pd.DataFrame(df['coords'].tolist(), index=df.index)

features2 = metadata_stac['features']
data2 = {
    'coords': extract_coordinates(metadata_stac['features'])
}
df2 = pd.DataFrame(data2)
df2[['lon', 'lat']] = pd.DataFrame(df2['coords'].tolist(), index=df2.index)

features3 = solar_viewing_angles['features']
data3 = {
    'coords': extract_coordinates(solar_viewing_angles['features'])
}
df3 = pd.DataFrame(data3)
df3[['lon', 'lat']] = pd.DataFrame(df3['coords'].tolist(), index=df3.index)

mapbox_access_token = 'pk.eyJ1Ijoic2FsbWFzeWRuZWV5IiwiYSI6ImNsdTlxNnoyejBkM2Mya3Flbm14bWk0a3QifQ.-_gvmsDiL3_4OVIKJRlZ9w'
# Create the figure using the processed data
fig = px.scatter_mapbox(df, lat='lat', lon='lon', 
                        title="TOA Factors Visualization",
                        mapbox_style="mapbox://styles/mapbox/satellite-streets-v11",
                        center={"lat": df.lat.mean(), "lon": df.lon.mean()},
                        zoom=1)
fig_metadata_stac = px.scatter_mapbox(df2, lat='lat', lon='lon',
                                      title="Metadata STAC Visualization",
                                      mapbox_style="mapbox://styles/mapbox/satellite-streets-v11",
                                      center={"lat": df2.lat.mean(), "lon": df2.lon.mean()},
                                      zoom=1)
fig_solar_viewing_angles = px.scatter_mapbox(df3, lat='lat', lon='lon',
                                             title="Solar and Viewing Angles Visualization",
                                             mapbox_style="mapbox://styles/mapbox/satellite-streets-v11",
                                             center={"lat": df3.lat.mean(), "lon": df3.lon.mean()},
                                             zoom=1)
# fig.update_layout(title_x=0.5)  # Centering the title of the figure
# fig.update_layout(mapbox_accesstoken=mapbox_access_token)
# fig_metadata_stac.update_layout(mapbox_accesstoken=mapbox_access_token, title_x=0.5)
# fig_solar_viewing_angles.update_layout(mapbox_accesstoken=mapbox_access_token, title_x=0.5)
fig_styles = {'title_x': 0.5, 'mapbox_accesstoken': mapbox_access_token}
fig.update_layout(**fig_styles, mapbox_style="outdoors")
fig_metadata_stac.update_layout(**fig_styles, mapbox_style="outdoors")
fig_solar_viewing_angles.update_layout(**fig_styles, mapbox_style="outdoors")

# Dashboard layout
app.layout = html.Div([
    html.Div([
        dcc.Graph(id='map-toa', figure=fig),
        html.Button('Show Coordinates', id='btn-toa', style={'display': 'block', 'margin-left': 'auto', 'margin-right': 'auto'}),
        html.Pre(id='display-toa', style={'display': 'none'})
    ], style={'text-align': 'center'}),
    html.Div([
        dcc.Graph(id='map-metadata-stac', figure=fig_metadata_stac),
        html.Button('Show Coordinates', id='btn-metadata-stac', style={'display': 'block', 'margin-left': 'auto', 'margin-right': 'auto'}),
        html.Pre(id='display-metadata-stac', style={'display': 'none'})
    ], style={'text-align': 'center'}),
    html.Div([
        dcc.Graph(id='map-solar-viewing', figure=fig_solar_viewing_angles),
        html.Button('Show Coordinates', id='btn-solar-viewing', style={'display': 'block', 'margin-left': 'auto', 'margin-right': 'auto'}),
        html.Pre(id='display-solar-viewing', style={'display': 'none'})
    ], style={'text-align': 'center'}),
])

fig_styles = {'title_x': 0.5, 'mapbox_accesstoken': mapbox_access_token}
fig.update_layout(**fig_styles, mapbox_style="outdoors")
fig_metadata_stac.update_layout(**fig_styles, mapbox_style="outdoors")
fig_solar_viewing_angles.update_layout(**fig_styles, mapbox_style="outdoors")

# Dashboard layout with more color and using Dash Bootstrap Components
app.layout = dbc.Container([
    dbc.Row(dbc.Col(html.H1("Visualization Dashboard", className="text-center text-primary mb-4"), width=12)),
    dbc.Row([
        dbc.Col(dcc.Graph(id='map-toa', figure=fig), md=4),
        dbc.Col(dcc.Graph(id='map-metadata-stac', figure=fig_metadata_stac), md=4),
        dbc.Col(dcc.Graph(id='map-solar-viewing', figure=fig_solar_viewing_angles), md=4),
    ]),
    dbc.Row([
        dbc.Col(html.Button('Show Coordinates', id='btn-toa', className="btn btn-secondary"), md=4),
        dbc.Col(html.Button('Show Coordinates', id='btn-metadata-stac', className="btn btn-secondary"), md=4),
        dbc.Col(html.Button('Show Coordinates', id='btn-solar-viewing', className="btn btn-secondary"), md=4),
    ]),
    dbc.Row([
        dbc.Col(html.Pre(id='display-toa', style={'display': 'none'}), md=4),
        dbc.Col(html.Pre(id='display-metadata-stac', style={'display': 'none'}), md=4),
        dbc.Col(html.Pre(id='display-solar-viewing', style={'display': 'none'}), md=4),
    ])
], fluid=True)

@app.callback(
    [Output('display-toa', 'children'),
     Output('display-toa', 'style'),
     Output('display-metadata-stac', 'children'),
     Output('display-metadata-stac', 'style'),
     Output('display-solar-viewing', 'children'),
     Output('display-solar-viewing', 'style')],
    [Input('btn-toa', 'n_clicks'),
     Input('btn-metadata-stac', 'n_clicks'),
     Input('btn-solar-viewing', 'n_clicks')],
    prevent_initial_call=True
)
def display_data(btn_toa, btn_metadata_stac, btn_solar_viewing):
    ctx = dash.callback_context

    if not ctx.triggered:
        # No button has been clicked yet
        return "", {'display': 'none'}, "", {'display': 'none'}, "", {'display': 'none'}
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    # Initialize the styles to 'none' each time, will show if the conditions below are met
    style_toa = {'display': 'none'}
    style_metadata_stac = {'display': 'none'}
    style_solar_viewing = {'display': 'none'}
    
    # Initialize the data to empty each time, will update if the conditions below are met
    data_toa = ""
    data_metadata_stac = ""
    data_solar_viewing = ""
    
    if button_id == 'btn-toa' and btn_toa and btn_toa % 2:
        style_toa = {'display': 'block'}
        data_toa = json.dumps(extract_coordinates(toa_factors['features']), indent=2)
    
    if button_id == 'btn-metadata-stac' and btn_metadata_stac and btn_metadata_stac % 2:
        style_metadata_stac = {'display': 'block'}
        data_metadata_stac = json.dumps(extract_coordinates(metadata_stac['features']), indent=2)
    
    if button_id == 'btn-solar-viewing' and btn_solar_viewing and btn_solar_viewing % 2:
        style_solar_viewing = {'display': 'block'}
        data_solar_viewing = json.dumps(extract_coordinates(solar_viewing_angles['features']), indent=2)
    
    return data_toa, style_toa, data_metadata_stac, style_metadata_stac, data_solar_viewing, style_solar_viewing


if __name__ == '__main__':
    app.run_server(debug=True)
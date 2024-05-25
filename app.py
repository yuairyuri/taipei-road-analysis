from dash import Dash, dcc, html, Input, Output, callback
from io import StringIO
import time
import json
import pandas as pd
import geopandas as gpd
import plotly.graph_objects as go

from sklearn.cluster import KMeans

app = Dash(__name__)

app.layout = html.Div([
    html.H1("Visualizing Clustering Results"),
    html.Div(className='container', children=[
        html.Div(className='left', children=[
            html.Div(className='controller', children=[
                html.P("Select the Number of Clusters"),
                dcc.Slider(2, 8, 1, value=3, id='k-range'),
                html.P("Select Cluster"),
                dcc.Dropdown(id='cluster', multi=True)
            ]),
            html.Div(className='chart', children=[
                dcc.Graph(figure={}, id='radar-chart')
            ])
        ]),
        html.Div(className='right', children=[
            dcc.Graph(figure={}, id='road')
        ])
    ]),
    dcc.Store(id='label')
])

@app.callback(
    Output('cluster', 'options'),
    Input('k-range', 'value')
)
def select_cluster(k_value):
    options = [i for i in range(k_value)]
    return options

@app.callback(
    Output('label', 'data'),
    Input('k-range', 'value')
)
def clustering(k_value):
    df = pd.read_csv("./data/major_road_data.csv").set_index('OBJECTID')
    X = df.iloc[:, 1:]
    kmeans = KMeans(n_clusters=k_value, random_state=31).fit(X)
    df['cluster_id'] = kmeans.labels_
    return df.reset_index().to_json(orient='index')

@app.callback(
    Output('radar-chart', 'figure'),
    Input('label', 'data')
)
def show_features(data):
    fig = go.Figure()
    time.sleep(1)
    labeled_df = pd.read_json(StringIO(data), orient='index').set_index('OBJECTID')
    X = labeled_df.iloc[:, 1:-1]
    for i in labeled_df['cluster_id'].unique():
        fig.add_trace(go.Scatterpolar(
            r=labeled_df.groupby('cluster_id').median().iloc[i, 1:],
            theta=X.columns,
            fill='toself',
            name=str(i)
        ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )
        ),
    )
    return fig

@app.callback(
    Output('road', 'figure'),
    Input('label', 'data'),
    Input('cluster', 'value')
)
def draw_road(data, selected_cluster):
    labeled_df = pd.read_json(StringIO(data), orient='index')
    road_gdf = gpd.read_file("./data/roads.geojson").to_crs(4326)
    road_gdf = road_gdf.merge(labeled_df, on='OBJECTID').set_index('OBJECTID')
    fig = go.Figure(go.Choroplethmapbox(
        geojson=json.loads(road_gdf.geometry.to_json()),
        locations=road_gdf.index,
        z=road_gdf['cluster_id']
    ))
    fig.update_layout(
        mapbox_style="carto-positron",
        mapbox_zoom=12,
        mapbox_center={"lat": 25.0375, "lon": 121.5625}
    )
    fig.update_layout(
        height=750,
        margin={'r': 16, 't': 16, 'l': 16, 'b': 16}
    )
    return fig

if __name__ == '__main__':
    app.run(debug=True)
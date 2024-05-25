from dash import Dash, dcc, html, Input, Output, callback, ctx
from io import StringIO
import time
import json
import pandas as pd
import geopandas as gpd
import plotly.graph_objects as go
import plotly.express as px

from sklearn.cluster import KMeans

app = Dash(__name__)

app.layout = html.Div([
    html.H1("Visualizing Clustering Results"),
    html.Div(className='top', children=[
        html.Div(id='message-box'),
        html.Button('Export', id='btn-export')
    ]),
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
    Output('message-box', 'children'),
    Input('k-range', 'value'),
    Input('label', 'data'),
    Input('btn-export', 'n_clicks')
)
def export_data(k_value, data, btn):
    export_path = './output/{}_clusters.csv'.format(k_value)
    if ctx.triggered_id == 'btn-export':
        pd.read_json(StringIO(data), orient='index').set_index('OBJECTID').to_csv(export_path)
        return html.Div(
            html.P('Export clustering results to ' + export_path)
        )
    return 

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
    road_gdf = road_gdf.astype({'cluster_id': 'category'})
    fig = px.choropleth_mapbox(
        road_gdf,
        geojson=road_gdf.geometry,
        color='cluster_id',
        locations=road_gdf.index,
        center={"lat": 25.0375, "lon": 121.5625},
        mapbox_style="carto-positron",
        zoom=12
    )
    fig.update_layout(
        height=750,
        margin={'r': 16, 't': 16, 'l': 16, 'b': 16}
    )
    return fig

if __name__ == '__main__':
    app.run(debug=True)
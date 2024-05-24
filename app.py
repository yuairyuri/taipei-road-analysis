from dash import Dash, dcc, html, Input, Output, callback
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
                dcc.Graph(figure={}, id='polar-chart')
            ])
        ]),
        html.Div(className='right', children=[
            dcc.Graph(figure={}, id='road')
        ])
    ])
])

@app.callback(
    Output('cluster', 'options'),
    Input('k-range', 'value')
)
def select_cluster(k_value):
    options = [i for i in range(k_value)]
    return options

@app.callback(
    Output('polar-chart', 'figure'),
    Input('k-range', 'value')
)
def clustering(k_value):
    df = pd.read_csv("./data/major_road_data.csv").set_index('OBJECTID')
    X = df.iloc[:, 1:]
    kmeans = KMeans(n_clusters=k_value, random_state=31).fit(X)

    fig = go.Figure()
    for i in range(kmeans.n_clusters):
        fig.add_trace(go.Scatterpolar(
            r=kmeans.cluster_centers_[i],
            theta=X.columns,
            fill='toself',
            name=i
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
    Input('cluster', 'value')
)
def draw_road(selected_cluster):
    road_gdf = gpd.read_file("./data/roads.geojson").to_crs(4326).set_index('OBJECTID')
    fig = go.Figure(go.Choroplethmapbox(
        geojson=json.loads(road_gdf.geometry.to_json()),
        locations=road_gdf.index,
        z=road_gdf['RoadWidth']
    ))
    fig.update_layout(
        mapbox_style="carto-positron",
        mapbox_zoom=12,
        mapbox_center={"lat": 25.0375, "lon": 121.5625}
    )
    return fig

if __name__ == '__main__':
    app.run(debug=True)
# dash_app.py
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output

app = dash.Dash(__name__)

app.layout = html.Div([
    dcc.Graph(id='line-chart'),
], style={'width': '100%', 'height': '100vh'})  # Set width and height to 100% and 100vh

@app.callback(
    Output('line-chart', 'figure'),
    Input('line-chart', 'relayoutData')
)
def update_chart(relayoutData):
    # Dummy data
    x = [1, 2, 3, 4, 5]
    y = [10, 11, 12, 11, 10]

    figure = {
        'data': [{'x': x, 'y': y, 'type': 'line'}],
        'layout': {'title': 'Line Chart'}
    }

    return figure
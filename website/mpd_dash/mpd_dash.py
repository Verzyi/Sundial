# Instantiate a Dash app.
import dash
from dash import dash_table, dcc, html

from .data import CreateDataFrame
from .layout import html_layout

url_base = '/properties/'

def InitDashboard(server):
    # Create a Plotly Dash dashboard.
    dash_app = dash.Dash(
        server=server, 
        url_base_pathname=url_base,
        external_stylesheets=[
            '/static/dist/css/styles.css',
            'https://fonts.googleapis.com/css?family=Lato',
        ],
    )

    # Load DataFrame
    df = CreateDataFrame()

    # Custom HTML layout
    dash_app.index_string = html_layout

    # Create Layout
    dash_app.layout = html.Div(
        children=[
            dcc.Graph(
                id='histogram-graph',
                figure={
                    'data': [
                        {
                            'x': df['complaint_type'],
                            'text': df['complaint_type'],
                            'customdata': df['key'],
                            'name': '311 Calls by region.',
                            'type': 'histogram',
                        }
                    ],
                    'layout': {
                        'title': 'NYC 311 Calls category.',
                        'height': 500,
                        'padding': 150,
                    },
                },
            ),
            CreateDataTable(df),
        ],
        id='dash-container',
    )
    return dash_app.server

def CreateDataTable(df):
    # Create Dash datatable from Pandas DataFrame.
    table = dash_table.DataTable(
        id='database-table',
        columns=[{'name': i, 'id': i} for i in df.columns],
        data=df.to_dict('records'),
        sort_action='native',
        sort_mode='native',
        page_size=300,
    )
    return table
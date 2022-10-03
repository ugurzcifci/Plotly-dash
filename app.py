import dash
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from dash import callback, dcc, html, dash_table as dt
from dash.dependencies import Input, Output


app = dash.Dash()

app.layout = html.Div([
    html.H2('Hello Dash App!'),
], className="body-container")


if __name__ == '__main__':
    app.run_server(debug=True)

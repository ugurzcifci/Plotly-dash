import dash
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from dash import callback, dcc, html, dash_table as dt
from dash.dependencies import Input, Output

import fetch_data

app = dash.Dash(__name__)

# Data Wrangling
df_healthcare_raw = fetch_data.__fetch_healthcare_organizations()
df_healthcare = fetch_data.__prepare_healthcare_data(df_healthcare_raw)
df_ses = fetch_data.__fetch_SES_scores()

district_mean_ses, district_sum_of_healthcare, district_healthcare_category = \
    fetch_data.DerivedData(df_healthcare, df_ses).district_based_dataframes()

nh_sum_of_healthcare, nh_healthcare_category = \
    fetch_data.DerivedData(df_healthcare, df_ses).nh_based_dataframes()

districts = df_healthcare["ILCE_ADI"].unique()

app.layout = html.Div([
    html.H3(['Socio-economic Status (SES) Scores & Types of Healthcare Institutions in Istanbul'], className="title-1-container"),
    html.Div([
        dcc.Graph(id="bar-chart", figure=go.Figure())], className="bar-chart-container"),
    html.Div([
        html.P('District:', className='fix_label2', style={'color': '#f5f5f5'}),
        dcc.Dropdown(
            id='district_dropdown',
            multi=False,
            options=[{'label': ds, 'value': ds} for ds in districts],
            className='dcc_compon'),
        html.Br(),
        html.Br(),
        html.P('Neighborhood:', className='fix_label3', style={'color': '#f5f5f5'}),
        dcc.Dropdown(
            id='nh_dropdown',
            multi=False,
            className='dcc_compon'),
    ], className="dropdown-container"),
    html.Div([
        dcc.Graph(id="pie-chart", figure=px.pie())], className="pie-chart-container"),


], className="body-container")


# ================ Callbacks

# Linking district-neighborhood
@app.callback(
    Output('nh_dropdown', 'options'),
    [Input('district_dropdown', 'value')])
def set_neighborhoods_options(selected_district):
    dff = df_healthcare[df_healthcare["ILCE_ADI"] == selected_district]
    return [{'label': i, 'value': i} for i in sorted(dff["MAHALLE"].unique())]


# Pie chart callback
@app.callback(
    Output("pie-chart", "figure"),
    [Input('district_dropdown', 'value'), Input('nh_dropdown', 'value')])
def update_pie_chart(district_values, nh_values):
    if district_values:
        if nh_values:
            dff = nh_healthcare_category.loc[district_values, nh_values]["ADI"]
        else:
            dff = district_healthcare_category.loc[district_values]["ADI"]
    else:
        dff = district_healthcare_category["ADI"].groupby(by=["ALT_KATEGORI"]).sum()

    names = dff.index
    values = dff.values
    fig_bar = px.pie(dff, values=values, names=names)

    fig_bar.update_layout(
        autosize=True,
        # width=620,
        height=300,
        yaxis_title=None,
        xaxis_title=None,
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(
            l=0,
            r=0,
            b=0,
            t=0,
            pad=2
        ), )

    return fig_bar

# Bar chart callback
@app.callback(
    Output("bar-chart", "figure"),
    [Input('district_dropdown', 'value'), Input('nh_dropdown', 'value')])
def update_bar_chart(district_values, nh_values):
    district_mean_ses_sorted = district_mean_ses["SES SKORU"].sort_values(ascending=False)
    district_sum_of_healthcare_sorted = district_sum_of_healthcare.sort_values(ascending=False)

    fig = go.Figure(
        data=[
            go.Bar(name='SES', x=district_mean_ses_sorted.index, y=district_mean_ses_sorted.values, yaxis='y2', offsetgroup=2),
            go.Bar(name='Sağlık Hizmeti', x=district_sum_of_healthcare_sorted.index, y=district_sum_of_healthcare_sorted.values,
                   yaxis='y', offsetgroup=1)
        ],
        layout={
            'yaxis': {'title': 'Toplam Sağlık Hizmeti'},
            'yaxis2': {'title': 'SES', 'overlaying': 'y', 'side': 'right'}
        }
    )

    # Change the bar mode
    fig.update_layout(barmode='group', template="plotly_dark",
                      paper_bgcolor='rgba(0,0,0,0)',
                      plot_bgcolor='rgba(0,0,0,0)')
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)

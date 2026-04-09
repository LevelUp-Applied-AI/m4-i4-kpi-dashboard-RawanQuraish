# app.py
import dash
from dash import dcc, html, Input, Output
import plotly.graph_objects as go
import pandas as pd
from analysis import connect_db, extract_data, compute_kpis

# --- Connect DB and compute KPIs ---
engine = connect_db()
data_dict = extract_data(engine)
kpis = compute_kpis(data_dict)

# --- Extract cities for dropdown ---
orders = data_dict['orders']
cities = orders['city'].dropna().unique() if 'city' in orders.columns else ['All']

# --- Initialize Dash ---
app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server

# --- Layout ---
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div([
        dcc.Link('KPI Overview | ', href='/'),
        dcc.Link('Time-Series | ', href='/time-series'),
        dcc.Link('Cohort Comparison', href='/cohort')
    ]),
    html.Hr(),
    html.Div(id='page-content')
])

# --- Page 1: KPI Overview ---
def page_kpi_overview():
    kpi_names = ['monthly_revenue','weekly_orders','aov_category','customer_retention','top_products']
    kpi_values = [
        kpis['monthly_revenue'].iloc[-1],
        kpis['weekly_orders'].iloc[-1],
        kpis['aov_category'].mean(),
        kpis['customer_retention'].iloc[-1],
        kpis['top_products'].sum()
    ]
    figures = []
    for name, val in zip(kpi_names, kpi_values):
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=val,
            title={'text': name},
            gauge={'axis': {'range':[0, val*1.5]}}
        ))
        figures.append(dcc.Graph(figure=fig))
    
    return html.Div([
        html.H2("KPI Overview"),
        html.Label("Select City:"),
        dcc.Dropdown(id='city-dropdown', options=[{'label': c, 'value': c} for c in cities], value='All'),
        html.Div(figures)
    ])

# --- Page 2: Time-Series ---
def page_time_series():
    fig_rev = go.Figure()
    fig_rev.add_trace(go.Scatter(x=kpis['monthly_revenue'].index.astype(str),
                                 y=kpis['monthly_revenue'].values,
                                 mode='lines+markers',
                                 name='Revenue'))
    fig_ord = go.Figure()
    fig_ord.add_trace(go.Scatter(x=kpis['weekly_orders'].index.astype(str),
                                 y=kpis['weekly_orders'].values,
                                 mode='lines+markers',
                                 name='Orders'))
    return html.Div([
        html.H2("Time-Series Deep Dive"),
        html.Label("Select Date Range:"),
        dcc.DatePickerRange(
            id='date-range',
            start_date=kpis['monthly_revenue'].index.min().start_time,
            end_date=kpis['monthly_revenue'].index.max().end_time
        ),
        dcc.Graph(figure=fig_rev),
        dcc.Graph(figure=fig_ord)
    ])

# --- Page 3: Cohort Comparison ---
def page_cohort():
    # Example: group by customer join month
    customers = data_dict['customers']
    orders = data_dict['orders']
    merged = orders.merge(customers[['customer_id','join_date']], on='customer_id', how='left')
    merged['join_month'] = pd.to_datetime(merged['join_date']).dt.to_period('M')
    cohort_data = merged.groupby('join_month')['order_id'].count()
    fig = go.Figure([go.Bar(x=cohort_data.index.astype(str), y=cohort_data.values)])
    return html.Div([
        html.H2("Cohort Comparison"),
        dcc.Graph(figure=fig)
    ])

# --- Update Page Content ---
@app.callback(Output('page-content','children'), Input('url','pathname'))
def display_page(pathname):
    if pathname == '/time-series':
        return page_time_series()
    elif pathname == '/cohort':
        return page_cohort()
    else:
        return page_kpi_overview()

# --- Run App ---
if __name__ == '__main__':
    app.run(debug=True)
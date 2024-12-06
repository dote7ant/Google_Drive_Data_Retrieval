# Importing necessary libraries for Dash and Plotly
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go

# Initializing the Dash app
app = dash.Dash(__name__)

# Creating the layout of the app
app.layout = html.Div(
    children=[
        html.H1(children="Energy Production Dashboard"),
        dcc.Graph(
            id="daily-energy-graph",
            figure={
                "data": [
                    go.Bar(
                        x=daily_energy["Date"],
                        y=daily_energy["Total_Energy_Produced"],
                        name="Daily Energy Production",
                    ),
                    go.Scatter(
                        x=daily_energy["Date"],
                        y=daily_energy["Cumulative_Energy"],
                        mode="lines+markers",
                        name="Cumulative Energy Production",
                    ),
                ],
                "layout": {
                    "title": "Daily and Cumulative Energy Production",
                    "xaxis": {"title": "Date"},
                    "yaxis": {"title": "Energy (kWh)"},
                },
            },
        ),
    ]
)

# Running the app
if __name__ == "__main__":
    app.run_server(debug=True)

ye

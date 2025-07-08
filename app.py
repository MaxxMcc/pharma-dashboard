#app.py

import dash
from dash import dcc, html
import pandas as pd

# TODO: Load data/batch_data.csv
# For now, just print to show it works
try:
    df = pd.read_csv('data/batch_data.csv')
    print("CSV loaded successfully. Shape:", df.shape)
except FileNotFoundError:
    print("CSV not found. Make sure data/batch_data.csv exists.")

# Create Dash app
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Pharma Process Dashboard"),
    html.P("This is a stub — add graphs and callbacks here.")
])

if __name__ == '__main__':
    app.run_server(debug=True)
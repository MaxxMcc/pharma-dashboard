#app.py

import dash
from dash import dcc, html, dash_table
import pandas as pd
import plotly.express as px


# TODO: Load data/batch_data.csv
# For now, just print to show it works
try:
    df = pd.read_csv('data/batch_data.csv')
    print("CSV loaded successfully. Shape:", df.shape)
except FileNotFoundError:
    print("CSV not found. Make sure data/batch_data.csv exists.")

totalSnapshots = len(df)
totalAlarms = df['AlarmTriggered'].sum()
avgYield = round(df['Yield'].mean(), 2)

kpiCards = html.Div([
    html.H4(f"Total Batches: {totalSnapshots}"),
    html.H4(f"Total Alarms: {totalAlarms}"),
    html.H4(f"Average Yield: {avgYield} g")
])

#Yield Chart
import plotly.express as px
yieldChart = px.line(df, x='Timestamp', y='Yield', title='Yield[g] Per Run')

#alarms table
alarms_df = (
    df[df['AlarmTriggered'] == 1]
    .drop(columns=['AlarmTriggered'])
    .sort_values(by='Timestamp', ascending=False)
)
alarmTable = dash_table.DataTable(
    columns=[{"name": i, "id": i} for i in alarms_df.columns],
    data=alarms_df.to_dict('records'),
    page_size=10,
    style_table={'overflowX': 'auto'},
    style_cell={
        'textAlign': 'center',
        'padding': '5px'
    },
    style_header={
        'backgroundColor': 'lightgrey',
        'fontWeight': 'bold'
    }
)


# Create Dash app
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Pharma Process Dashboard"),
    html.P("Simulated batch process with real-time trends."),
    kpiCards,
    dcc.Graph(figure=yieldChart),
    html.H3("Alarm Events"),
    alarmTable
])


if __name__ == '__main__':
    app.run(debug=True)

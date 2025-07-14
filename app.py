#app.py

import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import time
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from simulateProcess import runSimulatorLoop

# -------------------------------------
# Constants
# -------------------------------------

DATA_FILE_PATH = "data/batch_data.csv"


# -------------------------------------
# Core App
# -------------------------------------

app = dash.Dash(__name__)


app.layout = html.Div([
    html.H1("Pharma Process Dashboard"),
    html.P("Simulated batch process with real-time trends."),
    html.Button(
        "Simulate One Snapshot",
        id="simulate-button",
        n_clicks=0
    ),
    dcc.Store(id="last-click-store", data=0),
    html.Div(id="kpi-cards"),
    dcc.Graph(id='yield-chart'),
    html.H3("Alarm Events"),
    html.Div([
        dcc.Graph(id='alarm-pie', style={'flex': '0.35', 'padding': '0 20px'}),

        html.Div([
            dash_table.DataTable(
                id="alarm-table",
                page_size=10,
                style_table={'overflowX': 'auto'},
                style_cell={'textAlign': 'center', 'padding': '5px'},
                style_header={'backgroundColor': 'lightgrey', 'fontWeight': 'bold'}
            )
        ], style={'flex': '0.6'})
    ], style={'display': 'flex', 'flex-direction': 'row'})    
])




@app.callback(
    Output("simulate-button", "children"),
    Output("kpi-cards", "children"),
    Output("yield-chart", "figure"),
    Output("alarm-table", "data"),
    Output("alarm-pie", "figure"),
    Output("last-click-store", "data"),
    Input("simulate-button", "n_clicks"),
    State("last-click-store", "data")
)
def simulate_and_update(n_clicks, last_click_stored):
    if n_clicks > 0 and n_clicks != last_click_stored:
        runSimulatorLoop(batchCount=1, wipeCSV=False)
        last_click_stored = n_clicks

    try:
        df = pd.read_csv(DATA_FILE_PATH)
    except FileNotFoundError:
        df = pd.DataFrame(columns=[
            "Timestamp","BatchID","DissolvedOxygen",
            "Temperature","pH","Yield","AlarmTriggered","AlarmType(s)"
        ])

    totalSnapshots = len(df)
    totalAlarms = df['AlarmTriggered'].sum() if not df.empty else 0
    avgYield = round(df['Yield'].mean(), 2) if not df.empty else 0

    kpiCards = html.Div([
        html.H4(f"Total Batches: {totalSnapshots}"),
        html.H4(f"Total Alarms: {totalAlarms}"),
        html.H4(f"Average Yield: {avgYield} g") 
    ])


    # Alarms Table 
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

    #Alarm Pie Chart
    if not df.empty:
        alarm_counts = {}
        for alarms in alarms_df['AlarmType(s)']:
            if pd.isna(alarms) or alarms.strip() == "":
                continue
            for alarm in alarms.split(','):
                alarm = alarm.strip()
                if alarm:
                    alarm_counts[alarm] = alarm_counts.get(alarm, 0) + 1

        if alarm_counts:
            alarmPie = px.pie(
                names=list(alarm_counts.keys()),
                values=list(alarm_counts.values()),
                title="Alarm Breakdown"
            )
        else:
            alarmPie = {}
    else:
        alarmPie = {}

    alarms_df = df[df['AlarmTriggered'] == 1].drop(columns=['AlarmTriggered'], errors='ignore').sort_values(by='Timestamp', ascending=False)
    alarmData = alarms_df.to_dict('records') if not alarms_df.empty else []

# Yield Graph
    if not df.empty:
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        df.sort_values('Timestamp', inplace=True)
        
        df['7DayAvg'] = df['Yield'].rolling(window=7, min_periods=1).mean()
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df['Timestamp'],
            y=df['Yield'],
            name='Daily Yield',
            marker_color='lightskyblue'
        ))

        # Line for 7-day rolling average
        fig.add_trace(go.Scatter(
            x=df['Timestamp'],
            y=df['7DayAvg'],
            name='7-Day Average',
            mode='lines',
            line=dict(color='firebrick', width=2)
        ))

        fig.update_layout(
            title='Yield [g] Per Batch with 7-Day Average',
            barmode='overlay',
            xaxis_title='Date',
            yaxis_title='Yield (g)',
            legend=dict(x=0.01, y=0.99),
            template='plotly_white'
        )
        yieldChart = fig
    else:
        yieldChart = {}

    return (
            "Simulate One Snapshot",
            kpiCards,
            yieldChart,
            alarmData,
            alarmPie,
            last_click_stored
        )


# -------------------------------------
# Run App Command
# -------------------------------------

if __name__ == '__main__':
    app.run(debug=True)

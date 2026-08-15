import json
import os
import threading
from datetime import datetime

import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import paho.mqtt.client as mqtt

MAX_RECORDS = 15

telemetry_logs = []
time_data = []
temp_data = []
hum_data = []
light_data = []
dist_data = []

MQTT_BROKER = "YOUR_MQTT_BROKER_IP"
MQTT_PORT = 1883
MQTT_TOPIC = "esp32/group52/data"


def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT Broker with result code:", rc)
    client.subscribe(MQTT_TOPIC)
    print(f"Subscribed to topic: {MQTT_TOPIC}")


def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode("utf-8"))
        current_time = datetime.now().strftime("%H:%M:%S")

        temp = payload.get("temperature", 0.0)
        hum = payload.get("humidity", 0.0)
        light = payload.get("light", 0)
        dist = payload.get("distance", 0.0)

        time_data.append(current_time)
        temp_data.append(temp)
        hum_data.append(hum)
        light_data.append(light)
        dist_data.append(dist)

        if len(time_data) > MAX_RECORDS:
            time_data.pop(0)
            temp_data.pop(0)
            hum_data.pop(0)
            light_data.pop(0)
            dist_data.pop(0)

        telemetry_logs.insert(0, {
            "Time": current_time,
            "Temp (C)": f"{temp:.2f}",
            "Humidity (%)": f"{hum:.2f}",
            "Light": light,
            "Distance (cm)": f"{dist:.2f}",
        })

        if len(telemetry_logs) > MAX_RECORDS:
            telemetry_logs.pop()

        print(f"[{current_time}] Appended MQTT Data: {payload}")

    except Exception as e:
        print(f"Error parsing MQTT payload: {e}")


def start_mqtt():
    try:
        client = mqtt.Client()
        client.on_connect = on_connect
        client.on_message = on_message
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_forever()
    except Exception as e:
        print(f"Could not connect to MQTT broker: {e}")


app = dash.Dash(_name_)
server = app.server  # Needed for gunicorn/Render deployment

DARK_BG = "#1e222d"
CARD_BG = "#2a2e3d"
TEXT_COLOR = "#e1e1e6"

app.layout = html.Div(
    style={
        "backgroundColor": DARK_BG,
        "color": TEXT_COLOR,
        "padding": "20px",
        "fontFamily": "Arial, sans-serif",
        "minHeight": "100vh",
    },
    children=[
        html.Div(
            style={
                "textAlign": "center",
                "marginBottom": "30px",
                "padding": "20px",
                "backgroundColor": CARD_BG,
                "borderRadius": "10px",
            },
            children=[
                html.H1("EE 288: Monitoring Dashboard",
                        style={"margin": "0", "fontSize": "28px"}),
                html.H4(
                    "Bit By Bit — Real-Time Sensor Telemetry & Logging System",
                    style={"color": "#00d2d3", "marginTop": "5px"},
                ),
            ],
        ),

        html.Div(
            style={"display": "flex", "gap": "20px", "marginBottom": "20px"},
            children=[
                html.Div(
                    style={"flex": "1", "backgroundColor": CARD_BG,
                           "padding": "15px", "borderRadius": "10px"},
                    children=[dcc.Graph(id="temp-graph")],
                ),
                html.Div(
                    style={"flex": "1", "backgroundColor": CARD_BG,
                           "padding": "15px", "borderRadius": "10px"},
                    children=[dcc.Graph(id="hum-graph")],
                ),
            ],
        ),

        html.Div(
            style={"display": "flex", "gap": "20px", "marginBottom": "30px"},
            children=[
                html.Div(
                    style={"flex": "1", "backgroundColor": CARD_BG,
                           "padding": "15px", "borderRadius": "10px"},
                    children=[dcc.Graph(id="light-graph")],
                ),
                html.Div(
                    style={"flex": "1", "backgroundColor": CARD_BG,
                           "padding": "15px", "borderRadius": "10px"},
                    children=[dcc.Graph(id="dist-graph")],
                ),
            ],
        ),

        html.Div(
            style={"backgroundColor": CARD_BG, "padding": "20px",
                   "borderRadius": "10px"},
            children=[
                html.H3("Recent Telemetry Logs",
                        style={"textAlign": "center",
                               "color": TEXT_COLOR,
                               "marginBottom": "15px"}),
                dash_table.DataTable(
                    id="telemetry-table",
                    columns=[
                        {"name": "Time", "id": "Time"},
                        {"name": "Temp (C)", "id": "Temp (C)"},
                        {"name": "Humidity (%)", "id": "Humidity (%)"},
                        {"name": "Light", "id": "Light"},
                        {"name": "Distance (cm)", "id": "Distance (cm)"},
                    ],
                    data=[],
                    style_header={
                        "backgroundColor": DARK_BG,
                        "color": "#00d2d3",
                        "fontWeight": "bold",
                        "textAlign": "center",
                    },
                    style_cell={
                        "backgroundColor": CARD_BG,
                        "color": "#ffffff",
                        "textAlign": "center",
                        "fontSize": "14px",
                        "border": "1px solid #3a3f51",
                    },
                    style_data_conditional=[
                        {"if": {"row_index": "odd"},
                         "backgroundColor": "#232734"}
                    ],
                ),
            ],
        ),

        dcc.Interval(id="interval-component", interval=2000, n_intervals=0),
    ],
)


@app.callback(
    [
        Output("temp-graph", "figure"),
        Output("hum-graph", "figure"),
        Output("light-graph", "figure"),
        Output("dist-graph", "figure"),
        Output("telemetry-table", "data"),
    ],
    [Input("interval-component", "n_intervals")],
)
def update_dashboard(n):
    layout_template = dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=TEXT_COLOR),
        xaxis=dict(showgrid=True, gridcolor="#3a3f51", title="Time"),
        yaxis=dict(showgrid=True, gridcolor="#3a3f51"),
    )

    fig_temp = go.Figure([go.Scatter(
        x=list(time_data), y=list(temp_data),
        mode="lines+markers", line=dict(color="#ff6b6b", width=2)
    )])
    fig_temp.update_layout(title="Temperature (C)", yaxis_title="C",
                           **layout_template)

    fig_hum = go.Figure([go.Scatter(
        x=list(time_data), y=list(hum_data),
        mode="lines+markers", line=dict(color="#00d2d3", width=2)
    )])
    fig_hum.update_layout(title="Humidity (%)", yaxis_title="% RH",
                          **layout_template)

    fig_light = go.Figure([go.Scatter(
        x=list(time_data), y=list(light_data),
        mode="lines+markers", line=dict(color="#fabca1", width=2)
    )])
    fig_light.update_layout(title="Light Intensity (LDR)",
                            yaxis_title="ADC Value", **layout_template)

    fig_dist = go.Figure([go.Scatter(
        x=list(time_data), y=list(dist_data),
        mode="lines+markers", line=dict(color="#1dd1a1", width=2)
    )])
    fig_dist.update_layout(title="Distance (cm)", yaxis_title="cm",
                           **layout_template)

    return fig_temp, fig_hum, fig_light, fig_dist, list(telemetry_logs)


mqtt_thread = threading.Thread(target=start_mqtt, daemon=True)
mqtt_thread.start()

if _name_ == "_main_":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8050)), debug=False)

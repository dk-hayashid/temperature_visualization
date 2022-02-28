import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import pandas as pd

cm = [
        [0, "rgb(181, 210, 236)"],
        [0.5, "rgb(255, 255, 255)"],
        [1.0, "rgb(252, 91, 74)"]
]
df = pd.read_csv('./data/0127_AM/temperature.csv')
app = dash.Dash(__name__)
app.layout = html.Div(children=[

    html.Div(
        html.H1("温湿度データの可視化"),
        style={"textAlign": "center"}
    ),

    html.Div([

        html.Div(children=[
            html.H4("種類を選択してください。",
                    style={"textAlign": "center"}),
            dcc.Dropdown(
                id="select-data-type",
                options=[{"label": "温度", "value": "temperature"},
                         {"label": "湿度", "value": "humidity"}],
                value="temperature",
                style={"textAlign": "center"}
            )
        ], style={"width": "30%", "display": "inline-block"}),

        html.Div(children=[
            html.H4("日付を選択してください。",
                    style={"textAlign": "center"}),
            dcc.Dropdown(
                id="select-data-date",
                options=[
                    {"label": "1月26日", "value": "0126"},
                    {"label": "1月27日", "value": "0127"},
                    {"label": "1月28日", "value": "0128"}
                ],
                value="0127",
                style={"textAlign": "center"}
            )
        ], style={"width": "30%", "display": "inline-block"}),

        html.Div(children=[
            html.H4("時間帯を選択してください。",
                    style={"textAlign": "center"}),
            dcc.Dropdown(
                id="select-data-period",
                options=[
                    {"label": "午前", "value": "AM"},
                    {"label": "午後", "value": "PM"}
                ],
                value="AM",
                style={"textAlign": "center"}
            )
        ], style={"width": "30%", "display": "inline-block"}),

    ], style={"padding": 10}),

    html.Div(id="heatmap", 
    style={
    "position": "relative",
    "top": "50%",
    "left": "30%",
})
])


@app.callback(
    Output("heatmap", "children"),
    [
        Input("select-data-type", "value"),
        Input("select-data-date", "value"),
        Input("select-data-period", "value"),
    ]
)
def update_graph(type_, date_, period_):
    df = pd.read_csv(f'./data/{date_}_{period_}/{type_}.csv')
    # df_max = max(df.max().tolist()[1:])
    # df_min = min(df.max().tolist()[1:])
    df_min, df_max = 22, 25
    dfs = []
    for idx, now in df.iterrows():
        dfs.append(pd.DataFrame(index=range(1, 12)[
                   ::-1], columns=list("abcde"), data=now.values[1:].reshape(11, 5)))
    frames = [
        go.Frame(data=go.Heatmap(z=df.values, x=df.columns, y=df.index,colorscale = cm), name=i)
        for i, df in zip(list(df['time']), dfs)
    ]

    fig = go.Figure(data=frames[0].data, frames=frames).update_layout(
        updatemenus=[
            {
                "buttons": [{"args": [None, {"frame": {"duration": 500, "redraw": True}}],
                            "label": "Play", "method": "animate", },
                            {"args": [[None], {"frame": {"duration": 0, "redraw": False},
                                               "mode": "immediate", "transition": {"duration": 0}, }, ],
                            "label": "Pause", "method": "animate", }, ],
                "type": "buttons",
            }
        ],
        # iterate over frames to generate steps... NB frame name...
        sliders=[{"steps": [{"args": [[f.name], {"frame": {"duration": 0, "redraw": True},
                                                 "mode": "immediate", }, ],
                            "label": f.name, "method": "animate", }
                            for f in frames], }],
        height=600,
        width=400,
        xaxis={"title": '窓側', "tickangle": 45, 'side': 'top'},
        title_x=0.5,
    )
    fig.data[0].update(zmin=df_min, zmax=df_max)

    return dcc.Graph(figure=fig)


app.run_server(host="0.0.0.0", port=5000, debug=False)  # Turn off reloader if inside Jupyter

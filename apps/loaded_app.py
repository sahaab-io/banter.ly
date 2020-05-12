import dash_core_components as dcc
import dash_html_components as html
from bson import ObjectId
from bson.errors import InvalidId
from dash.dependencies import Input, Output

from app import app
from constants.database_keys import COLOR_MAP, MEDIA_COUNTER, URI
from constants.div_properties import CHILDREN, DAQ_THEME, CIRCLE, VALUE
from datautils.Parser import Parser
from graphs.Graph import Graph
from layouts.graph_layout import graph_layout
from layouts.error_layout import error_layout
from services.processed_data_service import get_processed_data

CIRCLE_LOADING_2 = "circle-loading-2"
LOADED_CONTENT = "loaded-content"
LOADED_URL = "loaded-url"

layout = html.Div(
    [
        html.Br(),
        dcc.Loading(
            id=CIRCLE_LOADING_2,
            type=CIRCLE,
            children=[
                dcc.Location(id=LOADED_URL, refresh=False),
                html.Div(id=LOADED_CONTENT),
            ],
        ),
    ]
)


@app.callback(
    Output(LOADED_CONTENT, CHILDREN),
    [Input(LOADED_URL, "search"), Input(DAQ_THEME, VALUE)],
)
def display_loaded_page(search, dark_theme):
    uid = search[6:]
    try:
        oid = ObjectId(uid)
    except InvalidId:
        return html.Div(
            [
                error_layout(
                    "Analysis Not Found",
                    "the url you entered is either incorrect or the data has expired",
                ),
                dcc.Link("Start another analysis", href="/"),
            ]
        )
    processed_data = get_processed_data(oid)
    if processed_data:
        p = Parser()
        dfs, participants = p.reload_data(processed_data[URI])

        # Update the Graph class with the data and set the default graph template
        g = Graph()

        g.df = p.parsed_df
        g.dfs = dfs
        g.participants = participants
        g.color_map = processed_data[COLOR_MAP]
        g.media_counter = processed_data[MEDIA_COUNTER]

        # Create the final layout with Dash Graphs
        return graph_layout(g, dark_theme)
    else:
        return error_layout

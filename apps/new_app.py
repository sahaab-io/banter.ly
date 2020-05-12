import base64
import io

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app
from constants.div_properties import (
    CHAT_COUNT_MEMORY,
    CHILDREN,
    COLOR,
    DAQ_THEME,
    DATA,
    CHAT_COUNT,
    URL,
    CUSTOMIZATION_STORE,
    N_CLICKS,
    VALUE,
    FOR_RESEARCH,
    MESSAGE_COUNT_MEMORY,
    MESSAGE_COUNT,
    PARTICIPANTS_ALIASES,
    ALIASES_COLORS,
)
from constants.styling import BLUE
from datautils.Parser import Parser
from datautils.processor import process_data
from graphs.Graph import Graph
from layouts.graph_layout import graph_layout
from layouts.error_layout import error_layout
from services.counter_service import get_chat_count, get_message_count

CIRCLE_LOADING = "circle-loading"
CONTENTS = "contents"
GRAPH = "graph-container"
SHARE_URL = "share-url"
SHARE_BUTTON = "share-button"
UPLOAD = "upload-data"

# This graph and parser objects needs to be initialized here as their data
# will be shared by most of the methods
g = Graph()
parser = Parser()

layout = html.Div(
    [
        dcc.Upload(
            id=UPLOAD,
            children=html.Div(
                [
                    "Drag and drop or ",
                    html.A("select a file"),
                    " - note that processing may take as long as 2 minutes, or even longer",
                ]
            ),
            style={
                "width": "100%",
                "height": "60px",
                "lineHeight": "60px",
                "borderWidth": "1px",
                "borderStyle": "dashed",
                "borderRadius": "5px",
                "textAlign": "center",
                "margin": "10px",
            },
            # Explicitly don't allow multiple files to be uploaded
            multiple=False,
        ),
        html.Br(),
        dcc.Loading(
            id=CIRCLE_LOADING, type="circle", children=[html.Div(id=GRAPH)]
        ),
    ]
)


@app.callback(Output(CIRCLE_LOADING, CHILDREN), [Input(GRAPH, VALUE)])
@app.callback(
    Output(GRAPH, CHILDREN),
    [
        Input(UPLOAD, CONTENTS),
        Input(DAQ_THEME, VALUE),
        Input(CUSTOMIZATION_STORE, DATA),
        Input(FOR_RESEARCH, VALUE),
    ],
)
def generate_graphs(contents, dark_theme, customization, research_consent):
    try:
        if contents is not None:
            content_type, content_string = contents.split(",")
            if "text" in content_type:
                raw_text = io.StringIO(
                    base64.b64decode(content_string).decode("utf-8")
                ).getvalue()

                # Process the uploaded data and generate the new columns
                parser.parse(raw_text)
                # Check that the graph configuration matches the number of participants in the convo
                alias_color_map = None
                if customization:
                    participant_alias_map = customization[PARTICIPANTS_ALIASES]
                    if len(participant_alias_map) != len(parser.participants):
                        return error_layout(
                            "There are {} participants in this chat but the customization was set"
                            "for only {}".format(
                                len(parser.participants),
                                len(participant_alias_map),
                            ),
                            "Try clearing the graph customization",
                        )
                    else:
                        # Update the parsed dataframe with the aliases
                        parser.set_customization(participant_alias_map)
                        alias_color_map = customization[ALIASES_COLORS]

                # Run the processor and generate the new dataframe columns, and get back
                # an array of dataframes corresponding to each person in the chat
                # note that because this function is memoized you need to return a new df
                df, dfs, _ = process_data(parser.parsed_df)
                parser.parsed_df = df

                # Store a copy of the processed data in the bucket if the user has consented
                if len(research_consent) > 0:
                    parser.save_data(alias_color_map, True)

                # Update the Graph class with the data and set the default graph template
                g.df = parser.parsed_df
                g.dfs = dfs
                g.participants = parser.participants
                g.media_counter = parser.media_count_map

                if alias_color_map:
                    g.color_map = alias_color_map

                # Create the final layout with Dash Graphs
                return html.Div(
                    [
                        html.Div(
                            className="container",
                            style={
                                "text-align": "center",
                                "margin-bottom": "30px",
                            },
                            children=[
                                html.Button(
                                    "Share Results",
                                    id=SHARE_BUTTON,
                                    n_clicks=0,
                                    style={COLOR: BLUE},
                                ),
                                html.Div(id=SHARE_URL, style={COLOR: BLUE}),
                            ],
                        ),
                        graph_layout(g, dark_theme),
                    ]
                )
    except Exception as e:
        return error_layout("An un expected error occurred", str(e))


@app.callback(Output(CHAT_COUNT_MEMORY, DATA), [Input(UPLOAD, CONTENTS)])
def update_chat_counter(content):
    if content:
        return {CHAT_COUNT: get_chat_count()}


@app.callback(Output(MESSAGE_COUNT_MEMORY, DATA), [Input(UPLOAD, CONTENTS)])
def update_message_counter(content):
    if content:
        return {MESSAGE_COUNT: get_message_count()}


@app.callback(
    Output(SHARE_URL, CHILDREN),
    [
        Input(SHARE_BUTTON, N_CLICKS),
        Input(URL, "href"),
        Input(CUSTOMIZATION_STORE, DATA),
    ],
)
def generate_share_url(n_clicks, href, customization_data):
    # Only trigger this the first time a user clicks on a button, after that no need
    if n_clicks == 1:
        uuid = parser.save_data(g.color_map)
        return [
            html.H6(href + "share?uuid=" + uuid),
            html.H6("This link will be valid for 3 days"),
        ]
    elif n_clicks > 1:
        return html.H6(
            "Link already generated. To generate another link re-upload your data"
        )

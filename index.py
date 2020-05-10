import dash_core_components as dcc
import dash_daq as daq
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from app import app
from apps import new_app, loaded_app
from config import Config
from constants.div_properties import (
    ALIASES,
    CHILDREN,
    COLOR,
    CUSTOMIZATION_STORE,
    PARTICIPANT_COLORS,
    DAQ_THEME,
    PARTICIPANTS,
    CHAT_COUNT,
    CHAT_COUNT_MEMORY,
    DATA,
    PRIVACY,
    URL,
    N_CLICKS,
    VALUE,
    FOR_RESEARCH,
    MESSAGE_COUNT,
    MESSAGE_COUNT_MEMORY,
    PARTICIPANTS_ALIASES,
    ALIASES_COLORS,
)
from constants.styling import BLUE, GREEN
from services.counter_service import get_chat_count, get_message_count
from utils import is_hex_color

DARK_THEME_COMPONENTS = "dark-theme-components"
DARK_THEME_CONTAINER = "dark-theme-container"
CLEAR_GRAPH_CUSTOMIZATION = "clear-graph-customization"
GRAPH_CUSTOMIZATION = "graph-customization"
GRAPH_CUSTOMIZATION_ERROR = "graph-customization-error"
INSTRUCTIONS = "instructions"
PAGE_CONTENT = "page-content"
SET_GRAPH_CUSTOMIZATION = "set-graph-customization"
TEXT_AREA_CLASS = "four columns graph-customization-text-area"
HOVER_BOB = "hvr-bob"
HOVER_BOB_CONTINUOUS = "hvr-bob-continuous"
# Need to override the width of the text areas from here, and not from the CSS
TEXT_AREA_STYLE = {"width": "188px"}
CUSTOMIZATION_FIELDS = [PARTICIPANTS, ALIASES, PARTICIPANT_COLORS]

theme = {
    "dark": False,
    "detail": "#007439",
    "primary": GREEN,
    "secondary": "#6E6E6E",
}

chat_count = get_chat_count()
message_count = get_message_count()

# Instructions layout
instructions_layout = html.Details(
    title="Instructions",
    style={"text-align": "center"},
    children=[
        html.Summary("📔 Instructions"),
        dcc.Markdown(
            """
        ---
        1. [Export a WhatsApp Chat (without media)](https://faq.whatsapp.com/en/android/23756533/)
        2. _(Optional)_ customize the graph configuration below - **needs to be done first**
        3. Upload your `.txt` file
        4. Share with your friends!
        ---
        """
        ),
    ],
)

# Graph detail layout
graph_detail_layout = (
    html.Details(
        title="Customize",
        className="container",
        style={"text-align": "center"},
        children=[
            dcc.Store(id=CUSTOMIZATION_STORE, storage_type="memory"),
            html.Summary("⚙️ Graph Customization"),
            html.Div(
                [
                    html.Hr(),
                    dcc.Textarea(
                        id=PARTICIPANTS,
                        className=TEXT_AREA_CLASS,
                        style=TEXT_AREA_STYLE,
                        placeholder="The first name of everyone in the chat,"
                        "capitalization sensitive  - i.e. Amir,Laith",
                    ),
                    dcc.Textarea(
                        id=ALIASES,
                        className=TEXT_AREA_CLASS,
                        style=TEXT_AREA_STYLE,
                        placeholder="Aliases that what will be displayed on the graph "
                        "corresponding to each person - i.e. 👑, 🦁",
                    ),
                    dcc.Textarea(
                        id=PARTICIPANT_COLORS,
                        className=TEXT_AREA_CLASS,
                        style=TEXT_AREA_STYLE,
                        placeholder="A list of HEX or RGBA colors corresponding "
                        "to each person - i.e. #6E6E6E,#007439",
                    ),
                    daq.ColorPicker(
                        id="color-picker",
                        className="four columns",
                        label="A color picker for your convenience",
                        value=dict(hex="#ffffff"),
                    ),
                    html.Div(
                        [
                            html.Button(
                                "Set  ",
                                id=SET_GRAPH_CUSTOMIZATION,
                                n_clicks=0,
                                style={COLOR: BLUE, "margin": "5px"},
                            ),
                            html.Button(
                                "Clear",
                                id=CLEAR_GRAPH_CUSTOMIZATION,
                                n_clicks=0,
                                style={COLOR: BLUE, "margin": "5px"},
                            ),
                        ]
                    ),
                    html.Div(id=GRAPH_CUSTOMIZATION_ERROR),
                    html.Hr(),
                ]
            ),
        ],
    ),
)

# Privacy note layout
privacy_notice_layout = html.Details(
    title="Privacy Notice",
    style={"text-align": "center"},
    children=[
        html.Summary("🔐 Privacy Notice"),
        dcc.Markdown(
            """
        ---
        We do not collect or store any data beyond what's required to produce these graphs,
        and even that's stored encrypted and deleted after *72 hours*. The source code is public, so you can check
        for yourself (not that you can see the bucket configuration, so I guess you'll just have to trust us). If you 
        want to be super cautious, you can simply run Banter.ly locally on your machine.
        """
        ),
        html.P(
            [
                "If for some reason you're feeling generous, you can check ",
                dcc.Checklist(
                    id=FOR_RESEARCH,
                    options=[
                        {"label": "THIS BOX RIGHT HERE", VALUE: "research"}
                    ],
                    value=[],
                    labelStyle={"display": "inline-block"},
                ),
                "and explicitly give us permission to use your data for research and to improve this service "
                "- but we really recommend you don't.",
            ]
        ),
        dcc.Markdown(
            """
    ##### _"All data is either lost forever, or ends up public"_
    ---
    """
        ),
    ],
)

# A little confusing, but the root layout needs to be defined separately so that the dark-theme-provider can render it
root_layout = html.Div(
    [
        html.Div(id=GRAPH_CUSTOMIZATION),
        html.Br(),
        html.Div(
            [dcc.Location(id=URL, refresh=False), html.Div(id=PAGE_CONTENT)]
        ),
    ]
)

app.layout = html.Div(
    id=DARK_THEME_CONTAINER,
    children=[
        dcc.Store(id=CHAT_COUNT_MEMORY, storage_type="local"),
        dcc.Store(id=MESSAGE_COUNT_MEMORY, storage_type="local"),
        html.Header(
            className="container",
            style={"text-align": "center"},
            children=[
                html.A(
                    href="",
                    children=[
                        html.Img(
                            src=app.get_asset_url("logo.png"),
                            className=HOVER_BOB_CONTINUOUS,
                            alt="Banter.ly Logo",
                            style={"max-width": "300px"},
                        )
                    ],
                ),
                html.H1("Banter.ly"),
                html.H3(
                    "The world's most comprehensive open source chat analytics 🔎 and visualization app 📊"
                ),
                html.A(
                    href="https://ko-fi.com/I3I01O8A7",
                    children=[
                        html.Img(
                            src="https://cdn.ko-fi.com/cdn/kofi1.png?v=2",
                            alt="Buy me a coffee",
                            className=HOVER_BOB,
                            style={"height": "36px", "padding-right": "25px"},
                        )
                    ],
                ),
                html.Iframe(
                    src="https://ghbtns.com/github-btn.html?user=sahaab-io&repo=banter.ly&type=star&count=true&size"
                    "=large",
                    width="170",
                    height="30",
                    title="Star on GitHub",
                    className=HOVER_BOB,
                ),
                html.Br(),
                html.P([html.Em("v" + Config.VERSION)]),
                html.Br(),
                html.H2(
                    [
                        html.Span(
                            id=CHAT_COUNT,
                            style={COLOR: GREEN},
                            children=[chat_count],
                        ),
                        " chats analyzed",
                    ]
                ),
                html.H2(
                    [
                        html.Span(
                            id=MESSAGE_COUNT,
                            style={COLOR: GREEN},
                            children=[message_count],
                        ),
                        " messages processed",
                    ]
                ),
            ],
        ),
        html.Br(),
        daq.ToggleSwitch(
            id=DAQ_THEME,
            label=["Light", "Dark"],
            style={"width": "250px", "margin": "auto"},
            value=True,
        ),
        html.Br(),
        html.Div(id=INSTRUCTIONS, className="container"),
        html.Br(),
        html.Div(id=PRIVACY, className="container"),
        html.Br(),
        html.Div(
            id=DARK_THEME_COMPONENTS,
            children=[
                daq.DarkThemeProvider(theme=theme, children=root_layout)
            ],
        ),
        html.Br(),
        html.Footer(
            className="footer",
            children=[
                html.Div(
                    html.A(
                        href="https://sahaab.io",
                        children=[
                            html.Img(
                                className=HOVER_BOB,
                                src=app.get_asset_url("sahaab-logo.png"),
                                alt="Sahaab Logo",
                                style={"max-width": "50px"},
                            )
                        ],
                    )
                ),
                "made with 💙 at ",
                html.A("sahaab.io", href="https://sahaab.io"),
            ],
        ),
    ],
)


@app.callback(Output(PAGE_CONTENT, CHILDREN), [Input(URL, "pathname")])
def display_page(pathname):
    if pathname == "/":
        return new_app.layout
    elif "share" in pathname:
        return loaded_app.layout
    else:
        return "404"


@app.callback(
    Output(DARK_THEME_COMPONENTS, CHILDREN), [Input(DAQ_THEME, VALUE)]
)
def turn_dark(dark_theme):
    if dark_theme:
        theme.update(dark=True)
    else:
        theme.update(dark=False)
    return daq.DarkThemeProvider(theme=theme, children=root_layout)


@app.callback(Output(DARK_THEME_CONTAINER, "style"), [Input(DAQ_THEME, VALUE)])
def change_bg(dark_theme):
    if dark_theme:
        return {"background-color": "#383838", "color": "white"}
    else:
        return {"background-color": "white", "color": "black"}


@app.callback(Output("js-focus-visible", "style"), [Input(DAQ_THEME, VALUE)])
def change_bg_2(dark_theme):
    if dark_theme:
        return {"background-color": "#383838", "color": "white"}
    else:
        return {"background-color": "white", "color": "black"}


@app.callback(
    Output(CHAT_COUNT, CHILDREN),
    [Input(CHAT_COUNT_MEMORY, DATA)],
    [State(CHAT_COUNT_MEMORY, DATA)],
)
def update_chat_count(_, new_data):
    data = new_data or {}
    return data.get(CHAT_COUNT, get_chat_count())


@app.callback(
    Output(MESSAGE_COUNT, CHILDREN),
    [Input(MESSAGE_COUNT_MEMORY, DATA)],
    [State(MESSAGE_COUNT_MEMORY, DATA)],
)
def update_message_count(_, new_data):
    data = new_data or {}
    return data.get(MESSAGE_COUNT, get_message_count())


@app.callback(Output(GRAPH_CUSTOMIZATION, CHILDREN), [Input(URL, "search")])
def display_customization(search):
    if not search:
        return graph_detail_layout


@app.callback(Output(INSTRUCTIONS, CHILDREN), [Input(URL, "search")])
def display_instructions(search):
    if not search:
        return instructions_layout


@app.callback(Output(PRIVACY, CHILDREN), [Input(URL, "search")])
def display_privacy(search):
    if not search:
        return privacy_notice_layout


@app.callback(
    Output(GRAPH_CUSTOMIZATION_ERROR, CHILDREN),
    [Input(SET_GRAPH_CUSTOMIZATION, N_CLICKS)],
    [
        State(PARTICIPANTS, VALUE),
        State(ALIASES, VALUE),
        State(PARTICIPANT_COLORS, VALUE),
    ],
)
def validate_customization(n_clicks, participants, aliases, colors):
    if n_clicks:
        if participants and aliases and colors:
            participant_list = [
                participant.strip() for participant in participants.split(",")
            ]
            alias_list = [alias.strip() for alias in aliases.split(",")]
            color_list = [color.strip() for color in colors.split(",")]

            if not (
                len(participant_list) == len(alias_list)
                and len(participant_list) == len(alias_list)
            ):
                return html.Div(
                    className="container error-container",
                    children=[
                        html.H3("❗"),
                        html.H6(
                            "Number of settings in each list is not equal"
                        ),
                        html.P(
                            "Make sure the length of each list is the same"
                        ),
                    ],
                )

            for color in color_list:
                if not is_hex_color(color):
                    return html.Div(
                        className="container error-container",
                        children=[
                            html.H3("❗"),
                            html.H6("Invalid Color"),
                            html.P(
                                "Please use a valid hex color (including the #) - use the color picker!"
                            ),
                        ],
                    )

            return [
                html.H3("✔️"),
                html.H4("Graph Customization Set!", style={COLOR: GREEN}),
            ]


@app.callback(
    Output(CUSTOMIZATION_STORE, DATA),
    [Input(SET_GRAPH_CUSTOMIZATION, N_CLICKS)],
    [
        State(PARTICIPANTS, VALUE),
        State(ALIASES, VALUE),
        State(PARTICIPANT_COLORS, VALUE),
    ],
)
def set_local_store_customization_data(
    n_clicks, participants, aliases, colors
):
    if n_clicks:
        if participants and aliases and colors:
            participant_list = [
                participant.strip() for participant in participants.split(",")
            ]
            alias_list = [alias.strip() for alias in aliases.split(",")]
            color_list = [color.strip() for color in colors.split(",")]

            if not (
                len(participant_list) == len(alias_list)
                and len(participant_list) == len(alias_list)
            ):
                raise PreventUpdate

            for color in color_list:
                if not is_hex_color(color):
                    raise PreventUpdate

            return {
                PARTICIPANTS_ALIASES: dict(zip(participant_list, alias_list)),
                ALIASES_COLORS: dict(zip(alias_list, color_list)),
            }
    raise PreventUpdate


# Create callbacks for clearing graph customization fields
for field in CUSTOMIZATION_FIELDS:

    @app.callback(
        Output(field, VALUE), [Input(CLEAR_GRAPH_CUSTOMIZATION, N_CLICKS)]
    )
    def clear_field(n_clicks):
        if n_clicks:
            return ""


if __name__ == "__main__":
    app.run_server(debug=True)

import dash_core_components as dcc
import dash_html_components as html
import plotly.io as pio

from graphs.Graph import Graph


def layout_graphs(g: Graph, dark_theme: bool) -> html.Div:
    config = {"displaylogo": False}
    graph_class = "graph-container"

    if dark_theme:
        pio.templates.default = "plotly_dark"
    else:
        pio.templates.default = "plotly"

    return html.Div(
        style={"text-align": "center"},
        children=[
            __layout_quote("What stories do the numbers tell?"),
            dcc.Graph(
                figure=g.pie_charts(), config=config, className=graph_class
            ),
            dcc.Graph(
                figure=g.daily_messages(), config=config, className=graph_class
            ),
            dcc.Graph(
                figure=g.word_distribution(),
                config=config,
                className=graph_class,
            ),
            dcc.Graph(
                figure=g.word_cloud(),
                config=config,
                className=graph_class,
                style={"FONT-WEIGHT": "300px"},
            ),
            __layout_quote("Time isn't the main thing. It's the only thing"),
            dcc.Graph(
                figure=g.time_heat_map(), config=config, className=graph_class
            ),
            dcc.Graph(
                figure=g.sentiment_over_time(),
                config=config,
                className=graph_class,
            ),
            __layout_quote(
                "The value of emotions comes from sharing them, not just having them"
            ),
            dcc.Graph(
                figure=g.emotion_tree_map(),
                config=config,
                className=graph_class,
            ),
            dcc.Graph(
                figure=g.profanity_sunburst(),
                config=config,
                className=graph_class,
            ),
            __layout_quote(
                "When you talk, you are only repeating what you already know. "
                "But if you listen, you may learn something new"
            ),
            dcc.Graph(
                figure=g.topic_graph(), config=config, className=graph_class
            ),
            __layout_quote("Time spent learning is never wasted"),
        ],
    )


def __layout_quote(quote: str) -> html.Div:
    return html.Div(
        className="container",
        children=[
            html.Hr(),
            html.H3([html.Em('"{}"'.format(quote))]),
            html.Hr(),
        ],
    )

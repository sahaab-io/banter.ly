import dash_core_components as dcc
import dash_html_components as html
import plotly.io as pio

from graphs.Graph import Graph
from layouts.error_layout import error_layout


def graph_layout(g: Graph, dark_theme: bool) -> html.Div:
    if dark_theme:
        pio.templates.default = "plotly_dark"
    else:
        pio.templates.default = "plotly"

    return html.Div(
        style={"text-align": "center"},
        children=[
            __layout_quote("What stories do the numbers tell?"),
            __layout_chart("pie charts", g.pie_charts),
            __layout_chart("daily messages chart", g.daily_messages),
            __layout_chart("word distribution chart", g.word_distribution),
            __layout_chart(
                "word cloud", g.word_cloud, {"FONT-WEIGHT": "300px"}
            ),
            __layout_quote("Time isn't the main thing. It's the only thing"),
            __layout_chart("time heat map", g.time_heat_map),
            __layout_chart("sentiment over time", g.sentiment_over_time),
            __layout_quote(
                "The value of emotions comes from sharing them, not just having them"
            ),
            __layout_chart("emotion tree map", g.emotion_tree_map),
            __layout_chart("profanity sunburst plot", g.profanity_sunburst),
            __layout_quote(
                "When you talk, you are only repeating what you already know. "
                "But if you listen, you may learn something new"
            ),
            __layout_chart("topic graph", g.topic_graph),
            __layout_quote("Time spent learning is never wasted"),
        ],
    )


def __layout_chart(name, graph_func, style=None):
    if style is None:
        style = {}
    try:
        return dcc.Graph(
            figure=graph_func(),
            config={"displaylogo": False},
            className="graph-container",
            style=style,
        )
    except Exception as e:
        return error_layout(
            "Something went wrong plotting the " + name, str(e)
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

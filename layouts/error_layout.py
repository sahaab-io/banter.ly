import dash_html_components as html


def error_layout(error_type: str, error_message: str) -> html.Div:
    return html.Div(
        className="container error-container",
        children=[html.H3("❗"), html.H6(error_type), html.P(error_message)],
    )

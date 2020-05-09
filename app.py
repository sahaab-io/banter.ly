"""The main dash flask application and it's components"""
import dash
from pymongo import MongoClient

from config import Config

# from flask_caching import Cache


app = dash.Dash(
    __name__,
    meta_tags=[
        # A description of the app, used by e.g.
        # search engines when displaying search results.
        {
            "name": "Banter.ly",
            "content": "The world's most comprehensive open source chat analytics 🔎 and visualization app 📊",
        },
        # A tag that tells Internet Explorer (IE)
        # to use the latest renderer version available
        # to that browser (e.g. Edge)
        {"http-equiv": "X-UA-Compatible", "content": "IE=edge"},
        # A tag that tells the browser not to scale
        # desktop widths to fit mobile screens.
        # Sets the width of the viewport (browser)
        # to the width of the device, and the zoom level
        # (initial scale) to 1.
        #
        # Necessary for "true" mobile support.
        {
            "name": "viewport",
            "content": "width=device-width, initial-scale=1.0",
        },
    ],
)
app.title = "Banter.ly"

server = app.server
server.config.from_object(Config)
app.config.suppress_callback_exceptions = True

db = MongoClient(Config.DB_URL).test_database

# Initialize the cache
# if Config.CACHE_TYPE == 'redis':
#     cache_config = {
#         'DEBUG': Config.CACHE_DEBUG,
#         'CACHE_TYPE': Config.CACHE_TYPE,
#         'CACHE_REDIS_URL': Config.CACHE_URL
#     }
# else:
#     cache_config = {
#         'DEBUG': True,
#         'CACHE_TYPE': 'filesystem',
#         'CACHE_DIR': 'cache'
#     }
#
# cache = Cache(server, config=cache_config)

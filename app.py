"""The main dash flask application and it's components"""
import logging
import os
from logging.handlers import RotatingFileHandler

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
# Configure the logging in production (assuming Heroku environment)
if Config.LOG_TO_STDOUT:
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    server.logger.addHandler(stream_handler)
else:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/banterly.log',
                                       maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s '
        '[in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    server.logger.addHandler(file_handler)

server.logger.setLevel(logging.INFO)
server.logger.info('Banter.ly startup')

# Create the DB Client (and DB if it doesn't exist)
db = MongoClient(Config.DB_URL).banterly_main

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

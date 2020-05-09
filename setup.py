"""You must run this file at least once for the app to work, simply by running `python setup.py`"""
from datetime import datetime

import nltk

from app import db
from constants.database_keys import TYPE, COUNT, LAST_UPDATED

# Download additional NLTK Data
nltk.download("punkt")
nltk.download("stopwords")
nltk.download("wordnet")
nltk.download("vader_lexicon")

# Create the counters in the DB
counters = db.counters
if not counters.find_one({TYPE: "chats"}):
    counters.insert_many(
        [
            {TYPE: "chats", COUNT: 0, LAST_UPDATED: datetime.now()},
            {TYPE: "messages", COUNT: 0, LAST_UPDATED: datetime.now()},
        ]
    )

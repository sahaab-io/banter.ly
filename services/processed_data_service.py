from datetime import datetime
from typing import Dict

from bson.objectid import ObjectId

from app import db
from constants.database_keys import (
    OID,
    URI,
    LAST_UPDATED,
    MEDIA_COUNTER,
    COLOR_MAP,
)

__processed_data = db.processed_data


def create_processed_data_entry(
    oid: ObjectId, uri: str, color_map: Dict, media_counter: Dict
):
    return __processed_data.insert_one(
        {
            OID: oid,
            URI: uri,
            LAST_UPDATED: datetime.now(),
            COLOR_MAP: color_map,
            MEDIA_COUNTER: media_counter,
        }
    ).acknowledged


def get_processed_data(oid: ObjectId) -> dict:
    return __processed_data.find_one({OID: oid})

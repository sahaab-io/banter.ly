from app import db
from constants.database_keys import TYPE, COUNT

__counters = db.counters
__chat_query = {TYPE: "chats"}
__message_query = {TYPE: "messages"}


def get_chat_count() -> int:
    c = __counters.find_one(__chat_query)
    return c[COUNT]


def get_message_count() -> int:
    c = __counters.find_one(__message_query)
    return c[COUNT]


def increment_chat_count():
    __counters.update_one(__chat_query, {"$inc": {COUNT: 1}})


def increase_message_count(num_messages: int):
    __counters.update_one(__message_query, {"$inc": {COUNT: num_messages}})

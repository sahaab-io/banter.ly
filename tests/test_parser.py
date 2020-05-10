import pytest
import numpy as np
from constants.column_names import TIMESTAMP, SENDER, RAW_TEXT
from datautils.Parser import Parser
from datetime import datetime

test_data = [
    (
        "2017-03-17, 11:57 a.m. - Sami: you tryna eat \n2017-03-17, 1:06 p.m. - Amir Abushanab: No food",
        np.datetime64(datetime(2017, 3, 17, 11, 57)),
        "Sami",
        "you tryna eat ",
        np.datetime64(datetime(2017, 3, 17, 13, 6)),
        "Amir",
        "No food",
    ),
    (
        "2019-07-27, 14:43 - Amir Abushanab: well\n2019-07-27, 14:44 - Amir Abushanab: you see",
        np.datetime64(datetime(2019, 7, 27, 14, 43)),
        "Amir",
        "well",
        np.datetime64(datetime(2019, 7, 27, 14, 44)),
        "Amir",
        "you see",
    ),
    (
        "[2019-12-15, 8:42:59 AM] Amir: 👂🏽\n[2019-12-15, 8:43:27 AM] Laila: I'",
        np.datetime64(datetime(2019, 12, 15, 8, 42, 59)),
        "Amir",
        "👂🏽",
        np.datetime64(datetime(2019, 12, 15, 8, 43, 27)),
        "Laila",
        "I'",
    ),
    (
        "2020-03-25, 12:15 - Amir Abushanab: [03-24, 22:05] Amir Abushanab: Legit problems need legit solutions.\n"
        "2020-03-25, 12:16 - Amir Abushanab: [03-24, 22:06] Amir Abushanab: Copy pasted texts are a bitch\n",
        np.datetime64(datetime(2020, 3, 25, 12, 15)),
        "Amir",
        "[03-24, 22:05] Amir Abushanab: Legit problems need legit solutions.",
        np.datetime64(datetime(2020, 3, 25, 12, 16)),
        "Amir",
        "[03-24, 22:06] Amir Abushanab: Copy pasted texts are a bitch",
    ),
]


@pytest.mark.parametrize(
    "message,timestamp_one, sender_one, raw_text_one, timestamp_two, sender_two, raw_text_two",
    test_data,
)
def test_parser(
    message,
    timestamp_one,
    sender_one,
    raw_text_one,
    timestamp_two,
    sender_two,
    raw_text_two,
):
    p = Parser()
    p.parse(message)
    assert p.parsed_df[TIMESTAMP].values[0] == timestamp_one
    assert p.parsed_df[SENDER].values[0] == sender_one
    assert p.parsed_df[RAW_TEXT].values[0] == raw_text_one

    assert p.parsed_df[TIMESTAMP].values[1] == timestamp_two
    assert p.parsed_df[SENDER].values[1] == sender_two
    assert p.parsed_df[RAW_TEXT].values[1] == raw_text_two

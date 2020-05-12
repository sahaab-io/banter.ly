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
        "11/26/15, 2:16 PM - Amir The Sexy Awesome Dude MTL: Thanks bro👍🏼\n"
        "1/26/15, 2:38 PM - Riad El Muriby: No problem !",
        np.datetime64(datetime(2015, 11, 26, 14, 16)),
        "Amir",
        "Thanks bro👍🏼",
        np.datetime64(datetime(2015, 1, 26, 14, 38)),
        "Riad",
        "No problem !",
    ),
    (
        "1/2/15, 2:16 PM - Amir The Sexy Awesome Dude MTL: Thanks bro👍🏼\n"
        "11/2/15, 2:38 PM - Riad El Muriby: No problem !",
        np.datetime64(datetime(2015, 1, 2, 14, 16)),
        "Amir",
        "Thanks bro👍🏼",
        np.datetime64(datetime(2015, 11, 2, 14, 38)),
        "Riad",
        "No problem !",
    ),
    (
        "1/2/15, 2:16 PM - Amir The Sexy Awesome Dude MTL: Thanks bro👍🏼\n"
        "11/26/15, 12:38 PM - Riad El Muriby: No problem !",
        np.datetime64(datetime(2015, 1, 2, 14, 16)),
        "Amir",
        "Thanks bro👍🏼",
        np.datetime64(datetime(2015, 11, 26, 12, 38)),
        "Riad",
        "No problem !",
    ),
    (
        "[11/27/15, 12:43:46 AM] Loujaine A.: :/\n"
        "[1/1/16, 9:17:31 PM] Amir Abushanab: Thnx 👍🏼",
        np.datetime64(datetime(2015, 11, 27, 0, 43, 46)),
        "Loujaine",
        ":/",
        np.datetime64(datetime(2016, 1, 1, 21, 17, 31)),
        "Amir",
        "Thnx 👍🏼",
    ),
    (
        "[11/05/2020, 1:48:55 PM] Bashayer: What\n"
        "[11/05/2020, 1:48:58 PM] Bashayer: It's 2",
        np.datetime64(datetime(2020, 5, 11, 13, 48, 55)),
        "Bashayer",
        "What",
        np.datetime64(datetime(2020, 5, 11, 13, 48, 58)),
        "Bashayer",
        "It's 2",
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

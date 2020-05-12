"""The Parser class is used for converting raw exported chats from various sources to a standard DF format """
import datetime
from ast import literal_eval
from collections import defaultdict
from io import StringIO
from typing import Dict

import pandas as pd
from boto3.session import Session
from botocore.exceptions import NoCredentialsError
from bson.objectid import ObjectId
from smart_open import open

from config import Config
from constants.column_names import (
    TIMESTAMP,
    RAW_TEXT,
    SENDER,
    CLEANED_TEXT,
    ENTITIES,
)
from constants.date_formats import (
    IS_DASHED_Y_M_D_12,
    IS_DASHED_Y_M_D_24,
    IS_SQUARE_BRACKET_SLASHES,
    IS_SLASHES_M_D_Y_12,
    IS_SQUARE_BRACKET_Y_M_D_12,
)
from constants.messengers import WHATSAPP
from services import counter_service, processed_data_service


class Parser:
    def __init__(self):
        self.messengers = [WHATSAPP]
        self.parsed_df = None
        self.participants = None
        self.media_count_map = None
        self.session = Session(
            aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY,
        )

    def parse(self, raw_text: str, messenger: str = WHATSAPP):
        """
        Parse will take a raw input and convert it to a Dataframe, count the number of media messages sent, and
        store the result
        :param raw_text: The exported chat file's contents
        :param messenger: One of 'whatsapp'
        """
        if messenger not in self.messengers:
            raise ValueError(
                "received an an unsupported messenger type as an argument to parse -"
                " messenger should be one of {}".format(self.messengers)
            )

        d = []
        entry = None
        media_count_map = defaultdict(int)

        for line in raw_text.splitlines():
            # Skip over invalid whatsapp messages
            if self.__invalid_whatsapp_message(line):
                continue

            date_format = self.__extract_date_format(line)
            if date_format:
                # Set the indices
                first_name_start = self.__extract_first_name_index(
                    line, date_format
                )
                last_name_end = line.index(": ", first_name_start) + 2

                # Skip the lines with media causing issues and tally them
                if "<Media omitted>" in line:
                    media_count_map[
                        self.__extract_sender(
                            line, date_format, first_name_start
                        )
                    ] += 1
                    continue
                if entry is not None:
                    d.append(entry)

                # Set the sender
                sender = self.__extract_sender(
                    line, date_format, first_name_start
                )

                # Extract the timestamp. The try catch is to account for the case where you copy pasted a message or the
                # rare case where the message starts with a morphed timestamp
                time = self.__extract_time(line, date_format, first_name_start)
                if not time:
                    entry[RAW_TEXT] = entry[RAW_TEXT] + line
                    continue

                # Extract the text and create the data entry
                text = line[last_name_end : len(line)]
                entry = {TIMESTAMP: time, SENDER: sender, RAW_TEXT: text}

            # If it's a multiline text, in which case the entry value is not
            # reset and passed onto the next loop
            else:
                # Sometimes the first line is problematic, this if statement is to account for that
                if entry is None:
                    continue
                entry[RAW_TEXT] = entry[RAW_TEXT] + line

        # Append the last line left after exiting the loop
        if entry is not None:
            d.append(entry)

        df = pd.DataFrame(d)
        pd.to_datetime(df[TIMESTAMP])
        self.parsed_df = df
        self.media_count_map = media_count_map
        self.participants = list(df[SENDER].unique())

        # The try-catch is here only in case there's some error reaching the DB, i.e. we still want users
        # to be able to have their data parsed even if the DB is down
        try:
            counter_service.increment_chat_count()
            counter_service.increase_message_count(df.shape[0])
        finally:
            pass

    def reload_data(self, uri):
        with open(
            uri,
            mode="r",
            encoding="utf-8",
            transport_params=dict(session=self.session),
        ) as f:
            df = pd.read_csv(f, index_col=0, parse_dates=[TIMESTAMP])

        # Arrays and Dicts are stored as strings so you need to turn them back
        df[CLEANED_TEXT] = df[CLEANED_TEXT].apply(lambda x: literal_eval(x))
        df[ENTITIES] = df[ENTITIES].apply(lambda x: literal_eval(x))

        dfs = []
        participants = df[SENDER].unique()
        for participant in participants:
            dfs.append(df[df[SENDER] == participant])

        self.parsed_df = df
        self.participants = participants
        return dfs, participants

    def save_data(self, sender_color_map: Dict, is_permanent=False) -> str:
        oid = ObjectId()
        uid = str(oid)
        uri = Config.TEMP_BUCKET_PATH + uid + ".csv"
        if is_permanent:
            uri = Config.PERMANENT_BUCKET_PATH + uid + ".csv"
        try:
            fout = open(
                uri,
                "w",
                encoding="utf-8",
                transport_params=dict(session=self.session),
            )
        except (NoCredentialsError, ValueError) as e:
            uri = "./tmp/" + uid + ".csv"
            fout = open(uri, "w", encoding="utf-8")

        csv_buffer = StringIO()
        self.parsed_df.to_csv(csv_buffer)
        fout.write(csv_buffer.getvalue())
        csv_buffer.close()
        fout.close()

        processed_data_service.create_processed_data_entry(
            oid, uri, sender_color_map, self.media_count_map
        )
        return uid

    def set_customization(self, participant_alias_mapping):
        if len(self.parsed_df) == 0:
            raise ValueError("the parser has not parsed any dataframes")

        if not self.media_count_map:
            raise ValueError("the parser has not parsed a media count map")

        # Replace the participant names with their aliases
        self.parsed_df[SENDER] = self.parsed_df[SENDER].replace(
            participant_alias_mapping
        )

        # Do the same for the media count map and participant list
        updated_media_count = {}
        for name, count in self.media_count_map.items():
            updated_media_count[participant_alias_mapping[name]] = count
        self.media_count_map = updated_media_count

        self.participants = list(self.parsed_df[SENDER].unique())

    @staticmethod
    def __invalid_whatsapp_message(message: str) -> bool:
        return (
            message == ""
            or " are now secured with end-to-end encryption" in message
            or "You created group " in message
            or "You added " in message
            or "You removed " in message
            or " changed this group's icon" in message
            or ' changed the subject from "' in message
        )

    @staticmethod
    def __extract_date_format(message: str) -> str:
        # todo: implement stricter checking to prevent cases with phone numbers or postal codes
        if (message[0:4].isdigit() and message[4] == "-") and (
            " p.m. - " in message[:27] or " a.m. - " in message[:27]
        ):
            return IS_DASHED_Y_M_D_12

        if (message[0:4].isdigit() and message[4] == "-") and not (
            " p.m. - " in message[:27] or " a.m. - " in message[:27]
        ):
            return IS_DASHED_Y_M_D_24

        if (
            message[0] == "["
            and ("PM" in message[:27] or "AM" in message[:27])
            and "/" not in message[:27]
        ):
            return IS_SQUARE_BRACKET_Y_M_D_12

        if (
            message[0] != "["
            and (message[1] == "/" or message[2] == "/")
            and ("PM" in message[:27] or "AM" in message[:27])
        ):
            return IS_SLASHES_M_D_Y_12

        if (
            message[0] == "["
            and (message[2] == "/" or message[3] == "/")
            and ("PM" in message[:27] or "AM" in message[:27])
        ):
            return IS_SQUARE_BRACKET_SLASHES

        return ""

    @staticmethod
    def __extract_first_name_index(message: str, date_format: str) -> int:
        if IS_SQUARE_BRACKET_Y_M_D_12 == date_format:
            return 25

        if IS_DASHED_Y_M_D_12 == date_format:
            if message[24] == " ":
                return 25
            else:
                return 24

        if IS_DASHED_Y_M_D_24 == date_format:
            return 20

        if IS_SLASHES_M_D_Y_12 == date_format:
            for index, value in enumerate(message):
                if value == "-":
                    return index + 2

        if IS_SQUARE_BRACKET_SLASHES == date_format:
            for index, value in enumerate(message):
                if value == "]":
                    return index + 2
        return 0

    @staticmethod
    def __extract_sender(
        message: str, date_format: str, start_pos: int
    ) -> str:
        """
        Helper function for getting a person's name once we have the date
        :param message:
        :param start_pos:
        :return:
        """
        for index, letter in enumerate(message[start_pos:], start=start_pos):
            if letter == " " or letter == ":":
                return message[start_pos:index]

    @staticmethod
    def __extract_time(message: str, date_format: str, first_name_start: int):
        try:
            if IS_SQUARE_BRACKET_Y_M_D_12 == date_format:
                if message[first_name_start - 2] == "]":
                    first_name_start += 1
                    return datetime.datetime.strptime(
                        message[0 : first_name_start - 2],
                        "[%Y-%m-%d, %I:%M:%S %p]",
                    )
            elif IS_DASHED_Y_M_D_12 == date_format:
                return datetime.datetime.strptime(
                    message[0 : first_name_start - 3].replace(".", ""),
                    "%Y-%m-%d, %I:%M %p",
                )
            elif IS_DASHED_Y_M_D_24 == date_format:
                return datetime.datetime.strptime(
                    message[0 : first_name_start - 3], "%Y-%m-%d, %H:%M"
                )
            elif IS_SLASHES_M_D_Y_12 == date_format:
                return datetime.datetime.strptime(
                    message[0 : first_name_start - 3], "%m/%d/%y, %I:%M %p"
                )
            elif IS_SQUARE_BRACKET_SLASHES == date_format:
                try:
                    return datetime.datetime.strptime(
                        message[0 : first_name_start - 1],
                        "[%m/%d/%y, %I:%M:%S %p]",
                    )
                except ValueError:
                    return datetime.datetime.strptime(
                        message[0 : first_name_start - 1],
                        "[%d/%m/%Y, %I:%M:%S %p]",
                    )
        except ValueError:
            pass
        return None

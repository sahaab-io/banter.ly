import string
from collections import defaultdict
from typing import List

import constants.column_names as cn
import emoji
from datautils.stopwords import stopwords
import pandas as pd
import spacy
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from profanity_check import predict_prob as predict_prob_profane
from typing import Set

# from app import cache
from constants.profanity_labels import CLEAN, QUESTIONABLE, PROFANE
from constants.sentiment_labels import (
    SUPER_POSITIVE,
    SLIGHTLY_POSITIVE,
    POSITIVE,
    NEUTRAL,
    SLIGHTLY_NEGATIVE,
    NEGATIVE,
    SUPER_NEGATIVE,
)
from constants.topic_labels import PARTICIPANTS_LABEL, TOPIC_REDUCTION_MAP


# @cache.memoize(timeout=3000)
def process_data(
    df: pd.DataFrame, lang: str = "en"
) -> (List[pd.DataFrame], List[str]):
    """
    Adds extra columns to the dataframe passed in and generates subsets of it based on the sender
    :param df: a pandas dataframe with columns Timestamp: pandas.Timestamp | Sender: str | Raw Text: str
    :param lang: language code, default is 'en'
    :return: dfs:
    """
    # Load the language specific processing libraries
    nlp = None
    stop_words = None
    if lang == "en":
        nlp = spacy.load("en_core_web_sm")
        stop_words = stopwords(nlp, lang)

    df[cn.WORD_COUNT] = df[cn.RAW_TEXT].str.split(" ").apply(lambda l: len(l))
    df[cn.HOUR] = df[cn.TIMESTAMP].apply(lambda x: x.hour)
    df[cn.DAY] = df[cn.TIMESTAMP].apply(lambda x: x.dayofweek)
    df[cn.CLEANED_TEXT] = df[cn.RAW_TEXT].apply(
        lambda x: __clean(x, stop_words)
    )

    sia = SentimentIntensityAnalyzer()
    df[cn.SENTIMENT_SCORE] = df[cn.RAW_TEXT].apply(
        lambda x: sia.polarity_scores(x)["compound"]
    )
    df[cn.SENTIMENT_LABEL] = df[cn.SENTIMENT_SCORE].apply(
        lambda x: __label_sentiment(x)
    )
    df[cn.PROFANITY_SCORE] = df[cn.RAW_TEXT].apply(
        lambda x: predict_prob_profane([x])[0]
    )
    df[cn.PROFANITY_LABEL] = df[cn.PROFANITY_SCORE].apply(
        lambda x: __label_profanity(x)
    )

    emolex_df = pd.read_csv(
        "./data/NRC-Emotion-Intensity-Lexicon-v1.txt",
        names=["word", "emotion", "association"],
        sep="\t",
    )
    df[cn.EMOTION_LABEL] = df[cn.CLEANED_TEXT].apply(
        lambda x: __extract_emotion(x, emolex_df)
    )

    participants = list(df[cn.SENDER].unique())

    df[cn.ENTITIES] = df[cn.RAW_TEXT].apply(
        lambda x: __extract_named_entities(x, participants, nlp)
    )

    # Construct a list of participant specific dataframes
    dfs = []
    for participant in participants:
        dfs.append(df[df[cn.SENDER] == participant])

    return df, dfs, participants


def __clean(text: str, stop_words: Set[str]) -> List[str]:
    tokens = word_tokenize(text)
    # convert to lower case
    tokens = [w.lower() for w in tokens]
    # remove punctuation from each word
    table = str.maketrans("", "", string.punctuation)
    stripped = [w.translate(table) for w in tokens]
    # remove remaining tokens that are not alphabetic or emojis
    words = []
    for word in stripped:
        valid_word = True
        for char in word:
            if not (char.isalpha() or char in emoji.UNICODE_EMOJI):
                valid_word = False
        if valid_word:
            words.append(word)

    # filter out stop words and any empty stragglers
    cleaned_words = [w for w in words if not (w in stop_words or w == "")]
    # return cleaned_words
    lemmatizer = WordNetLemmatizer()

    return [lemmatizer.lemmatize(word, "v") for word in cleaned_words]


def __label_sentiment(score: float) -> str:
    if score >= 0.8:
        return SUPER_POSITIVE
    elif 0.3 <= score < 0.8:
        return POSITIVE
    elif 0.05 <= score < 0.3:
        return SLIGHTLY_POSITIVE
    elif -0.05 < score < 0.05:
        return NEUTRAL
    elif -0.05 >= score > -0.3:
        return SLIGHTLY_NEGATIVE
    elif -0.3 >= score > -0.8:
        return NEGATIVE
    elif score <= -0.8:
        return SUPER_NEGATIVE


def __label_profanity(score: float) -> str:
    """
    Matches a profanity score with a profanity label
    :param score:
    :return: A ProfanityLabel
    """
    if score <= 0.15:
        return CLEAN
    elif score < 0.3:
        return QUESTIONABLE
    else:
        return PROFANE


def __extract_named_entities(text: str, participants: List[str], spacy_nlp):
    named_entities = {}
    doc = spacy_nlp(text)
    for ent in doc.ents:
        if ent.text in participants:
            named_entities[ent.text] = PARTICIPANTS_LABEL
        else:
            named_entities[ent.text] = TOPIC_REDUCTION_MAP[ent.label_]
    return named_entities


def __extract_emotion(cleaned_text: List[str], emolex: pd.DataFrame):
    emotion_scores = defaultdict(float)
    emotion_scores["❔"] = 0.01
    for word in cleaned_text:
        matches = emolex[emolex["word"] == word]
        if len(matches) > 0:
            for match in matches.values:
                try:
                    emotion_scores[match[1]] += float(match[2])
                # There's a weird line in the emolex, this try-except is just to circumvent that
                except ValueError:
                    continue
    return max(emotion_scores, key=emotion_scores.get)

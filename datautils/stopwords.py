import spacy
from nltk.corpus import stopwords as nltk_stopwords
from typing import Set
from wordcloud import STOPWORDS


def stopwords(nlp=None, lang: str = "en") -> Set[str]:
    s = set()
    if nlp is None:
        nlp = spacy.load("en_core_web_sm")
    if lang == "en":
        s = set()
        s.update(nltk_stopwords.words("english"))
        s = s.union(nlp.Defaults.stop_words)
        s = s.union(STOPWORDS)
    return s

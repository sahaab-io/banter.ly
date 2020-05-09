NUMBERS_LABEL = "Numbers"
PEOPLE_LABEL = "People"
THINGS_LABEL = "Things"
PLACES_LABEL = "Places"
PARTICIPANTS_LABEL = "Participants"
SIMPLIFIED_LABELS = [
    PARTICIPANTS_LABEL,
    NUMBERS_LABEL,
    PEOPLE_LABEL,
    THINGS_LABEL,
    PLACES_LABEL,
]
TOPIC_REDUCTION_MAP = {
    "CARDINAL": NUMBERS_LABEL,
    "DATE": NUMBERS_LABEL,
    "EVENT": THINGS_LABEL,
    "FAC": PLACES_LABEL,
    "GPE": PLACES_LABEL,
    "LANGUAGE": PEOPLE_LABEL,
    "LAW": THINGS_LABEL,
    "LOC": PLACES_LABEL,
    "MONEY": NUMBERS_LABEL,
    "NORP": PEOPLE_LABEL,
    "ORDINAL": NUMBERS_LABEL,
    "ORG": THINGS_LABEL,
    "PERCENT": NUMBERS_LABEL,
    "PERSON": PEOPLE_LABEL,
    "PRODUCT": THINGS_LABEL,
    "QUANTITY": NUMBERS_LABEL,
    "TIME": NUMBERS_LABEL,
    "WORK_OF_ART": THINGS_LABEL,
}
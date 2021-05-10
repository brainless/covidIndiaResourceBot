from typing import List
from fuzzywuzzy import process


def match_response_in_list(
    message: str,
    allowed_responses: List[str]
):
    lowered = message.lower()
    for allowed in allowed_responses:
        if lowered == allowed.lower():
            return allowed

    raise ValueError


def fuzzy_match_response_in_list(
    message: str,
    allowed_responses: List[str]
):
    lowered = message.lower()
    matches = process.extractOne(lowered, allowed_responses)

    if matches and matches[1] >= 90:
        return matches[0]

    raise ValueError


def match_response_code_in_list(
    message: str,
    allowed_responses: List[str]
):
    try:
        code = int(message)
        if 0 < code < len(allowed_responses) + 2:
            return allowed_responses[code - 1]
    except ValueError:
        pass

    raise ValueError


def match_response_as_place_name_in_india(message: str):
    raise ValueError


def match_response_as_spo2_level(message: str):
    try:
        spo2_level = int(message)
        return spo2_level
    except ValueError:
        pass

    raise ValueError

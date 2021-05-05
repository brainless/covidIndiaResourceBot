from typing import List


def match_response_in_list(message: str, allowed_responses: List[str]):
    if message in allowed_responses:
        return message.lower()

    raise ValueError


def match_response_code_in_list(message: str, allowed_responses: List[str]):
    try:
        code = int(message)
        if 0 < code < len(allowed_responses) + 2:
            return allowed_responses[code - 1].lower()
    except ValueError:
        pass

    raise ValueError

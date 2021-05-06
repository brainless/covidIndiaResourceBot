from typing import Optional, List

from apps.chat import parsers
from apps.chat.state import Cacheable


class ChatVariables(Cacheable):
    looking_for: Optional[str]
    location: Optional[str]
    spo2_level: Optional[int]
    team: Optional[str]
    tags: Optional[List[str]]

    def __init__(self):
        self.looking_for = None
        self.location = None
        self.spo2_level = None
        self.team = None
        self.tags = []

    @classmethod
    def parse_welcome_response(cls, current_variables, parsed_response):
        if cls.__name__ == "ChatVariables":
            current_variables.team = parsed_response
            current_variables.tags.append(parsed_response)
        return current_variables


resources = [
    "Blood banks",
    "Ambulances",
    "Helplines",
    "Plasma",
    "Medicines",
    "Oxygen",
    "Beds",
    "Food",
    "Consultation"
    "Mental Health",
    "Vaccine",
    "Regional PoCs",
    "Something else"
]


def get_resources_list():
    return "\n".join(["{} {}".format(index, x) for index, x in enumerate(resources)])


welcome_message = """Hey, thank you for reaching. Can you please tell me what you are looking for from below options?

{}

Just press the number, 1 to 13
""".format(get_resources_list())

city_message = """Thank you.

Could you also please tell me which city or region the patient is?
"""

spo2_message = """And what is the SPO2 level?
"""

flow_config = {
    "steps": {
        "welcome": {
            "message": welcome_message,
            "allowed_parsers": [parsers.match_response_in_list, parsers.match_response_code_in_list],
            "success_state": "city",
            "failure_state": "welcome_failure",
            "parser_parameters": {
                "allowed_responses": resources
            },
            "parser_output_handler": ChatVariables.parse_welcome_response
        },
        "welcome_failure": {
            "inherit_step": "welcome",
            "message": "Please select a valid option. Eg. reply 2 for Ambulances.",
            "max_tries": 3,
        },
        "city": {
            "message": city_message,
            "allowed_parsers": [parsers.match_response_as_place_name_in_india]
        },
        "spo2": {
            "message": spo2_message,
            "allowed_parsers": []
        }
    },
    "chat_variables_class": ChatVariables,
    "start_at": "welcome"
}

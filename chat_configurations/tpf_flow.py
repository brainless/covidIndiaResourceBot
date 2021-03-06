from typing import Optional, List

from apps.chat import parsers
from apps.chat.state import Cacheable


resources_need_spo2 = [
    "Ambulances",
    "Oxygen",
    "Beds",
]

resources_dont_need_spo2 = [
    "Blood banks",
    "Helplines",
    "Medicines",
    "Plasma",
    "Consultation"
    "Food",
    "Mental Health",
    "Vaccine",
    "Regional PoCs",
    "Something else"
]

resources = resources_need_spo2 + resources_dont_need_spo2


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
    def store_welcome_response(cls, current_variables: "ChatVariables", parsed_response):
        if cls.__name__ == "ChatVariables" and parsed_response:
            current_variables.looking_for = parsed_response
            tags = set(current_variables.tags)
            tags.add(parsed_response)
            current_variables.tags = list(tags)
        return current_variables

    @classmethod
    def skip_spo2_step(cls, current_variables: "ChatVariables"):
        if cls.__name__ == "ChatVariables":
            if current_variables.looking_for in resources_dont_need_spo2:
                return True
        return False

    @classmethod
    def store_spo2_response(cls, current_variables: "ChatVariables", parsed_response):
        if cls.__name__ == "ChatVariables" and parsed_response:
            current_variables.spo2_level = parsed_response
            tags = set(current_variables.tags)
            spo2_tag = ""
            if parsed_response >= 95:
                spo2_tag = "normal"
            elif parsed_response >= 92:
                spo2_tag = "medium"
            elif parsed_response >= 86:
                spo2_tag = "low"
            elif parsed_response >= 80:
                spo2_tag = "needs-care"
            else:
                spo2_tag = "critical"
            tags.add("spo2:{}".format(spo2_tag))
            current_variables.tags = list(tags)
        return current_variables

    @classmethod
    def skip_blood_group_step(cls, current_variables: "ChatVariables"):
        if cls.__name__ == "ChatVariables":
            if current_variables.looking_for == "Plasma":
                return False
        return True

    @classmethod
    def store_blood_group_response(cls, current_variables: "ChatVariables", parsed_response: str):
        if cls.__name__ == "ChatVariables" and parsed_response:
            base_groups = ["A", "B", "AB", "O"]
            groups = ["{}+".format(x) for x in base_groups] + ["{}-".format(x) for x in base_groups]

            if parsed_response.upper() in groups:
                tags = set(current_variables.tags)
                tags.add(parsed_response.upper())
                current_variables.tags = list(tags)
        return current_variables

    @classmethod
    def set_team(cls, current_variables: "ChatVariables"):
        if cls.__name__ == "ChatVariables":
            current_variables.team = "Default"
        return current_variables


def get_resources_list():
    return "\n".join(["{} {}".format(index + 1, x) for index, x in enumerate(resources)])


welcome_message = """Hey, 
Please select your requirement from the options below so that we can direct you to the volunteer that can help you most:

{}

Just press the number, 1 to 12
""".format(get_resources_list())

city_message = """Thank you.

Could you also please tell me which city or region the patient is?
"""

spo2_message = """And what is the SPO2 level?
"""

spo2_failure_message = """Sorry I could not understand.
The SPO2 is the Oxygen saturation level as provided by the Doctor.
Can you please share the SPO2 number?
"""

blood_group_message = """What is the blood group of the patient? (need it for Plasma information)
"""


volunteer_message = """Please give us 2 minutes to get back to you within this chat
"""

flow_config = {
    "steps": {
        "welcome": {
            "message": welcome_message,
            "allowed_parsers": [
                parsers.match_response_code_in_list,
                parsers.match_response_in_list,
                parsers.fuzzy_match_response_in_list
            ],
            "success_step": "city",
            "failure_step": "welcome_failure",
            "parser_parameters": {
                "allowed_responses": resources
            },
            "parser_output_handler": ChatVariables.store_welcome_response,
        },
        "welcome_failure": {
            "inherit_step": "welcome",
            "message": "Please select a valid option. Eg. reply 2 for Ambulances.",
        },
        "city": {
            "message": city_message,
            "allowed_parsers": [parsers.match_response_as_place_name_in_india],
            "success_step": "spo2",
            "failure_step": "spo2",
        },
        "spo2": {
            "message": spo2_message,
            "skip_step_condition": ChatVariables.skip_spo2_step,
            "allowed_parsers": [parsers.match_response_as_spo2_level],
            "parser_output_handler": ChatVariables.store_spo2_response,
            "success_step": "blood_group",
            "failure_step": "spo2_failure",
            "skip_step": "blood_group",
        },
        "spo2_failure": {
            "inherit_step": "spo2",
            "message": spo2_failure_message
        },
        "blood_group": {
            "message": blood_group_message,
            "skip_step_condition": ChatVariables.skip_blood_group_step,
            "allowed_parsers": [parsers.match_response_as_string],
            "parser_output_handler": ChatVariables.store_blood_group_response,
            "success_step": "volunteer",
            "failure_step": "volunteer",
            "skip_step": "volunteer",
        },
        "volunteer": {
            "message": volunteer_message,
            "pre_message": ChatVariables.set_team,
        }
    },
    "chat_variables_class": ChatVariables,
    "max_failures": 2,
    "start_at": "welcome"
}

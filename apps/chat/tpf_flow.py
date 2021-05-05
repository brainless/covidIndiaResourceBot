from . import parsers

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
            "success_state": "",
            "failure_state": "",
            "variables": {
                "allowed_responses": resources
            }
        },
        "city": {
            "message": city_message,
            "allowed_parsers": []
        },
        "spo2": {
            "message": spo2_message,
            "allowed_parsers": []
        }
    },
    "start_at": "welcome"
}

from datetime import datetime
from typing import Optional


welcome_message = """Hey, thank you for reaching. Can you please tell me what you are looking for from below options?

1 Blood banks
2 Ambulances
3 Helplines
4 Plasma
5 Medicines
6 Oxygen
7 Beds
8 Food
9 Consultation
10 Mental Health
11 Vaccine
12 Regional PoCs or something else

Just press the number, 1 to 12
"""


def get_next_message(
        looking_for: Optional[str] = None,
        city: Optional[str] = None,
        spo2_level: Optional[int] = None,
        operator_has_replied: Optional[bool] = False,
        last_response_at: Optional[datetime] = datetime.utcnow()
):
    if operator_has_replied:
        return None

    if looking_for is None and city is None and spo2_level is None:
        return welcome_message

    return None

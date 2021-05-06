from typing import Optional

from apps.chat.state import ChatState


def get_next_message(
        config: dict,
        created_by: str,
        current_message: Optional[str],
        chat_state: ChatState
):
    response_message = None
    if chat_state.operator_has_replied or created_by == "operator":
        chat_state.operator_has_replied = True
        return response_message, chat_state

    if chat_state.current_step is None:
        chat_state.current_step = config["start_at"]

    step_config = config["steps"][chat_state.current_step]
    if "inherit_step" in step_config:
        parent_step_config = config["steps"][step_config["inherit_step"]]
        step_config = {
            **parent_step_config,
            **step_config,
        }

    if chat_state.has_sent_current_step_message:
        # We have sent out the message for the current step
        # We now expect a response from user, so lets run parsers and see if we find a valid response
        is_successful = False
        for message_parser in step_config["allowed_parsers"]:
            try:
                message_parser(current_message, **step_config["variables"])
                # Found a valid response, move the step to success
                is_successful = True
                break
            except ValueError:
                # We do not do anything when any one parser fails, just ignore and try next
                pass

        can_move_step = False
        if is_successful:
            if "success_state" in step_config:
                chat_state.current_step = step_config["success_state"]
                can_move_step = True
            else:
                response_message = None
        else:
            # We tried all parsers, none worked so we are in failure step of the current step
            if "failure_state" in step_config:
                chat_state.current_step = step_config["failure_state"]
                can_move_step = True
            else:
                response_message = None

        if can_move_step:
            # Let's start over, but with the success or failed step
            # This will simply send out the message
            chat_state.has_sent_current_step_message = False
            response_message, chat_state = get_next_message(
                config=config,
                current_message=None,
                chat_state=chat_state
            )
    else:
        # We have not sent out the message configured for this current step, let's send it out
        response_message = step_config["message"]
        if "max_tries" in step_config:
            if chat_state.tried_this_step >= step_config["max_tries"]:
                response_message = None
        chat_state.has_sent_current_step_message = True
        chat_state.tried_this_step = chat_state.tried_this_step + 1

    return response_message, chat_state

from typing import Optional

from apps.chat.state import ChatState, Cacheable


def get_next_message(
        flow_config: dict,
        created_by: str,
        current_message: Optional[str],
        chat_state: ChatState,
        chat_variables: Cacheable
) -> [Optional[str], ChatState]:
    response_message = None
    if chat_state.has_operator_replied or created_by == "operator":
        chat_state.has_operator_replied = True
        return response_message, chat_state

    if chat_state.current_step is None:
        chat_state.current_step = flow_config["start_at"]

    step_config = flow_config["steps"][chat_state.current_step]
    if "inherit_step" in step_config:
        parent_step_config = flow_config["steps"][step_config["inherit_step"]]
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
                if "parser_parameters" in step_config:
                    parser_output = message_parser(current_message, **step_config["parser_parameters"])
                else:
                    parser_output = message_parser(current_message)
                # Found a valid response, move the step to success
                is_successful = True
                if "parser_output_handler" in step_config and "chat_variables_class" in flow_config:
                    step_config["parser_output_handler"](chat_variables, parser_output)
                break
            except ValueError:
                # We do not do anything when any one parser fails, just ignore and try next
                pass

        can_move_step = False
        if is_successful:
            if "success_step" in step_config:
                chat_state.current_step = step_config["success_step"]
                can_move_step = True
            else:
                response_message = None
        else:
            # We tried all parsers, none worked so we are in failure step of the current step
            if "failure_step" in step_config:
                chat_state.current_step = step_config["failure_step"]
                can_move_step = True
            else:
                response_message = None

        if can_move_step:
            # Let's start over, but with the success or failed step
            # This will simply send out the message
            chat_state.has_sent_current_step_message = False
            response_message, chat_state = get_next_message(
                flow_config=flow_config,
                created_by=created_by,
                current_message=None,
                chat_state=chat_state,
                chat_variables=chat_variables
            )
    else:
        # We have not sent out the message configured for this current step, let's send it out
        response_message = step_config["message"]
        """
        if "max_tries" in step_config:
            if chat_state.tried_this_step >= step_config["max_tries"]:
                response_message = None
        """
        chat_state.has_sent_current_step_message = True
        chat_state.tried_this_step = chat_state.tried_this_step + 1

    return response_message, chat_state

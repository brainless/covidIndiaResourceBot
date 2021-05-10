from typing import Optional

from apps.chat.state import ChatState, Cacheable


def get_next_message(
        flow_config: dict,
        created_by: str,
        current_message: Optional[str],
        chat_state: ChatState,
        chat_variables: Cacheable
) -> [Optional[str], ChatState, Cacheable]:
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
        if "allowed_parsers" in step_config:
            for message_parser in step_config["allowed_parsers"]:
                try:
                    if "parser_parameters" in step_config:
                        parser_output = message_parser(current_message, **step_config["parser_parameters"])
                    else:
                        parser_output = message_parser(current_message)
                    # Found a valid response, move the step to success
                    is_successful = True
                    if "parser_output_handler" in step_config and "chat_variables_class" in flow_config:
                        chat_variables = step_config["parser_output_handler"](chat_variables, parser_output)
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
            chat_state.failures_count = chat_state.failures_count + 1
            if "failure_step" in step_config:
                chat_state.current_step = step_config["failure_step"]
                can_move_step = True
            else:
                response_message = None

        if can_move_step:
            # Let's start over, but with the success or failed step
            # This will simply send out the message
            chat_state.has_sent_current_step_message = False
            response_message, chat_state, chat_variables = get_next_message(
                flow_config=flow_config,
                created_by=created_by,
                current_message=None,
                chat_state=chat_state,
                chat_variables=chat_variables
            )
    else:
        # We have not sent out the message configured for this current step, let's send it out
        is_skipped = False
        if "skip_step_condition" in step_config and "skip_step" in step_config:
            # A step condition means we need to check if we are allowed to run this step on not
            if step_config["skip_step_condition"](chat_variables):
                chat_state.current_step = step_config["skip_step"]
                chat_state.has_sent_current_step_message = False
                response_message, chat_state, chat_variables = get_next_message(
                    flow_config=flow_config,
                    created_by=created_by,
                    current_message=None,
                    chat_state=chat_state,
                    chat_variables=chat_variables
                )
                is_skipped = True

        if not is_skipped:
            response_message = step_config["message"]
            if "pre_message" in step_config and "chat_variables_class" in flow_config:
                chat_variables = step_config["pre_message"](chat_variables)

        chat_state.has_sent_current_step_message = True

    if "max_failures" in flow_config:
        if chat_state.failures_count >= flow_config["max_failures"]:
            response_message = None

    return response_message, chat_state, chat_variables

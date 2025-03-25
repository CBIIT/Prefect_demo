from prefect import flow, get_run_logger
from typing import Literal


def birthday_message(name="user", celebration=False):
    logger = get_run_logger()
    """
    Prints a birthday message. 
    """
    message = f"Happy Birthday {name}" if name != "user" else "Happy Birthday to you"

    if celebration == "yes":
        kirby_left = "<(^O^<)"
        kirby_right = "(>^O^)>"
        logger.info(f"{kirby_left} {kirby_left} {message} {kirby_right} {kirby_right}")
    else:
        logger.info(message)


DropDownChoices = Literal["yes", "no"]



@flow(
    name="Happy_Birthday",
    log_prints=True,
    flow_run_name="happy_birthday...",
)
def runner(user_name: str, celebration_mode: DropDownChoices):
    """
    Prints a birthday message.
    If no name is provided, defaults to "user" and prints "Happy Birthday to you".
    If celebration_mode is True, surrounds the message with dancing Kirby emojis.

    Args:
        user_name (str): The name of the person. Defaults to "user".
        celebration_mode (DropDownChoices): Whether to enable celebration mode. Defaults to False.
    """

    birthday_message(name=user_name, celebration=celebration_mode)

if __name__=="__main__":
    runner(user_name="Max", celebration_mode="yes")
def birthday_message(name="user", celebration_mode=False):
    """
    Prints a birthday message. 
    
    If no name is provided, defaults to "user" and prints "Happy Birthday to you".
    If celebration is True, surrounds the message with dancing Kirby emojis.
    
    Args:
        name (str): The name of the person. Defaults to "user".
        celebration (bool): Whether to enable celebration mode. Defaults to False.
    """
    message = f"Happy Birthday {name}" if name != "user" else "Happy Birthday to you"
    
    if celebration:
        kirby_left = "<(^O^<)"
        kirby_right = "(>^O^)>"
        print(f"{kirby_left} {kirby_left} {message} {kirby_right} {kirby_right}")
    else:
        print(message)


# Example usage:
if __name__ == "__main__":
    # Example: Enter name and celebration mode
    person_name = input("Enter the person's name (leave blank for default): ").strip() or "user"
    celebration = input("Enable celebration mode? (yes/no): ").strip().lower() == "yes"
    
    # Print the birthday message
    birthday_message(name=person_name, celebration_mode=celebration)

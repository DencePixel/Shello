async def replace_variable_welcome(message, replacements):
    """Welcome Variable Function

    Args:
        message (_type_): _description_
        replacements (_type_): _description_

    Returns:
        _type_: _description_
        
    Why:
        So that variables work in the welcome message.
    """
    for placeholder, value in replacements.items():
        message = message.replace(placeholder, value)
    return message





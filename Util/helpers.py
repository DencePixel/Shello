import datetime
import typing
import discord
from discord import Embed, InteractionResponse, Webhook
import re
from Cogs.emojis import approved_emoji, denied_emoji

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




def convert_duration(duration_str):
    duration_str = duration_str.lower()
    match = re.match(r'(\d+)([dwmhms]{1,2}|mi|s)', duration_str)
    
    if not match:
        raise ValueError("Invalid duration format. Please use a valid format like 1D, 2W, 3M, 4H.")
    
    amount, unit = match.groups()
    amount = int(amount)
    
    if unit == 'd':
        return datetime.datetime.now() + datetime.timedelta(days=amount)
    elif unit == "mi":
        return datetime.datetime.now() + datetime.timedelta(minutes=amount)
    elif unit == "s":
        return datetime.datetime.now() + datetime.timedelta(seconds=amount)
    elif unit == 'w':
        return datetime.datetime.now() + datetime.timedelta(weeks=amount)
    elif unit == 'm':
        return datetime.datetime.now() + datetime.timedelta(days=30 * amount)
    elif unit == 'h':
        return datetime.datetime.now() + datetime.timedelta(hours=amount)
    else:
        raise ValueError("Invalid duration unit. Please use one of D, W, M, H, S, or MI.")
    
    
async def interaction_check_failure(responder: typing.Union[InteractionResponse, Webhook, typing.Callable]):
    if isinstance(responder, typing.Callable):
        responder = responder()

    if isinstance(responder, InteractionResponse):
        await responder.send_message(content=f"{denied_emoji} You can't use these buttons.")
    else:
        await responder.send(content=f"{denied_emoji} You can't use these buttons.")


import discord
from jsonschema import validate, exceptions
import sqlite3
import json

def update_existing_entry(cursor, guild_id, channel_id):
    cursor.execute("UPDATE design SET channel_id = ? WHERE guild_id = ?", (channel_id, guild_id))

def validate_existing_guild(cursor, guild_id):
    cursor.execute("SELECT guild_id FROM design WHERE guild_id = ?", (guild_id,))
    row = cursor.fetchone()
    if row:
        raise exceptions.ValidationError("Design entry already exists for this guild.")

def insert_or_replace_design_info(cursor, guild_id, channel_id):
    cursor.execute("INSERT OR REPLACE INTO design (guild_id, channel_id) VALUES (?, ?)", (guild_id, channel_id))

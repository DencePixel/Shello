import sqlite3
import json
from jsonschema import validate, exceptions

def create_tickets_table(conn):
    with open('Data/DesignLog/Designer_Role/schema.json') as schema_file:
        schema = json.load(schema_file)

    try:
        validate_tickets(schema)
    except exceptions.ValidationError as e:
        print(f"Design validation failed: {e}")
        return

    cur = conn.cursor()

    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='design'")
    table_exists = cur.fetchone()

    if table_exists:
        print("Table 'design' already exists.")
    else:
        cur.execute('''
            CREATE TABLE design (
                guild_id INTEGER PRIMARY KEY,
                role_id INTEGER
            )
        ''')
        print("Created 'design' table.")

    conn.commit()
    cur.close()

def validate_tickets(schema):
    with open('Data/DesignLog/Designer_Role/base.json') as tickets_file:
        tickets = json.load(tickets_file)

    validate(tickets, schema)

def get_existing_guild_id(cursor):
    cursor.execute("SELECT guild_id FROM design")
    row = cursor.fetchone()
    return row[0] if row else None

if __name__ == '__main__':
    conn = sqlite3.connect('Data/DesignLog/Designer_Role/DesignerRole.sql')
    create_tickets_table(conn)
    conn.close()




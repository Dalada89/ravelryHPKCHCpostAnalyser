import json
import mysql.connector

tables = {
    "posts": "presented_projects",
    "classes": "classes"
}


def connect_to_database():
    """
    Initialise the connection to the database
    """

    with open('credentials.json', 'r') as file:
        credentials = json.load(file)

    mydb = mysql.connector.connect(
        host=credentials['database']['host'],
        database=credentials['database']['database'],
        user=credentials['database']['user'],
        password=credentials['database']['password']
    )

    return mydb

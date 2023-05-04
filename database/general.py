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


def extract_data_from_curser(mycursor):
    results = []
    columns = [column[0] for column in mycursor.description]
    myresults = mycursor.fetchall()
    for row in myresults:
        element_dict = {}
        for index, element in enumerate(row):
            if type(element) == bytes:
                element = json.loads(element)
            element_dict[columns[index]] = element
        results.append(element_dict)

    return results

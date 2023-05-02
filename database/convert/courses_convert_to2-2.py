import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path.cwd()))
from database import general  # noqa: E402

table = 'courses'


def create_table():
    """
    Im creating this table
    """
    mydb = general.connect_to_database()
    mycursor = mydb.cursor()

    sql = "DROP TABLE IF EXISTS " + table + ";"
    mycursor.execute(sql)

    sql = "CREATE TABLE {table} ( \
            id INTEGER PRIMARY KEY AUTO_INCREMENT, \
            ravelry_id INTEGER UNIQUE NOT NULL, \
            title VARCHAR(256), \
            term VARCHAR(32), \
            active json, \
            mode INTEGER, \
            tracked_by VARCHAR(128), \
            type VARCHAR(32), \
            base_points INTEGER, \
            last_post INTEGER);"

    mycursor.execute(sql.format(table=table))
    mycursor.close()
    mydb.close()


def get_old():
    """
    Im getting the courses from the  old table
    """
    mydb = general.connect_to_database()
    mycursor = mydb.cursor()

    sql = "SELECT * FROM {table};".format(table=table)
    mycursor.execute(sql)

    data = general.extract_data_from_curser(mycursor)

    mydb.commit()
    mycursor.close()
    mydb.close()

    return data


def convert_data(data):
    for el in data:
        el.pop('id')
        el.pop('month')
        el['active'] = [
            [el.pop('start'), el.pop('end')]
        ]
        el['type'] = el['type'].lower()

    return data


def insert(data):
    """
    This function shall insert all course into the new table
    """
    mydb = general.connect_to_database()
    mycursor = mydb.cursor()

    for course in data:
        course['active'] = json.dumps(course['active'])

        placeholder = ", ".join(["%s"] * len(course))
        sql = "INSERT INTO `{table}` ({columns}) VALUES ({values});"
        sql = sql.format(table=table, columns=",".join(course.keys()), values=placeholder)

        mycursor.execute(sql, list(course.values()))

    mydb.commit()
    mycursor.close()
    mydb.close()


def convert_courses_table():
    """
    This function shall convert the course table to version 2.2
    """
    data = get_old()
    data = convert_data(data)
    create_table()
    insert(data)


def main():
    convert_courses_table()


if __name__ == '__main__':
    main()

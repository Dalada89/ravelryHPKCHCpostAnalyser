from pathlib import Path
import sys
cwd = str(Path.cwd())
if cwd not in sys.path:
    sys.path.insert(0, cwd)
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
            month VARCHAR(32), \
            active INTEGER, \
            tracked_by INTEGER, \
            type VARCHAR(32), \
            base_points INTEGER, \
            last_post INTEGER);"

    mycursor.execute(sql.format(table=table))
    mycursor.close()
    mydb.close()


def get(filter=None, mycursor=None):
    """
    Im getting the classes from the table
    """
    close_connection = False
    if mycursor is None:
        mydb = general.connect_to_database()
        mycursor = mydb.cursor()
        close_connection = True
    
    if filter is not None:
        sqlfilter = ''
        for key in filter:
            if type(filter[key]) in [int, float]:
                sqlfilter += '{key}={val} AND '.format(key=key, val=filter[key])
            else:
                sqlfilter += "{key}='{val}' AND ".format(key=key, val=filter[key])
        sqlfilter = sqlfilter[0:-5]
        sql = "SELECT * FROM {table} WHERE {filter};".format(table=table, filter=sqlfilter)
    else:
        sql = "SELECT * FROM {table};".format(table=table)
    mycursor.execute(sql)

    data = general.extract_data_from_curser(mycursor)

    if close_connection:
        mydb.commit()
        mycursor.close()
        mydb.close()
    
    return data


def insert(course, mycursor=None):
    """
    This function shall insert a class into the database
    """
    close_connection = False
    if mycursor is None:
        mydb = general.connect_to_database()
        mycursor = mydb.cursor()
        close_connection = True

    if 'id' in course:
        course.pop('id')

    placeholder = ", ".join(["%s"] * len(course))
    sql = "INSERT INTO `{table}` ({columns}) VALUES ({values});".format(table=table, columns=",".join(course.keys()),
                                                                        values=placeholder)
    mycursor.execute(sql, list(course.values()))

    if close_connection:
        mydb.commit()
        mycursor.close()
        mydb.close()


def update(course, mycursor=None):
    """
    Function to update an existing clusters in the database
    """
    close_connection = False
    if mycursor is None:
        mydb = general.connect_to_database()
        mycursor = mydb.cursor()
        close_connection = True

    # id and ravelry_id should not be updated
    course.pop('id')
    ravelry_id = course.pop('ravelry_id')
    
    varset = ''
    for key in course:
        if type(course[key]) in [int, float]:
            varset += '{key}={val}, '.format(key=key, val=course[key])
        else:
            varset += "{key}='{val}', ".format(key=key, val=course[key])
    varset = varset[0:-2]

    sql = "UPDATE {table} SET {set} WHERE ravelry_id='{id}';".format(table=table, set=varset, id=ravelry_id)
    mycursor.execute(sql)

    if close_connection:
        mydb.commit()
        mycursor.close()
        mydb.close()


def delete(ravelry_id: int, mycursor=None):
    """
    Function to delete an entry
    """

    close_connection = False
    if mycursor is None:
        mydb = general.connect_to_database()
        mycursor = mydb.cursor()
        close_connection = True

    sql = "DELETE FROM {table} WHERE ravelry_id = {id}"
    sql = sql.format(table=table, id=ravelry_id)

    mycursor.execute(sql)

    if close_connection:
        mydb.commit()
        mycursor.close()
        mydb.close()
    
    return True

import warnings
from database import general


table = 'turn_ins'


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
            ravelry_id INTEGER NOT NULL, \
            post_id INTEGER NOT NULL, \
            name VARCHAR(256) NOT NULL, \
            house VARCHAR(64) NOT NULL, \
            date INTEGER NOT NULL, \
            project VARCHAR(64), \
            verb VARCHAR(64), \
            points INTEGER, \
            status VARCHAR(64), \
            UNIQUE KEY unique_ravelry_post (ravelry_id, post_id));"

    mycursor.execute(sql.format(table=table))
    mycursor.close()
    mydb.close()


def get(filter=None, mycursor=None, start=None, end=None):
    """
    Im getting the classes from the table
    input:
    - filter: dict,
    - mycursor,
    - start: timestamp (int)
    - end: timestamp (int)

    output: list of dicts
    """
    close_connection = False
    if mycursor is None:
        mydb = general.connect_to_database()
        mycursor = mydb.cursor()
        close_connection = True

    sqlfilter = ''
    if filter is not None:
        if 'date' in filter and (start != None or end != None):
            warnings.warn('You can only filter with a date or with a range [start, end], but not both. I will ignore the filter[date].')
            filter.pop('date')

        for key in filter:
            if type(filter[key]) in [int, float]:
                sqlfilter += '{key}={val} AND '.format(key=key, val=filter[key])
            else:
                sqlfilter += "{key}='{val}' AND ".format(key=key, val=filter[key])
        sqlfilter = sqlfilter[0:-5]
        if sqlfilter != '':
            sql = "SELECT * FROM {table} WHERE {filter}"
        else:
            sql = "SELECT * FROM {table}"
    else:
        sql = "SELECT * FROM {table}"

    sql = sql.format(table=table, filter=sqlfilter)
    sql_add = ''
    if start != None and end != None:
        sql_add = 'date BETWEEN {s} AND {e}'
    elif start != None:
        sql_add = 'date > {s}'
    elif end != None:
        sql_add = 'date < {e}'
    sql_add = sql_add.format(s=start, e=end)
    if sql_add != '':
        if sql.find('WHERE') == -1:
            sql = sql + ' WHERE ' + sql_add
        else:
            sql = sql + ' AND ' + sql_add 
    sql += ';'

    mycursor.execute(sql)

    data = general.extract_data_from_curser(mycursor)

    if close_connection:
        mydb.commit()
        mycursor.close()
        mydb.close()
    
    return data


def insert(turn_in, mycursor=None):
    """
    This function shall insert a class into the database
    """
    close_connection = False
    if mycursor is None:
        mydb = general.connect_to_database()
        mycursor = mydb.cursor()
        close_connection = True

    if 'id' in turn_in:
        turn_in.pop('id')

    placeholder = ", ".join(["%s"] * len(turn_in))
    sql = "INSERT INTO `{table}` ({columns}) VALUES ({values});".format(table=table, columns=",".join(turn_in.keys()),
                                                                        values=placeholder)
    mycursor.execute(sql, list(turn_in.values()))

    if close_connection:
        mydb.commit()
        mycursor.close()
        mydb.close()


def update(turn_in, mycursor=None):
    """
    Function to update an existing clusters in the database
    """
    close_connection = False
    if mycursor is None:
        mydb = general.connect_to_database()
        mycursor = mydb.cursor()
        close_connection = True

    # id should not be updated
    id = turn_in.pop('id')
    
    varset = ''
    for key in turn_in:
        if type(turn_in[key]) in [int, float]:
            varset += '{key}={val}, '.format(key=key, val=turn_in[key])
        else:
            varset += "{key}='{val}', ".format(key=key, val=turn_in[key])
    varset = varset[0:-2]

    sql = "UPDATE {table} SET {set} WHERE id='{id}';".format(table=table, set=varset, id=id)
    mycursor.execute(sql)

    if close_connection:
        mydb.commit()
        mycursor.close()
        mydb.close()


def delete(id: int, mycursor=None):
    """
    Function to delete an entry
    """

    close_connection = False
    if mycursor is None:
        mydb = general.connect_to_database()
        mycursor = mydb.cursor()
        close_connection = True

    sql = "DELETE FROM {table} WHERE id = {id}"
    sql = sql.format(table=table, id=id)

    mycursor.execute(sql)

    if close_connection:
        mydb.commit()
        mycursor.close()
        mydb.close()
    
    return True

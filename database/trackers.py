from database import general


table = 'trackers'


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
            name varchar(128) NOT NULL, \
            mail VARCHAR(256), \
            updated INTEGER);"

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
        sql = "SELECT * FROM {table}".format(table=table)
    mycursor.execute(sql)

    data = general.extract_data_from_curser(mycursor)

    if close_connection:
        mydb.commit()
        mycursor.close()
        mydb.close()
    
    return data


def insert(tracker, mycursor=None):
    """
    This function shall insert a class into the database
    """
    close_connection = False
    if mycursor is None:
        mydb = general.connect_to_database()
        mycursor = mydb.cursor()
        close_connection = True

    if 'id' in tracker:
        tracker.pop('id')

    placeholder = ", ".join(["%s"] * len(tracker))
    sql = "INSERT INTO `{table}` ({columns}) VALUES ({values});".format(table=table, columns=",".join(tracker.keys()),
                                                                        values=placeholder)
    mycursor.execute(sql, list(tracker.values()))

    if close_connection:
        mydb.commit()
        mycursor.close()
        mydb.close()


def update(tracker, mycursor=None):
    """
    Function to update an existing clusters in the database
    """
    close_connection = False
    if mycursor is None:
        mydb = general.connect_to_database()
        mycursor = mydb.cursor()
        close_connection = True

    # id and ravelry_id should not been updated
    id = tracker.pop('id')
    
    varset = ''
    for key in tracker:
        if type(tracker[key]) in [int, float]:
            varset += '{key}={val}, '.format(key=key, val=tracker[key])
        else:
            varset += "{key}='{val}', ".format(key=key, val=tracker[key])
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

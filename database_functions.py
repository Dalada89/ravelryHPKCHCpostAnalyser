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


def store_posts(list_of_posts):
    """
    Stores the posts in the database. If the post is already stored, the database will be updated.
    If it is a new post, it will be inserted into the database.
    """

    mydb = connect_to_database()
    mycursor = mydb.cursor()
    inc = {
        'new': 0,
        'updated': 0
    }
    for post in list_of_posts:
        if len(get_post(mycursor, post['class_id'], post['post_id'])) == 0:
            insert_post(mycursor, post)
            inc['new'] += 1
        else:
            update_post(mycursor, post)
            inc['updated'] += 1

    mydb.commit()

    print(str(inc['new']) + "record inserted and " + str(inc['updated']) + " updated.")


def insert_post(mycursor, data):
    """
    Insert a post to the database
    """

    sql = "INSERT INTO " + tables['posts'] + " (class_id, post_id, name, house, date, project, verb, loved, url) " + \
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
    val = (
        data['class_id'],
        data['post_id'],
        data['name'],
        data['house'],
        data['date'],
        data['project'],
        data['verb'],
        data['loved'],
        data['url'])
    mycursor.execute(sql, val)


def update_post(mycursor, data):
    """
    Updates a post to the database
    """

    sql = "UPDATE " + tables['posts'] + " " + \
          "SET project = %s, " + \
              "verb = %s, " + \
              "loved = %s " + \
          "WHERE class_id = " + str(data['class_id']) + " AND post_id = " + str(data['post_id'])  # noqa: E127

    val = (
        data['project'],
        data['verb'],
        data['loved']
    )
    mycursor.execute(sql, val)


def get_post(mycursor, class_id, post_id):
    """
    Reads a single post from the database
    """

    sql = "SELECT * FROM " + tables['posts'] + " " + \
          "WHERE class_id = " + str(class_id) + " AND post_id = " + str(post_id)

    mycursor.execute(sql)

    myresult = mycursor.fetchall()
    list_of_posts = []
    for row in myresult:
        post = {
            'id': row[0],
            'class_id': int(row[1]),
            'post_id': int(row[2]),
            'name': row[3],
            'house': row[4],
            'date': int(row[5]),
            'project': row[6],
            'verb': row[7],
            'loved': int(row[8]),
            'url': row[9]}
        list_of_posts.append(post)

    return list_of_posts


def read_posts(list_class_ids, start_date, end_date):
    """
    """
    mydb = connect_to_database()
    mycursor = mydb.cursor()

    list_of_posts = []
    for class_id in list_class_ids:
        sql = "SELECT * FROM " + tables['posts'] + " " + \
          "WHERE class_id = " + str(class_id) + " AND " + \
          "date BETWEEN " + str(start_date) + " AND " + str(end_date)
        # print(sql)
        mycursor.execute(sql)

        myresult = mycursor.fetchall()

        for row in myresult:
            post = {
                'id': row[0],
                'class_id': int(row[1]),
                'post_id': int(row[2]),
                'name': row[3],
                'house': row[4],
                'date': int(row[5]),
                'project': row[6],
                'verb': row[7],
                'loved': int(row[8]),
                'url': row[9]}
            list_of_posts.append(post)

    return list_of_posts

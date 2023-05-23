import mysql.connector
from database import submissions, courses, general
from analysis import course_pages
from report import inform_users, nextcloud_report
import manage_courses


def main():
    info_to_send = {}
    info_to_send['new_courses'] = manage_courses.add_courses()
    class_pages = courses.get(filter={'mode': 1})
    database = course_pages.analyse_game_pages(class_pages)

    mydb = general.connect_to_database()
    mycursor = mydb.cursor()
    for entry in database:
        try:
            submissions.insert(entry, mycursor=mycursor)
        except mysql.connector.errors.IntegrityError:
            msg = 'Submission from {name} ({house}) in course {course} is already stored.'
            msg = msg.format(name=entry['name'], house=entry['house'], course=entry['ravelry_id'])
            print(msg)
    mydb.commit()
    mycursor.close()
    mydb.close()

    # ravelry_id was popped
    class_pages = courses.get(filter={'mode': 1})
    nextcloud_report.create_reports()
    info_to_send['changed'] = manage_courses.update_mode()
    inform_users.inform_user(class_pages)
    manage_courses.inform_users(info_to_send)


if __name__ == '__main__':
    main()

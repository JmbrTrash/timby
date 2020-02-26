import mysql.connector
from timby_config import MYSQL_HOST, MYSQL_DATABASE, MYSQL_USER, MYSQL_PASSWORD


def get_db():
    mydb = mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        passwd=MYSQL_PASSWORD,
        database=MYSQL_DATABASE
    )
    mydb.autocommit = True

    return mydb


def database_init():
    sql_create_time_entries = """ CREATE TABLE IF NOT EXISTS time_entries (
                                        id INTEGER PRIMARY KEY AUTO_INCREMENT,
                                        begintime integer NOT NULL,
                                        lasttime integer NOT NULL,
                                        totaltime integer NOT NULL,
                                        user text,
                                        project_id integer NOT NULL
                                    ); """

    sql_chat_ids = """ CREATE TABLE IF NOT EXISTS chatids (
                                        id integer PRIMARY KEY NOT NULL,
                                        user TEXT NOT NULL,
                                        canManage boolean default 0
                                    ); """

    sql_create_projects = """ CREATE TABLE IF NOT EXISTS projects (
                                        id INTEGER PRIMARY KEY AUTO_INCREMENT,
                                        name varchar(45) NOT NULL
                                    ); """

    sql_adjust_time_entries = """ ALTER TABLE time_entries ADD COLUMN IF NOT EXISTS type VARCHAR(255); """

    adjust_can_manage = """ ALTER TABLE chatids ADD COLUMN IF NOT EXISTS canManage boolean default 0; """

    # create a database connection

    # create tables
    try:
        db = get_db()
        c = db.cursor()
        c.execute(sql_create_time_entries)
        c.execute(sql_create_projects)
        c.execute(sql_chat_ids)
        c.execute(sql_adjust_time_entries)
        c.execute(adjust_can_manage)
    except Exception as e:
        print(e)

import mysql.connector
import timby_config


def getDb():
    mydb = mysql.connector.connect(
        host=timby_config.MYSQL_HOST,
        user=timby_config.MYSQL_USER,
        passwd=timby_config.MYSQL_PASSWORD,
        database=timby_config.MYSQL_DATABASE
    )
    mydb.autocommit = True

    return mydb

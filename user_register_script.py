from werkzeug.security import generate_password_hash
import pymysql
import datetime


def connect_to_database():
    try:
        connection = pymysql.connect(
            host="localhost",
            user="root",
            password="root",
            db="safety_measurements_2",
            charset='utf8',
        )
        return connection
    except Exception as e:
        return None


def register_user(connection, username, password):
    try:
        with connection.cursor() as cursor:
            password = generate_password_hash(password)
            insert_query = f'''INSERT INTO login_table
            (login_username, login_password, login_role,
             is_deleted, created_on, modified_on)
            VALUES
            ("{username}", "{password}", "admin", false, 
            {int(datetime.datetime.now().timestamp())}, 
            {int(datetime.datetime.now().timestamp())})'''
            cursor.execute(insert_query)
            connection.commit()
            print("User registered successfully!")
    except Exception as e:
        print(f"Error registering user: {e}")


# Connect to the database
connection = connect_to_database()
print(connection)
if connection:
    # Register a user
    username = input("Enter username: ")
    password = input("Enter password: ")

    register_user(connection, username, password)

    # Close the connection
    connection.close()

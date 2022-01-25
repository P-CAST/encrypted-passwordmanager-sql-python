import os
import base64
import getpass
import mysql.connector
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC 

"""
    +------------SECTION------------+
    - setup    : setup dependencies
    - db_setup : setup database
    - menu     : menu prompting
    - db_check : check if row exist
    - view     : view module
    - insert   : insert module
    - delete   : delete module
    - salter   : salt generator
    - kdf      : _cryption module
    +-------------------------------+
"""

def setup():
    global login_user
    global mysql_passwd
    global main_passwd
    global mydb
    global mysql_cursor
    global id_cursor
    global password_cursor
    global salt_cursor

    # login section
    login_user = input('Enter user: ')
    mysql_passwd = getpass.getpass('Enter password: ')
    main_passwd = getpass.getpass('Enter main password: ')
    
    # Database connection
    mydb = mysql.connector.connect(
        host='localhost', # Change this if you have dedicated Database
        user=(login_user),
        password=(mysql_passwd)
        )
    mysql_cursor = mydb.cursor(buffered=True)
    id_cursor = mydb.cursor(buffered=True)
    password_cursor = mydb.cursor(buffered=True)
    salt_cursor = mydb.cursor(buffered=True)
    db_setup()

def db_setup():
    # Check if Database exist
    mysql_cursor.execute(f'CREATE DATABASE IF NOT EXISTS db_password_{login_user}')
    
    # Check if Table exist
    mysql_cursor.execute(f'CREATE TABLE IF NOT EXISTS db_password_{login_user}.tb_{login_user} (id INT NOT NULL AUTO_INCREMENT,name VARCHAR(255) NOT NULL,tag VARCHAR(255), password BLOB NOT NULL, salt BLOB NOT NULL, PRIMARY KEY (id))')
    menu() # Forward to menu

def menu():
    print('\nWelcome!')
    print('v to view all your password')
    print('i to insert new password')
    print('d to delete password')
    print('q to quit the program')
    cmd = input('> ').lower()

    if cmd == 'v':
        view()
    elif cmd == 'i':
        insert()
    elif cmd == 'd':
        delete()
    elif cmd == 'q':
        print('\nBye!')
        return 0
    else:
        print('\nNot an option!')
        return menu()
    
def db_check():
    # Query id, name
    mysql_cursor.execute(f"SELECT id, name FROM db_password_{login_user}.tb_{login_user}")
    myresult = mysql_cursor.fetchall()

    # If query return 0
    if len(myresult) == 0:
        print('Nothing to show.')
    else: # If there's data
        for item in myresult:
            print(item)
        pass

def view():
    db_check()
        
    view_id = input('Enter id: ')
    try:
        view_id = int(view_id) # Check if ID is INT or not

        # Check if data exist on ID
        id_cursor.execute(f"SELECT id, COUNT(*) FROM db_password_{login_user}.tb_{login_user} WHERE id = {view_id} GROUP BY id")
        check_id = id_cursor.rowcount
        if check_id == 0:
            print('\nInvalid ID')
            return view()
    except:
        print('\nInvalid ID')
    
    # Query id, name, salt, password
    id_cursor.execute(f"SELECT id,name FROM db_password_{login_user}.tb_{login_user} WHERE id={view_id}")
    salt_cursor.execute(f"SELECT salt FROM db_password_{login_user}.tb_{login_user} WHERE id={view_id}")
    password_cursor.execute(f"SELECT password FROM db_password_{login_user}.tb_{login_user} WHERE id={view_id}")

    # Clean Query
    id_for_view = id_cursor.fetchall()[0][1]
    salt_for_view = salt_cursor.fetchall()[0][0]
    password_for_view = password_cursor.fetchall()[0][0]

    kdf(salt_for_view) # Pass salt to KDF module
    decrypted = crypter.decrypt(password_for_view) # Decrypt password
    showed_password = decrypted.decode() # Decode byte object to normal string
    print("Password for",id_for_view,"is",showed_password)
    menu()

def insert():
    name = input('Name: ')
    tag = input('Tag: ')
    password = input('Password: ') 

    if name == '' or password == '':
        print('Please enter something')
    else:
        try:
            salt = salter() # Gen Salt
            kdf(salt) # Pass salt to KDF module
            password = crypter.encrypt(password.encode()) # Encrypt password(.encode() to turn into byte object)

            # Insert name, tag, password, salt to Database
            sql = f"INSERT INTO db_password_{login_user}.tb_{login_user} (name, tag, password, salt) VALUES (%s, %s, %s, %s)"
            value = (name, tag, password, salt)
            mysql_cursor.execute(sql, value)
            mydb.commit()
            print(mysql_cursor.rowcount, 'password inserted')
            menu()
        except:
            print('Something wrong')

def delete():
    db_check()

    del_id = input('Enter id: ')
    del_confirm = input('Confirm deleting?(y/N): ').lower()
            
    if del_id == '':
        print('Invalid id')
    else:
        if del_confirm == 'y':
            # Delete entire row by ID
            mysql_cursor.execute(f"DELETE FROM db_password_{login_user}.tb_{login_user} WHERE id ={del_id}")
            mydb.commit()
            print(mysql_cursor.rowcount, "name and password deleted")
            menu()
        else:
            print("Cancled...")

def salter():
    return os.urandom(16) # Generate random byte for lenght of 16

def kdf(salt):
    global crypter

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(), # Algorithm SHA256
        length=32,
        salt=salt,
        iterations=100000, # Iterations can be changed 
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(main_passwd.encode()))
    crypter = Fernet(key) # Crypter

if __name__ == '__main__':
    setup()
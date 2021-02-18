import mysql.connector
import urllib
import sqlite3
import functools
import operator
import json
import base64
import re
import os
import sys
import cryptography
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

#connect to database
mydb = mysql.connector.connect(
  host="localhost",
  user="root"
)

#set cursor
mycursor = mydb.cursor(buffered=True)
d = mydb.cursor(buffered=True)
i = mydb.cursor(buffered=True)

#detect and create database
mycursor.execute('CREATE DATABASE IF NOT EXISTS db_password')
mycursor.execute('CREATE TABLE IF NOT EXISTS db_password.tb_nap (id INT NOT NULL AUTO_INCREMENT,name VARCHAR(255) NOT NULL,password VARCHAR(255) NOT NULL,PRIMARY KEY (id))')

#interfaces
print("\n\nWelcome to password manager python! what you want to do?(v to view all your password,i to insert,d to delete")
cmd = input(">")

#view query
if cmd == 'v' or cmd == 'V':
    mycursor.execute("SELECT id, name FROM db_password.tb_nap") #select id,name from database
    myresult = mycursor.fetchall()

    if len(myresult)==0: #detect blank input
        print("Notthing here\n")
    else:    
        print("What you wanna see?")
        for x in myresult :
            print(x)

        icmd = input("Enter ID:")
        if icmd=='':
            print("\033[1;31;40m Error id. \033[1;37;40m")
        else:
            d.execute("SELECT id,name FROM db_password.tb_nap WHERE id= %s",(icmd,)) #select id,name from id input
            i.execute("SELECT password FROM db_password.tb_nap WHERE id= %s",(icmd,)) #select password from id input
            p = d.fetchall()
            i = i.fetchall()
            password = " , ".join( map(str, i) ) #transition list to string
    
            k = ("key") #set key 
            k_encode = k.encode() #encode key to byte
            p_encode = password.encode() #encode password to byte
            salt = b'`R\xf7\xc0\xf3+@\xdd~\xa4K1Ty\x83\x9a'
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
                backend=default_backend()
            )
            key = base64.urlsafe_b64encode(kdf.derive(k_encode))
            f = Fernet(key) #ready to decrypt
            decrypted = decrypted = f.decrypt(p_encode) #decrypted
            ogpasswd = decrypted.decode() #decode from byte to string

            print("Password for",p,"is",ogpasswd) #show id,name,password


#insert
elif cmd == 'i' or cmd == 'I':
    print("Insert name and password")
    n = input("name>")
    p = input("password>")

    if n=='' or p=='': #detect blank input
        print("\033[1;31;40m Can't insert into database.Plese input all of data. \033[1;37;40m")
    else:
        k = ("key") #set key
        k_encode = k.encode() #encode key to byte
        p_encode = p.encode() #encode password input to byte
        salt = b'`R\xf7\xc0\xf3+@\xdd~\xa4K1Ty\x83\x9a'
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(k_encode))

        f = Fernet(key) #ready to encrypt
        encrypted = f.encrypt(p_encode) #encrpyted

        sql = "INSERT INTO db_password.tb_nap (name, password) VALUES (%s, %s)" #insert to table query
        val = (n, encrypted)
        mycursor.execute(sql, val)
        mydb.commit() #confirm operation to database

        print(mycursor.rowcount, "password inserted") #show number(s) of query that have inserted

#delete
elif cmd == 'd' or cmd == 'D':
    mycursor.execute("SELECT id,name FROM db_password.tb_nap") #select id,name from db
    myresult = mycursor.fetchall()
    for x in myresult: #show id,name query in database
        print("What you want to delete")
        print(x)

    i = input("Enter id:") #enter query id
    
    if i=='': #detect blank input
        print("\033[1;31;40m Error id. \033[1;37;40m")
    else:
        sql = "DELETE FROM db_password.tb_nap WHERE id = %s" #delete from query id
        mycursor.execute(sql, (i,))
        mydb.commit() #confirm operation to database

        print(mycursor.rowcount, "name and password deleted") #show number(s) of query that have deleted

#error
else :
    print("\033[1;31;40m Error,Can't define command...plese try again \033[1;37;40m\n")
import mysql.connector
import json
import os


''' database was stored locally so fill in the host user password and database based on the profile of your machine '''
mydb = mysql.connector.connect(
    host="localhost", 
    user="username",    
    password="password",
    database="database_name"
    )

mycursor = mydb.cursor()

json_file = open("code.txt")
file = json_file.read()



#Jason_smile = json.dumps(data)


def drop_table(table_name):
    mycursor.execute(f"DROP TABLE {table_name}")

def create_table():
    mycursor.execute("CREATE TABLE snippets (id INT AUTO_INCREMENT PRIMARY KEY, code TEXT NOT NULL, Qid VARCHAR(12) NOT NULL)")



#function inserts data from json into a row in the table
def insertion(data,table_name):
    sql = f"INSERT INTO {table_name}(code, QID) VALUES (%s,%s)"
    string = data.get("link")
    final= string[36:42]
    val = (data.get("snippet"),final)
    mycursor.execute(sql,val)
    mydb.commit()
    print(mycursor.rowcount, "record inserted")


#function looks for snippet in database and returns its Qid, same snippet can be more times in database so returns list of Qids
def find_snippet_qid(snippet):
    mycursor.execute(f"SELECT Qid FROM snippets WHERE code = '{snippet}'") # IT WOULD BE BETTER TO DO IT WITH JUST ID BUT ITS NOT SETUP YET
    myresult = mycursor.fetchall()
    result_list=[]
    for i in myresult:
        result_list.append(i)
    return result_list

#function displays contents of a table
def show_table(table_name):
    mycursor.execute(f"SELECT * FROM {table_name}")
    myresult = mycursor.fetchall()
    for x in myresult:
        print(x)

def access_data(table_name):
    list=[]
    mycursor.execute(f"SELECT code FROM {table_name}")
    myresult = mycursor.fetchall()
    for i in myresult:
        list.append(i)
    return list

def insert_all(json_file):
    json_list = json.loads(json_file)
    for i in json_list:
        insertion(i,"snippets")



#drop_table("snippets")
#create_table()

#insert_all(file)
#show_table("snippets")

outputdata = access_data("snippets")
#for i in outputdata:
#    print(i)

#file = json.loads(file)
#print(file)
print(outputdata)











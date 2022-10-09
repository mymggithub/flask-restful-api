import mysql.connector
import json

mydb = mysql.connector.connect(
	host="localhost", 
	user="root", 
	passwd="pass123word",
	database="yiiadv"
)

mycursor = mydb.cursor()

mycursor.execute("SELECT * FROM twitter")
myresult = mycursor.fetchall()
json_data=[] 
for x in myresult:
	json_data.append(x)

print(json.dumps(json_data))
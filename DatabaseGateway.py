import mysql.connector
import json

class DatabaseGateway:

    def db_connect(self):

        db_con = mysql.connector.connect(
                    host     = "localhost",
                    user     = "Smishy",
                    password = "fakepassword",
                    database = "agent_database"
                 )

        # db_cursor = db_con.cursor()

        return db_con

    def db_query(self, query_string):

        my_db    = self.db_connect()
        mycursor = my_db.cursor()
        mycursor.execute(query_string)

        columns = mycursor.description
        data  = []

        for row in mycursor.fetchall():

            row_data = {}

            for (column_name, column_value) in enumerate(row):

                row_data[columns[column_name][0]] = column_value

            data.append(row_data)

        json_object = json.dumps(data)

        return json.dumps(json.loads(json_object), indent = 2) 

    def db_execute(self, query_string, data):

        my_db = self.db_connect()
        mycursor = my_db.cursor()
        mycursor.execute(query_string, data)
        my_db.commit()

        self.lastrowid = str(mycursor.lastrowid)
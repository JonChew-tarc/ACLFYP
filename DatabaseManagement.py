import json

import DatabaseGateway

class BaseAgentDatabaseManagement:

    def __init__(self):
        self.imageID = 0

    def create_agentRecord(self, droneID, locationLatitude, locationLongitude, elevationLevel, batteryStatus, verticalSpeed, horizontalSpeed):

        dg = DatabaseGateway.DatabaseGateway()
        mydb = dg.db_connect()
        mycursor = mydb.cursor()


        query_string = "insert into droneagent (droneID, locationLatitude, locationLongitude, elevationLevel, batteryStatus, verticalSpeed, horizontalSpeed) values (%s, %s, %s, %s, %s, %s, %s)"
        data = (droneID, locationLatitude, locationLongitude, elevationLevel, batteryStatus, verticalSpeed, horizontalSpeed)

        mycursor.execute(query_string, data) 

        mydb.commit()    

        return self.read_records(mycursor.lastrowid)


    def update_agentRecord(self, battery, locationLatitude, locationLongitude, elevation, horizontal, resource_id):
        dg = DatabaseGateway.DatabaseGateway()
        mydb = dg.db_connect()
        mycursor = mydb.cursor()

        query_string = "update droneagent set batteryStatus = %s, locationLatitude = %s, locationLatitude = %s, verticalSpeed = %s, horizontalSpeed = %s where droneID = %s"

        data = (battery, locationLatitude, locationLongitude, elevation, horizontal, resource_id)

        mycursor.execute(query_string, data)  

        return self.read_records(resource_id)


    def delete_record(self, resource_id):

        dg = DatabaseGateway.DatabaseGateway()

        query_string = "delete from customers where customer_id = %s"

        data = (resource_id)

        dg.db_execute(query_string, data) 

        resp = ("Success",)

        json_object = json.dumps(resp)

        return json.dumps(json.loads(json_object), indent = 2)

    def read_records(self, resource_id):

        dg = DatabaseGateway.DatabaseGateway()
        mydb = dg.db_connect()
        mycursor = mydb.cursor()

        if resource_id == "" :
            query_string = "select * from droneagent"
        else:
            query_string = "select * from droneagent where droneID = '" + str(resource_id) + "'"

        resp = dg.db_query(query_string)      

        return resp

    def upload_image(self, resource_id):
        self.imageID += 1

        dg = DatabaseGateway.DatabaseGateway()
        mydb = dg.db_connect()
        mycursor = mydb.cursor()

        imageFormatter = "I" + str(self.imageID)


        query_string = "insert into captured_images (imageID, imageByte) values (%s, %s)"
        data = (imageFormatter, resource_id)

        mycursor.execute(query_string, data) 

        mydb.commit()    

    def read_images(self, resource_id):

        dg = DatabaseGateway.DatabaseGateway()
        mydb = dg.db_connect()
        mycursor = mydb.cursor()

        if resource_id == "" :
            query_string = "select * from captured_images"
        else:
            query_string = "select * from captured_images where imageID = '" + str(resource_id) + "'"

        resp = dg.db_query(query_string)      

        return resp

    def read_activetask(self, resource_id):

        dg = DatabaseGateway.DatabaseGateway()
        mydb = dg.db_connect()
        mycursor = mydb.cursor()

        if resource_id == "" :
            query_string = "select * from active_task"
        else:
            query_string = "select * from active_task where taskID = '" + str(resource_id) + "'"

        resp = dg.db_query(query_string)      

        return resp

    def read_completetask(self, resource_id):

        dg = DatabaseGateway.DatabaseGateway()
        mydb = dg.db_connect()
        mycursor = mydb.cursor()

        if resource_id == "" :
            query_string = "select * from completed_task"
        else:
            query_string = "select * from completed_task where taskID = '" + str(resource_id) + "'"

        resp = dg.db_query(query_string)      

        return resp

    def delete_activetask(self, task_id):
        dg = DatabaseGateway.DatabaseGateway()
        mydb = dg.db_connect()
        mycursor = mydb.cursor()

        query_string = "DELETE FROM active_task WHERE taskID = '" + str(task_id) + "'"

        mycursor.execute(query_string)

        mydb.commit()

        print(mycursor.rowcount, "record(s) deleted")

    def add_activetask(self, task_id, task_name, task_type, generated_time, drone_id):
        dg = DatabaseGateway.DatabaseGateway()
        mydb = dg.db_connect()
        mycursor = mydb.cursor()

        query_string = "INSERT INTO active_task (taskID, taskName, taskType, generatedTIme, droneID) values (%s, %s, %s, %s, %s)"

        data = (task_id, task_name, task_type, generated_time, drone_id)


        mycursor.execute(query_string, data)

        mydb.commit()

    def add_completedtask(self, task_id, task_name, task_type, drone_id):
        dg = DatabaseGateway.DatabaseGateway()
        mydb = dg.db_connect()
        mycursor = mydb.cursor()

        query_string = "INSERT INTO completed_task (taskID, taskName, taskType,  droneID) values (%s, %s, %s, %s)"

        data = (task_id, task_name, task_type, drone_id)


        mycursor.execute(query_string, data)

        mydb.commit()

        




if __name__ == "__main__":
    test = BaseAgentDatabaseManagement()
    #test.create_agentRecord("user3@localhost", "70.4242", "24.2414", "40", 78, "0.241", "50.241")
    wow = test.read_completetask("")
    print (wow)
    dg = DatabaseGateway.DatabaseGateway()
    mydb = dg.db_connect()
    mycursor = mydb.cursor()

    #mycursor.execute("CREATE TABLE captured_images (imageID VARCHAR(50), imageByte VARCHAR(1000)) ENGINE = InnoDB")
    #mycursor.execute("CREATE TABLE active_task (taskID VARCHAR(50), taskName VARCHAR(50), taskType VARCHAR(50), generatedTime VARCHAR(50), droneID VARCHAR(50)) ENGINE = InnoDB")
    #mycursor.execute("CREATE TABLE completed_task (taskID VARCHAR(50), taskName VARCHAR(50), taskType VARCHAR(50), droneID VARCHAR(50)) ENGINE = InnoDB")



    mycursor.execute("SHOW TABLES")
    for x in mycursor:
        print(x)
    



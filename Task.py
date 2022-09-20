

class Task():
    def __init__(self, TaskID, TaskName, TaskType, GeneratedTime, agentID, droneID):
        self.TaskID = TaskID
        self.TaskName = TaskName
        self.TaskType = TaskType
        
        self.GeneratedTime = GeneratedTime
        self.agentID = agentID
        self.droneID = droneID



class TaskStorage():
    def __init__(self):
        self.activeTask = []
        self.completedTask = []

    def addActiveTask(self, task):
        self.activeTask.append(task)

    def removeActiveTask(self, task):
        #loop
        found = False
        for x in self.activeTask:
            if(x.TaskID == task.TaskID):
                self.activeTask.remove(x)
                found = True
        
        if(found):
            print("Successfully removed [{}] from the Active Task List".format(str(task.TaskID))
            )
            self.completedTask.append(task)
        else:
            print("[{}] is not found")




import datetime
import getpass
from re import A
import time
import asyncio
import spade
import xml.etree.ElementTree as ET
import itertools as IT
import requests
import aioxmpp


from lxml import etree
from spade import quit_spade
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour, PeriodicBehaviour, FSMBehaviour, State, OneShotBehaviour
from spade.message import Message
from spade.template import Template


def GenerateDroneDataXML(filename, baseAgent, droneAgent, taskID, latitude, longitude, battery):
    root = ET.Element("Response")

    droneType = ET.SubElement(root, "DroneType")
    droneType.text = "Drone Agent"

    ontology = ET.SubElement(root, "Ontology")
    ontology.text = "Drone Data"

    senderAgent = ET.SubElement(root, "senderAgent")
    senderAgent.text = droneAgent #replace with jID

    receiverAgent = ET.SubElement(root, "receiverAgent")
    receiverAgent.text = baseAgent #replace with jID

    droneName = ET.SubElement(root, "Name")
    if str(droneAgent) == "user2@localhost"  : 
        droneName.text = "Drone 1"
    elif str(droneAgent) == "user3@localhost":
        droneName.text = "Drone 2"

    droneID = ET.SubElement(root, "DroneID")
    droneID.text = droneAgent

    locationLatitiude = ET.SubElement(root, "locationLatitiude")
    locationLatitiude.text = latitude

    locationLongtitude= ET.SubElement(root,"locationLongtitude")
    locationLongtitude.text = longitude
    
    elevationLevel = ET.SubElement(root,"elevationLevel")
    elevationLevel.text = "5000"

    batteryStatus = ET.SubElement(root,"batteryStatus")
    batteryStatus.text = battery


    verticalSpeed = ET.SubElement(root,"verticalSpeed")
    verticalSpeed.text = "100"

    horizontalSpeed = ET.SubElement(root,"horizontalSpeed")
    horizontalSpeed.text = "100"

    replyTask = ET.SubElement(root, "ReplyTask")
    replyTask.text = taskID #replace with Task ID

    #print(ET.tostring(root)) #use this to print the whole thing out

    tree = ET.ElementTree(root)
    ET.indent(tree)
    tree.write(str(filename), encoding='unicode')
    #tree = ET.tostring(tree).decode()
    #return tree
    #headers={'Content-Type' : 'Test/XML'}

    #requests.post('http://127.0.0.1', data = tree, headers=headers)
    #with open (filename, "wb") as files:
     #   tree.write(files)

def GenerateDroneReturnXML(filename, taskID, baseAgent, droneAgent):
    root = ET.Element("Response")

    droneType = ET.SubElement(root, "DroneType")
    droneType.text = "Drone Agent"

    ontology = ET.SubElement(root, "Ontology")
    ontology.text = "Return Home"

    senderAgent = ET.SubElement(root, "senderAgent")
    senderAgent.text = droneAgent #replace with jID

    receiverAgent = ET.SubElement(root, "receiverAgent")
    receiverAgent.text = baseAgent #replace with jID

    droneName = ET.SubElement(root, "Name")
    if str(droneAgent) == "user2@localhost"  : 
        droneName.text = "Drone 1"
    elif str(droneAgent) == "user3@localhost":
        droneName.text = "Drone 2"

    droneID = ET.SubElement(root, "DroneID")
    droneID.text = droneAgent

    replyTask = ET.SubElement(root, "ReplyTask")
    replyTask.text = taskID #replace with Task ID

    print(ET.tostring(root))
    tree = ET.ElementTree(root)
    ET.indent(tree)
    tree.write(filename, encoding='unicode')


def GenerateCoordinateTaskCompletedXML(filename, taskID, baseAgent, droneAgent):
    root = ET.Element("Response")

    droneType = ET.SubElement(root, "DroneType")
    droneType.text = "Drone Agent"

    senderAgent = ET.SubElement(root, "senderAgent")
    senderAgent.text = droneAgent #replace with jID

    receiverAgent = ET.SubElement(root, "receiverAgent")
    receiverAgent.text = baseAgent #replace with jID

    droneName = ET.SubElement(root, "Name")
    if str(droneAgent) == "user2@localhost"  : 
        droneName.text = "Drone 1"
    elif str(droneAgent) == "user3@localhost":
        droneName.text = "Drone 2"

    ontology = ET.SubElement(root, "Ontology")
    ontology.text = "Coordinate" 

    descName = ET.SubElement(root, "DescName")
    descName.text = "Drone Agent have reached"

    generatedTime =  ET.SubElement(root, "GeneratedTime")
    generatedTime.text = datetime.datetime.now().time()

    replyTask = ET.SubElement(root, "ReplyTask")
    replyTask.text = taskID #replace with Task ID
    
    tree = ET.ElementTree(root)
    ET.indent(tree)
    tree.write(filename, encoding='unicode')

'''
query drone data
order return home
send drone data
tell return home
send coordinates to work
send coordinates have reached
send input data to base

'''
def GenerateUserInputXML(filename, baseAgent, droneAgent, userLatitude, userLongitude):
    root = ET.Element("Input")

    senderAgent = ET.SubElement(root, "senderAgent")
    senderAgent.text = "user4@localhost" #replace with jID

    receiverAgent = ET.SubElement(root, "receiverAgent")
    receiverAgent.text = baseAgent #replace with jID

    droneName = ET.SubElement(root, "DroneName")
    droneName.text = droneAgent

    ontology = ET.SubElement(root, "Ontology")
    ontology.text = "Input Data" 

    latitude = ET.SubElement(root, "InputLatitude")
    latitude.text = userLatitude

    longitude = ET.SubElement(root, "InputLongitude")
    longitude.text = userLongitude

    generatedTime =  ET.SubElement(root, "GeneratedTime")
    generatedTime.text = str(datetime.datetime.now().time())
    
    tree = ET.ElementTree(root)
    ET.indent(tree)
    tree.write(filename, encoding='unicode')


def GenerateTaskQueryXML(filename, iDCounter, baseAgent, droneAgent):
    root = ET.Element("Task")

    taskID = ET.SubElement(root, "TaskID")
    taskID.text = "T" + str(iDCounter) #ID dynamic

    senderAgent = ET.SubElement(root, "senderAgent")
    senderAgent.text = baseAgent #replace with jID

    receiverAgent = ET.SubElement(root, "receiverAgent")
    receiverAgent.text = droneAgent #replace with jID

    droneName = ET.SubElement(root, "Name")
    if str(droneAgent) == "user2@localhost"  : 
        droneName.text = "Drone 1"
    elif str(droneAgent) == "user3@localhost":
        droneName.text = "Drone 2"

    ontology = ET.SubElement(root, "Ontology")
    ontology.text = "Query Data" 

    taskName = ET.SubElement(root, "TaskName")
    taskName.text = "Request Data from Drone Agent 1 or 2"

    generatedTime =  ET.SubElement(root, "GeneratedTime")
    generatedTime.text = str(datetime.datetime.now().time())
    
    tree = ET.ElementTree(root)
    ET.indent(tree)
    tree.write(filename, encoding='unicode')


def GenerateTaskReturnXML(filename, iDCounter, baseAgent, droneAgent):
    root = ET.Element("Task")

    taskID = ET.SubElement(root, "TaskID")
    taskID.text = "T" + str(iDCounter)

    senderAgent = ET.SubElement(root, "senderAgent")
    senderAgent.text = baseAgent #replace with jID

    receiverAgent = ET.SubElement(root, "receiverAgent")
    receiverAgent.text = droneAgent #replace with jID

    droneName = ET.SubElement(root, "Name")
    if str(droneAgent) == "user2@localhost"  : 
        droneName.text = "Drone 1"
    elif str(droneAgent) == "user3@localhost":
        droneName.text = "Drone 2"

    ontology = ET.SubElement(root, "Ontology")
    ontology.text = "Return Home" 

    taskName = ET.SubElement(root, "TaskName")
    taskName.text = "Request Drone Agent 1 or 2 to return to base"

    generatedTime =  ET.SubElement(root, "GeneratedTime")
    generatedTime.text = str(datetime.datetime.now().time())

    tree = ET.ElementTree(root)
    ET.indent(tree)
    tree.write(filename, encoding='unicode')

#need to put two coordinates (latitude, longitude) here
def GenerateTaskGoCoordinatesXML(filename, iDCounter, latitude, longitude, baseAgent, droneAgent):
    root = ET.Element("Task")

    taskID = ET.SubElement(root, "TaskID")
    taskID.text = "T" + str(iDCounter)

    senderAgent = ET.SubElement(root, "senderAgent")
    senderAgent.text = baseAgent #replace with jID

    receiverAgent = ET.SubElement(root, "receiverAgent")
    receiverAgent.text = droneAgent #replace with jID

    droneName = ET.SubElement(root, "Name")
    if str(droneAgent) == "user2@localhost"  : 
        droneName.text = "Drone 1"
    elif str(droneAgent) == "user3@localhost":
        droneName.text = "Drone 2"

    ontology = ET.SubElement(root, "Ontology")
    ontology.text = "Coordinate" 

    taskName = ET.SubElement(root, "TaskName")
    taskName.text = "Drone Agent will move to ("+ latitude+", "+ longitude+ ")"

    statedLatitude = ET.SubElement(root, "Latitude")
    statedLatitude.text = latitude

    statedLongitude = ET.SubElement(root, "Longitude")
    statedLongitude.text = longitude

    generatedTime =  ET.SubElement(root, "GeneratedTime")
    generatedTime.text = str(datetime.datetime.now().time())

    tree = ET.ElementTree(root)
    ET.indent(tree)
    tree.write(filename, encoding='unicode')



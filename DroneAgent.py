import datetime
import getpass
from re import A
import time
import asyncio
import io
import xml.etree.ElementTree as ET
import itertools as IT

import aioxmpp
import XMLGenerate

from PIL import Image

from lxml import etree
from spade import quit_spade
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour, PeriodicBehaviour, FSMBehaviour, State, OneShotBehaviour
from spade.message import Message
from spade.template import Template

LONGITUDE = "0"
LATITUDE = "0"

class DroneAgent(Agent):
    def __init__(self, ip, _pass):
        Agent.__init__(self, ip, _pass)
        
        self.battery = 100
        self.latitude = LATITUDE
        self.longitude = LONGITUDE

        self.GoLatitude = LATITUDE
        self.GoLongitude = LONGITUDE

        self.coordinateTask = 0
        self.operatingTask = 0

        self.sleep = False
        self.startAgent = 0
        self.reached = False
    
        self.speed = 0
        self.elevationSpeed = 0
        self.elevationLevel = 0
    


    class SubscribePresenceBehav(OneShotBehaviour):
            def on_available(self, jid, stanza):
                
                print(
                    "[{}] Agent {} is available.".format(self.agent.name, str(jid).split("@")[0])
                )
            
            def on_subscribed(self,jid):
                print(
                    "[{}] Agent {} has accepted the subscription.".format(self.agent.name, jid.split("@")[0])
                )
                print(
                    "[{}] Contacts List : {}".format(self.agent.name, self.agent.presence.get_contacts())
                )
            
            def on_subscribe(self, jid):
                print(
                    "[{}] Agent {} asked for subscription. Should I approve it?".format(self.agent.name, jid.split("@")[0])
                )
                self.presence.approve(jid)
                self.presence.subscribe(jid)

            def set_unavailable(self, stanza):
                print(
                    "[{}] Agent {} is offline.".format(self.agent.name, self.agent.name)
                )

            def set_available(self, stanza):
                print(
                    "[{}] Agent {} is online.".format(self.agent.name, self.agent.name)
                )

            async def run(self):
                self.presence.on_subscribe = self.on_subscribe
                self.presence.on_subscribed = self.on_subscribed
                self.presence.on_available = self.on_available

                self.presence.set_available()
                self.presence.subscribe(self.agent.BaseAgent)





    class ReceiveOrder(CyclicBehaviour): 

        async def run(self):
            self.contRecvOrder = True
            while(self.contRecvOrder):
                recvMsg = await self.receive(timeout = 30)

                if(recvMsg.get_metadata("ontology") == "XML"):

                    receivedTree = ET.XML(recvMsg.body)
                    with open("Task.XML", "wb") as f:
                        f.write(ET.tostring(receivedTree))
                    treeReceivedData = ET.parse('Task.XML')
                    rootReceivedData = treeReceivedData.getroot()
                    

                    for elem in rootReceivedData.iter('Ontology'):
                        self.ontology = str(elem.text)
                    
                    for elem in rootReceivedData.iter('TaskID'):
                        self.taskID = str(elem.text)

                        self.agent.operatingTask = self.taskID
                    if (self.ontology == "Query Data"):

                        if(self.agent.name == "user2@localhost"):
                            
                            XMLGenerate.GenerateDroneDataXML("DroneData1.XML", "user1@localhost", self.agent.name, self.agent.operatingTask , str(self.agent.latitude), str(self.agent.longitude), str(self.agent.battery), str(self.agent.elevationSpeed), str(self.agent.speed))
                            tree1 = ET.parse('DroneData1.XML')
                        
                        else:
                            XMLGenerate.GenerateDroneDataXML("DroneData2.XML", "user1@localhost", self.agent.name, self.agent.operatingTask , str(self.agent.latitude), str(self.agent.longitude), str(self.agent.battery), str(self.agent.elevationSpeed), str(self.agent.speed))
                            tree1 = ET.parse('DroneData2.XML')
                        

                        root1 = tree1.getroot()
                        droneDataXML = ET.tostring(root1).decode()

                        msg = Message(to="user1@localhost")  # Instantiate the message
                        msg.set_metadata("performative", "inform")
                        msg.body = droneDataXML
                        self.agent.operatingTask = ""
                        await self.send(msg)
                        print(f"[{self.agent.name}] Sent drone data to base ")
                    
                    elif (self.ontology == "Return Home"):
                        XMLGenerate.GenerateDroneReturnXML("DroneReturn.XML", self.agent.operatingTask , str(recvMsg.sender), self.agent.name)
                        tree1 = ET.parse('DroneReturn.XML')
                        root1 = tree1.getroot()
                        droneReturnXML = ET.tostring(root1).decode()

                        msg = Message(to=recvMsg.sender)  # Instantiate the message
                        msg.set_metadata("performative", "inform")
                        msg.body = droneReturnXML
                        
                        self.agent.operatingTask = ""
                        self.agent.GoLatitude = "0"
                        self.agent.GoLongitude = "0"

                        await self.send(msg)

                        print(f"[{self.agent.name}] Returning to base ")

                    elif(self.ontology == "Coordinate"):
                        for elem in rootReceivedData.iter('Latitude'):
                            self.latitude = str(elem.text)
                        for elem in rootReceivedData.iter('Longitude'):
                            self.longitude = str(elem.text)
                        for elem in rootReceivedData.iter('TaskID'):
                            self.taskID = str(elem.text)

                        
                        self.agent.coordinateTask = self.taskID 
                        self.agent.GoLatitude = self.latitude
                        self.agent.GoLongitude = self.longitude

                        print(f"[{self.agent.name}] Received Coordinates from Base")
                        

                elif(recvMsg.get_metadata("ontology") == "Speed"):
                    self.agent.speed = int(recvMsg.body)
                    print(f"[{self.agent.name}] Drone Agent has set horizontal speed to {self.agent.speed}")

                elif(recvMsg.get_metadata("ontology") == "Elevation"):
                    self.agent.elevationSpeed = int(recvMsg.body)
                    print(f"[{self.agent.name}] Drone Agent has set elevation speed to {self.agent.elevationSpeed}")


            
        async def on_end(self):
            await self.agent.stop()

        


    # use async def function to call XML  and put into task

#use to take photo
    class TakePhotoBehav(PeriodicBehaviour):
        async def run(self):
            if((self.agent.latitude == self.agent.GoLatitude) 
            and (self.agent.longitude == self.agent.GoLongitude) and self.agent.sleep == False and self.agent.startAgent == 2):
                #will integrate KML file here to get the subsequent steps
                print(f"[{self.agent.name}] Taking photo at the objective")
                print(f"[{self.agent.name}] Saved as palmtree.jpeg")





# use to perform pathway decision (implement KML here) and check if drone has reached home or not
    class PathwayTaskBehav(PeriodicBehaviour):

        async def run(self):

            if(self.agent.battery > 60 and self.agent.longitude == "0" and self.agent.latitude == "0" and self.agent.startAgent == 0):
                self.agent.sleep = False
                self.agent.presence.set_available(aioxmpp.PresenceShow.CHAT)
                


            if(self.agent.sleep == True):
                self.agent.presence.set_unavailable(aioxmpp.PresenceShow.NONE)


            if((self.agent.latitude != self.agent.GoLatitude) and (self.agent.longitude != self.agent.GoLongitude)):
                #will integrate KML file here to get the subsequent steps
                if(self.agent.GoLatitude == "0" and self.agent.GoLongitude == "0"):
                    self.agent.startAgent = 1
                else:
                    self.agent.startAgent = 2

                self.agent.sleep = False
                self.agent.reached = False
                print(f"[{self.agent.name}] Moving to next coordinate")

                #illustrating the drone already reached the destination
                self.agent.latitude = self.agent.GoLatitude
                self.agent.longitude = self.agent.GoLongitude


            elif(self.agent.latitude == "0" and self.agent.longitude == "0" and self.agent.sleep == False and self.agent.startAgent == 1):
                #add transfer photo here
                print(f"[{self.agent.name}] Has reached charging port.")
                print(f"[{self.agent.name}] Transfering images to the base agent")

#the code to turn images to bytearray but the file is too big to be inserted into the table of MySQL
                #im = Image.open('palmtree.jpeg')
                #im_resize = im.resize((500,500))
                #buf = io.BytesIO()
                #im_resize.save(buf, format='JPEG')
                #byte_im = buf.getvalue()
                #byte_im = str(byte_im)
                

                if(self.agent.name == 'user2'):

                    XMLGenerate.GenerateDroneHomeXML("ReachedHome1.XML", "user1@localhost",
                    "user2@localhost", "palmtree.jpeg", self.agent.coordinateTask)
                    

                    tree1 = ET.parse('ReachedHome1.XML')
                    root1 = tree1.getroot()
                    droneHomeReturnXML1 = ET.tostring(root1).decode()

                    msg = Message(to="user1@localhost")  # Instantiate the message
                    msg.set_metadata("performative", "inform")
                    msg.body = droneHomeReturnXML1
                
                    await self.send(msg)

                    print(f"[{self.agent.name}] Drone has transferred images to base agent")

                elif(self.agent.name =='user3'):
                    XMLGenerate.GenerateDroneHomeXML("ReachedHome2.XML", "user1@localhost",
                    "user3@localhost", "palmtree.jpeg",  self.agent.coordinateTask)

                    tree2 = ET.parse('ReachedHome2.XML')
                    root2 = tree2.getroot()
                    droneHomeReturnXML2 = ET.tostring(root2).decode()

                    msg = Message(to="user1@localhost")  # Instantiate the message
                    msg.set_metadata("performative", "inform")
                    msg.body = droneHomeReturnXML2
                    
                    await self.send(msg)

                    print(f"[{self.agent.name}] Drone has transferred images to base agent")

                self.agent.coordinateTask = ""
                self.agent.sleep = True
                self.agent.startAgent = 0

            
            elif((self.agent.latitude == self.agent.GoLatitude) 
            and (self.agent.longitude == self.agent.GoLongitude) and self.agent.startAgent == 2 and self.agent.reached == False):
                XMLGenerate.GenerateCoordinateTaskCompletedXML("ReachedCoordinate.XML", self.agent.coordinateTask,
                 "user1@localhost", self.agent.name + "@localhost")
                tree1 = ET.parse('ReachedCoordinate.XML')
                root1 = tree1.getroot()
                droneReachedCoordinateXML = ET.tostring(root1).decode()

                msg = Message(to="user1@localhost")  # Instantiate the message
                msg.set_metadata("performative", "inform")
                msg.body = droneReachedCoordinateXML
                self.agent.coordinateTask = ""
                await self.send(msg)

                print(f"[{self.agent.name}] Drone has reached its pinpointed coordinates")
                self.agent.reached = True
        

        async def on_start(self):
            
            print(f"[{self.agent.name}] Currently no coordinate task for [{self.agent.name}]")



    async def setup(self):

        print(f"[{self.name}] Drone Agent initiated")
        recOrder = self.ReceiveOrder()
        template = Template()
        template.set_metadata("performative", "request")
        self.add_behaviour(recOrder, template)
        d = self.SubscribePresenceBehav()
        self.add_behaviour(d)
        takePhotoBehaviour = self.TakePhotoBehav(period = 15)
        self.add_behaviour(takePhotoBehaviour)
        pathwayBehaviour = self.PathwayTaskBehav(period = 15)
        self.add_behaviour(pathwayBehaviour)

        

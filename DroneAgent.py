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
import XMLGenerate

from lxml import etree
from spade import quit_spade
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour, PeriodicBehaviour, FSMBehaviour, State, OneShotBehaviour
from spade.message import Message
from spade.template import Template


class DroneAgent(Agent):
    def __init__(self, ip, _pass):
        Agent.__init__(self, ip, _pass)
        self.available = True
        self.battery = 100
        self.latitude = 25
        self.longitude = 25
        self.GoLatitude = 0
        self.GoLongitude = 0
        self.coordinateTask = 0
        self.operatingTask = 0


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

            async def run(self):
                self.presence.on_subscribe = self.on_subscribe
                self.presence.on_subscribed = self.on_subscribed
                self.presence.on_available = self.on_available

                self.presence.set_available()
                self.presence.subscribe(self.agent.BaseAgent)
                self.agent.battery = 70
                self.agent.latitude = 34.1312512
                self.agent.longitude = 69.69696969




    class ReceiveOrder(CyclicBehaviour): 
        async def run(self):
            self.contRecvOrder = True
            while(self.contRecvOrder):
                recvMsg = await self.receive(timeout = 30)

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
                    XMLGenerate.GenerateDroneDataXML("DroneData.XML", "user1@localhost", self.agent.name, 
                    self.taskID, str(self.agent.latitude), str(self.agent.longitude), str(self.agent.battery))
                    tree1 = ET.parse('DroneData.XML')
                    root1 = tree1.getroot()
                    droneDataXML = ET.tostring(root1).decode()

                    msg = Message(to="user1@localhost")  # Instantiate the message
                    msg.set_metadata("performative", "inform")
                    msg.body = droneDataXML
                    self.agent.operatingTask = ""
                    await self.send(msg)
                    print(f"[{self.agent.name}] Sent drone data to base ")
                
                elif (self.ontology == "Return Home"):
                    XMLGenerate.GenerateDroneReturnXML("DroneReturn.XML", self.taskID, str(recvMsg.sender), self.jid)
                    tree1 = ET.parse('DroneReturn.XML')
                    root1 = tree1.getroot()
                    droneReturnXML = ET.tostring(root1).decode()

                    msg = Message(to=recvMsg.sender)  # Instantiate the message
                    msg.set_metadata("performative", "inform")
                    msg.body = droneReturnXML
                    self.agent.operatingTask = ""
                    await self.send(msg)

                    print("[{}] Returning to base ", format(self.agent.name))

                elif(self.ontology == "Coordinate"):
                    for elem in rootReceivedData.iter('Latitude'):
                        self.latitude = str(elem.text)
                    for elem in rootReceivedData.iter('Longitude'):
                        self.longitude = str(elem.text)
                    for elem in rootReceivedData.iter('TaskID'):
                        self.taskID = str(elem.text)

                    self.agent.coordinateTask = self.taskID 
                    self.agent.GoLatitude = self.latitude
                    self.agent.GoLongitude= self.longitude

                    print(f"[{self.agent.name}] Received Coordinate from Base")

            
        async def on_end(self):
            await self.agent.stop()

    # use async def function to call XML  and put into task

#use to take photo
    class TakePhotoBehav(PeriodicBehaviour):
        async def run(self):
            if((self.agent.latitude == self.agent.GoLatitude) 
            and (self.agent.longitude == self.agent.GoLongitude)):
                #will integrate KML file here to get the subsequent steps
                print("[{}]Taking photo, taka", format(self.agent.name))


    class PathwayTaskBehav(PeriodicBehaviour):
        async def run(self):
            if((self.agent.latitude != self.agent.GoLatitude) 
            and (self.agent.longitude != self.agent.GoLongitude)):
                #will integrate KML file here to get the subsequent steps
                print(f"[{self.agent.name}]Moving to next coordinate")

            
            else:
                XMLGenerate.GenerateCoordinateTaskCompletedXML("ReachCoordinate.XML", self.agent.coordinateTask,
                 "user1@localhost", self.jid)
                tree1 = ET.parse('DroneReturn.XML')
                root1 = tree1.getroot()
                droneReachedCoordinateXML = ET.tostring(root1).decode()

                msg = Message(to="user1@localhost")  # Instantiate the message
                msg.set_metadata("performative", "inform")
                msg.body = droneReachedCoordinateXML
                self.agent.coordinateTask = ""
                await self.send(msg)

        def on_start(self):
            
            print(f"[{self.agent.name}]Currently no coordinate task for [{self.agent.name}]")



    async def setup(self):

        print(f"[{self.name}] Drone Agent initiated")
        recOrder = self.ReceiveOrder()
        template = Template()
        template.set_metadata("performative", "request")
        self.add_behaviour(recOrder, template)
        d = self.SubscribePresenceBehav()
        takePhotoBehaviour = self.TakePhotoBehav(period = 10)
        self.add_behaviour(takePhotoBehaviour)
        pathwayBehaviour = self.PathwayTaskBehav(period = 15)
        self.add_behaviour(pathwayBehaviour)

        self.add_behaviour(d)

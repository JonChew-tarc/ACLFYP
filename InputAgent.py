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
import DroneAgent
import aioconsole

from lxml import etree
from spade import quit_spade
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour, PeriodicBehaviour, FSMBehaviour, State, OneShotBehaviour
from spade.message import Message
from spade.template import Template

class InputAgent(Agent):
    def __init__(self, ip, _pass):
        Agent.__init__(self, ip, _pass)
        self.inputLatitude= 0
        self.inputLongitude = 0
        self.inputSpeed = 0
        self.inputElevation = 0

    class InputBehav(PeriodicBehaviour):
        async def run(self):
            input = True


            self.startTime = time.time()
            while((time.time() - self.startTime) < 20):

                self.droneAgent = ""
                while(input):
                    chosenDrone = await aioconsole.ainput("Enter the drone number [1/2]  : ")
                    if(chosenDrone == '1'):
                        self.droneAgent = "user2@localhost"
                        input = False
                    
                    elif(chosenDrone =='2'):
                        self.droneAgent = "user3@localhost"
                        input = False
                    
                    else:
                        print("Please input again")

                input = True
                

                while(input):
                    chosenAction = await aioconsole.ainput("Set speed [1], elevation [2], coordinates [3]  : ")
                    if(chosenAction == "1"):
                        validValue = True
                        while(validValue):
                            self.agent.inputSpeed = await aioconsole.ainput("Enter horizontal velocity : ")

                            if(float(self.agent.inputSpeed) <= 0):
                                print("Negative value is invalid for horziontal speed")
                            
                            else: 
                                validValue = False

                        filename = "UserInputA.XML"
                        XMLGenerate.GenerateUserInputAXML(filename, "user1@localhost", str(self.droneAgent)
                        , str(self.agent.inputSpeed))
                        inputQuery = ET.parse('UserInputA.XML')
                        rootInputQuery = inputQuery.getroot()
                        inputQueryXML = ET.tostring(rootInputQuery).decode()

                        msg = Message(to="user1@localhost")  # Instantiate the message
                        msg.set_metadata("performative", "request")
                        msg.body = inputQueryXML  # Set the message content
                    
                        await self.send(msg)
                        print(f"[{self.agent.name}] Input Message A sent!")

                        input = False


                    elif (chosenAction == "2"):

                        
                        self.agent.inputElevation = await aioconsole.ainput("Enter elevation speed : ")
                        filename = "UserInputB.XML"
                        XMLGenerate.GenerateUserInputBXML(filename, "user1@localhost", str(self.droneAgent)
                        , str(self.agent.inputElevation))

                        inputQuery = ET.parse('UserInputB.XML')
                        rootInputQuery = inputQuery.getroot()
                        inputQueryXML = ET.tostring(rootInputQuery).decode()

                        msg = Message(to="user1@localhost")  # Instantiate the message
                        msg.set_metadata("performative", "request")
                        msg.body = inputQueryXML  # Set the message content
                    
                        await self.send(msg)
                        print(f"[{self.agent.name}] Input Message B sent!")

                        input = False

                    elif(chosenAction == "3"):
                        self.agent.inputLatitude = await aioconsole.ainput("Enter latitude : ")
                        self.agent.inputLongitude = await aioconsole.ainput("Enter longitude : ")

                        filename = "UserInputC.XML"
                        XMLGenerate.GenerateUserInputCXML(filename, "user1@localhost", str(self.droneAgent)
                        , str(self.agent.inputLatitude), str(self.agent.inputLongitude))
                        inputQuery = ET.parse('UserInputC.XML')
                        rootInputQuery = inputQuery.getroot()
                        inputQueryXML = ET.tostring(rootInputQuery).decode()

                        msg = Message(to="user1@localhost")  # Instantiate the message
                        msg.set_metadata("performative", "request")
                        msg.body = inputQueryXML  # Set the message content
                    
                        await self.send(msg)
                        print(f"[{self.agent.name}] Input Message C sent!")

                        input = False

                    else:
                        print("Please input again")



    async def setup(self):
    
        print("Input Agent activated")

        b = self.InputBehav(period = 20)
        self.add_behaviour(b)
        
        

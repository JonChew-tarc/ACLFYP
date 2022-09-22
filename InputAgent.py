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

    class InputBehav(PeriodicBehaviour):
        async def run(self):
            self.startTime = time.time()
            while((time.time() - self.startTime) < 10):

                self.droneAgent = ""
                chosenDrone = await aioconsole.ainput("Enter the drone number [1/2]  : ")

                if(chosenDrone == '1'):
                    self.droneAgent = "user2@localhost"
                
                elif(chosenDrone =='2'):
                    self.droneAgent = "user3@localhost"

                self.agent.inputLatitude = await aioconsole.ainput("Enter latitude : ")
                self.agent.inputLongitude = await aioconsole.ainput("Enter longitude : ")

                filename = "UserInputA.XML"
                XMLGenerate.GenerateUserInputXML(filename, "user1@localhost", str(self.droneAgent)
                , str(self.agent.inputLatitude), str(self.agent.inputLongitude))
                inputQuery = ET.parse('UserInputA.XML')
                rootInputQuery = inputQuery.getroot()
                inputQueryXML = ET.tostring(rootInputQuery).decode()

                msg = Message(to="user1@localhost")  # Instantiate the message
                msg.set_metadata("performative", "request")
                msg.body = inputQueryXML  # Set the message content
            
                await self.send(msg)
                print(f"[{self.agent.name}] Input Message sent!")


    async def setup(self):
    
        print("Input Agent activated")

        b = self.InputBehav(period = 20)
        self.add_behaviour(b)
        
        

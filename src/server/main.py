#!/usr/bin/python
from gameObjects import *
import traceback
import network
import time

try:
  import ConfigParser
except ImportError:
  import configparser as ConfigParser

try:
  xrange(1)
except NameError:
  xrange = range

def getConfig(server):
  #Eventually, this function will get config from the clients
  config = {"difficulty":5, "mapType":"random", "ships":[{"type":"Player", "name":"Fartemis", "players":["127.0.0.1"]}], "height":1000, "width":1000, "frameRate":30, "teams":["foo"]}
  return config
  
def mapGenerator(config):
  entities = []
  for i in config['ships']:
    entities.append(Ship(i))
  for i in xrange(int(config['difficulty'])):
    conf = {"Type":"Enemy", "id":i}
    entities.append(Ship(conf))
  return entities

server = network.Server("0.0.0.0", 8553)
server.waitForStart()
config = getConfig(server)
universe = Universe(height=config['height'], width=config['width'])
entities = mapGenerator(config)
universe.add(entities)
universe.teams = config['teams']

while True:
  messages = server.getMessages()
  universe.tick(config['frameRate'])
  server.send(universe.dumpState())
  

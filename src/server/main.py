#!/usr/bin/python
import Universe
import json
import Ship

try:
  xrange(1)
except NameError:
  xrange = range

#def getConfig(server):
#  #Eventually, this function will get config from the clients
#  config = {"difficulty":5, "mapType":"random", "ships":[{"type":"Player", "name":"Fartemis", "players":["127.0.0.1"]}], "height":1000, "width":1000, "frameRate":30, "teams":["foo"]}
#  return config
  
#server = network.Server("0.0.0.0", 8553)
#server.waitForStart()
#config = getConfig(server)
#universe = Universe(height=config['height'], width=config['width'])
#entities = mapGenerator(config)
#universe.add(entities)
#universe.teams = config['teams']

with open("../../assets/data/ships/destroyer.js", 'r') as shipConfFile:
  shipConf = json.load(shipConfFile)

universe = Universe()
ship = Ship(universe, shipConf)

last = time.time()
while True:
#  messages = server.getMessages()
  universe.tick(time.time()-last)
  last = time.time()
  time.sleep(1/frameRate)
#  server.send(universe.dumpState())
  

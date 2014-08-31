#!/usr/bin/python
import Universe
import json
import Ship

with open("../../assets/data/ships/destroyer.js", 'r') as shipConfFile:
  shipConf = json.load(shipConfFile)

universe = Universe()
ship = Ship(universe, shipConf)

last = time.time()
while True:
  universe.tick(time.time()-last)
  last = time.time()
  time.sleep(1/frameRate)
  

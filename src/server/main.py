#!/usr/bin/python
import Universe
import json
import Ship
import time

frameRate = 30

with open("../../assets/data/ships/destroyer.json", 'r') as shipConfFile:
  shipConf = json.load(shipConfFile)

universe = Universe.Universe()
ship = Ship.Ship(shipConf, universe)

last = time.time()
while True:
  universe.tick(time.time()-last)
  last = time.time()
  time.sleep(1/frameRate)
  

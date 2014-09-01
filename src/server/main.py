#!/usr/bin/python
import Universe
import json
import Ship
import time
import physics
import Missile
import ServerNetwork
import os

frameRate = 30

with open("../../assets/data/ships/destroyer.json", 'r') as shipConfFile:
  shipConf = json.load(shipConfFile)
with open("../data/weapons.json", 'r') as missileConfFile:
  missileConf = json.load(missileConfFile)
missileConf = missileConf['weapons']['nuke']

universe = Universe.Universe()

network = ServerNetwork.NetworkServer({}, universe)
network.start()

ship1 = Ship.Ship(shipConf, universe)
ship2 = Ship.Ship(shipConf, universe)
ship1.location = physics.Vector(0,0,0)
ship2.location = physics.Vector(10000000000,0,0)
ship2.rotation = physics.Vector(3.1415,3.14159,3.1415)
universe.add(ship1)
universe.add(ship2)

missile = Missile.Missile(missileConf, universe)

for i in ship1.components:
  if i.type == "WeaponsStation":
    i.energy = 1
    i.load(missile)
universe.tick(5)
universe.collide()
universe.tock()

universe.tick(5)
universe.collide()
universe.tock()

for i in ship1.components:
  if i.type == "WeaponsStation":
    i.fire()
    
last = time.time()
while True:
  universe.tick(time.time()-last)
  last = time.time()
  universe.collide()
  universe.tock()
  time.sleep(1/frameRate)
  

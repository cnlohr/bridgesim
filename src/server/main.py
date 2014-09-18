#!/usr/bin/python
import pygame
import Universe
import json
import Entity
import Ship
import Component
import time
import physics
import Missile
import NetworkServer
import os
import ClientAPI
import SharedClientDataStore

frameRate = 30

with open("../../assets/data/ships/destroyer.json", 'r') as shipConfFile:
  shipConf = json.load(shipConfFile)
with open("../data/weapons.json", 'r') as missileConfFile:
  missileConf = json.load(missileConfFile)
missileConf = missileConf['weapons']['nuke']

pygame.init()
size = width, height = 6400,4800
SCALEFACTOR = 640/width
screen = pygame.display.set_mode((int(width*SCALEFACTOR), int(height*SCALEFACTOR)))

universe = Universe.Universe(size)
universe.id = 0

network = NetworkServer.NetworkServer({}, universe)

api = ClientAPI.ClientAPI(ClientAPI.GlobalContext([universe], network))

# Register ALL the classes!
api.register(Universe.Universe)
api.register(Entity.Entity)
api.register(Ship.Ship)
api.register(Component.Component)
api.register(Component.Drive)
api.register(Component.WeaponsStation)
api.register(Component.ShieldGenerator)
api.register(SharedClientDataStore.SharedClientDataStore)

print(api.getTable())

network.start(api)

ship1 = Ship.Ship(shipConf, universe)
ship1.name = "Aggressor"
ship2 = Ship.Ship(shipConf, universe)
ship2.name = "Victim"
ship1.location = physics.Vector(5000,1000,0)
ship2.location = physics.Vector(1000,1000,0)
ship2.rotation = physics.Vector(0,0,0)
universe.add(ship1)
universe.add(ship2)

missile = Missile.Missile(missileConf, universe)

for i in ship1.components.values():
  if i.type == "WeaponsStation":
    i.energy = 1
    i.load(missile)

screen.fill((255,255,255))

universe.tick(5)
universe.collide()
universe.tock()

last = time.time()
while True:
#  data = universe.tick(time.time()-last)
  data = universe.tick(.03)
  last = time.time()
  screen.fill((255,255,255))
  for i in data:
#    print(int(i[0]*SCALEFACTOR),int(i[1]*SCALEFACTOR))
    pygame.draw.circle(screen, (0,0,0), (int((i[0]-i[2])*SCALEFACTOR),int((i[1]-i[2])*SCALEFACTOR)), int(i[2]*SCALEFACTOR))
  pygame.display.flip()
  universe.collide()
  universe.tock()
#  print("Sleeping:", time.time()-last)
#  time.sleep((1/frameRate)-(time.time()-last))
  

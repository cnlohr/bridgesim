#!/usr/bin/python
print ("Basic stuff is good")
import gameObjects
print ("GameObjects is OK.")
import ConfigParser
      
print ("Imports are successfull.")
      
universe = gameObjects.Universe(TPS=30, difficulty=5)
gameObjects.universe = universe
      
if universe:
  print ("Universe is ok...")

def initStations(count):
  for i in xrange(count):
    station = gameObjects.Station(i, universe)
    universe.stations.append(station)

def initWeapons():
  config = ConfigParser.RawConfigParser()
  config.read('weapons.conf')
  weapons = config.sections()
  for i in weapons:
    tubeAmmoInfo = dict(config.items(i))
    tubeAmmoInfo['name'] = i
    tubeAmmo = gameObjects.TubeAmmo(tubeAmmoInfo)
    universe.tubeAmmos.append(tubeAmmo)

def initEnemyGroups(count):
  for i in xrange(count):
    enemyGroup = gameObjects.EnemyGroup(i, universe)
    universe.enemyGroups.append(enemyGroup)
    
def initPlayers(count):
  for i in xrange(count):
    universe.playerShips.append(gameObjects.PlayerShip(i, "Fartemis", universe))
    
print ("Start")
initWeapons()
print ("Weapons Check")
initStations(4)
print ("Stations Check")
initPlayers(1)
print ("Players Check")

while True:
  print ("Tick")
  universe.tick()
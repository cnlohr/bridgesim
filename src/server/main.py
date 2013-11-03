#!/usr/bin/python
import gameObjects
import timeit
try:
  import ConfigParser
except ImportError:
  import configparser as ConfigParser

try:
  xrange(1)
except NameError:
  xrange = range

universe = gameObjects.Universe(TPS=30, difficulty=5)
gameObjects.universe = universe
      
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
    
initWeapons()
initStations(40)
initPlayers(1)
initEnemyGroups(300)

#print(universe.state())

while True:
  rate = 10/timeit.timeit(universe.tick, number=10)
  print ("Frame Rate: %f" % rate)
 # print (universe.enemies[1].location)

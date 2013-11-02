#!/usr/bin/python
import gameObjects
import configparser

universe = gameObjects.Universe(TPS=30, difficulty=5)
gameObjects.universe = universe
      
def initStations(count):
  for i in xrange(count):
    station = gameObjects.Station(i, universe)
    universe.stations.append(station)

def initWeapons():
  config = configparser.RawConfigParser()
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
initStations(4)
initPlayers(1)
initEnemyGroups(3)

print(universe.state())

while True:
  universe.tick()
  print universe.enemies[1].location

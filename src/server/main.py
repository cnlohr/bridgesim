import time
import math
from random import randint
import gameObjects
import ConfigParser

playerShips = []
stations = []
tubeAmmos = []
enemies = []
enemyGroups = []
missiles = []
enemyMissiles = []
fighters = []
referenceOrientation = [1,1,1] #this should be arbitrary; but changing it is useful for testing purposes sometimes.
TPS = 30
timeMultiplier = 1/TPS
difficulty = 5

def Tick(input):
  for i in xrange(input):
    for i in playerShips:
      i.physics()
    for i in stations:
      i.physics()
    for i in enemyGroups:
      i.physics()
    for i in enemies:
      i.physics()
    for i in missiles:
      i.physics()
    for i in fighters:
      i.physics()
      
def initStations(a):
  for i in xrange(a):
    s = gameObjects.Station()
    s.init(i)
    stations.append(s)

def initWeapons():
  config = ConfigParser.RawConfigParser()
  config.read('weapons.conf')
  weapons = config.sections()
  for i in weapons:
    s = gameObjects.TubeAmmo()
    s.init(dict(config.items(i)))
    tubeAmmos.append(s)

def initEnemyGroups(a):
  for i in xrange(a):
    s = gameObjects.enemyGroup()
    s.init(i)
    enemyGroups.append(s)

def init():
  initWeapons()
  initStations(4)
  spawnGroups(5)
  initPlayers()

initStations(4)
initWeapons()
initEnemyGroups(2)
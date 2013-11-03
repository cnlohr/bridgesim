from physics import *
import network as network
from random import randint

def __init__(self):
  self.universe = self.Universe()

class Universe:
  def __init__(self, height=1000, width=1000):
    self.entities = []
    self.height = height
    self.width = width
    self.teams = []
    self.state = []
    
  def add(self, entities):
    self.entities.extend(entities)
    
  def tick(self):
    for i in entities:
      for j in i.tick(duration):
        self.state.update(j)
        
  def dumpState(self):
    return self.state
    

class Entity:
  
  def __init__(self, config):
    self.id = config['id']
    self.loc = config['loc']
    self.rot = config['rot']
    self.vel = config['vel']
    self.allyTeam = config['allyTeam']
    self.neutralTeam = config['neutralTeam']
    self.enemyTeam = config['enemyTeam']
    self.shield = config['shield']
    self.energy = config['energy']
    self.name = config['name']
    self.health = config['health']
    self.shieldMultiplier = config['shieldMultiplier']
    
  def tick(self, duration):
    return [{[self.id, "loc"]:self.loc},
            {[self.id, "rot"]:self.rot},
            {[self.id, "vel"]:self.vel},
            {[self.id, "allyTeam"]:self.allyTeam},
            {[self.id, "neutralTeam"]:self.neutralTeam},
            {[self.id, "enemyTeam"]:self.enemyTeam},
            {[self.id, "shield"]:self.shield},
            {[self.id, "energy"]:self.energy},
            {[self.id, "name"]:self.name},
            {[self.id, "health"]:self.health},]
    
class TubeAmmo:
class Station(Entity):
  def __init__(self, config):
    super(config)
    self.weaponStocks = config['weaponStocks']
    self.maxDock = config['maxDock']
    self.docked = config['docked']
    self.producing = config['producing']
  def dock(self, ship):
    if len(self.docked) < self.maxDock:
      self.docked.append(ship)
      return True
    return False
  def unDock(self, ship):
    if (ship in self.docked):
      self.docked.remove(ship)
      return True
    return False
  def tick(self, duration):
    self.shields += self.shieldMultiplier*duration
    self.energy += self.energyMultiplier*duration
    return super(duration).extend([{[self.id, "weaponStocks"]:self.weaponStocks},
                                   {[self.id, "maxDock"]:self.maxDock},
                                   {[self.id, "docked"]:self.docked}])
  
class Tube:
class Beam:
class Missile(Entity):
class Ship(Entity):
  def __init__(self, config):
    super(config)
class ShipGroup(Entity):
class AI:
class PlayerAI(AI):
class NPC(AI):
class Team:
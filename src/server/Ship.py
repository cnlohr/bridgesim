from Entity import Entity
from Component import *
from Missile import Missile
import sys

class Ship(Entity):
  def __init__(self, config, universe):
    super().__init__(config, universe)
    self.__dict__.update(config)

    self.energy = self.maxEnergy

    # How much power Engineering is giving to each component - [0, 1] normally
    self.energySupply = {}

    temp = []
    for i in self.components:
      comp = findComponent(i['type'])(self, i)
      temp.append(comp)
      self.energySupply[comp] = 1
    self.components = temp
    
  def collide(self, other):
    print("I got hit!")
    if type(other) is Missile:
      self.takeDamage(other.getDamage())
      
  def takeDamage(self, damage):
    print("I'm hit!", damage)
    for i in self.components:
      print(i.type, "Took damage")
      damage = i.takeDamage(damage)
      if damage <= 0:
        break
      
  def tick(self, duration):
    # Figure out how much each component wants and is being allowed
    needed = {component: component.energyNeeded() * duration * self.energySupply[component] for component in self.components}

    totalNeeded = sum(needed.values())
    factor = 1 if totalNeeded <= self.energy else self.energy / totalNeeded

    # do this before looping so nothing grabs power allotted to something else
    self.energy -= totalNeeded * factor

    for i in self.components:
      i.energy = factor * duration * self.energySupply[i] * needed[i]
      i.tick(duration)
  
  def tock(self):
    for i in self.components:
      if not i.isDead():
        return
    print("Boom!")
    self.destroy()

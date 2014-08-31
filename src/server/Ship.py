from Entity import Entity
from Component import *
from Missile import Missile
import sys

class Ship(Entity):
  def __init__(self, config, universe):
    super().__init__(config, universe)
    self.__dict__.update(config)
    temp = []
    for i in self.components:
      temp.append(findComponent(i['type'])(self, i))
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
    print("Ticking ship")
    for i in self.components:
      i.tick(duration)
  
  def tock(self):
    for i in self.components:
      if not i.isDead():
        return
    sys.exit("Boom!")
    self.destroy()
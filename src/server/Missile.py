from Entity import Entity
import physics

class Missile(Entity):
  def __init__(self, config, universe):
    super().__init__(config, universe)
    self.__dict__.update(config)
    print("New Missile")
    
  def fire(self, tube):
    print("Starting to fire missile")
    self.location = tube.ship.location + tube.position
  #  self.rotation = physics.rotate(tube.ship.rotation + tube.orientation, center=tube.ship.center)
    self.instantiate()
    print("Fired Missile!")

  def tick(self, duration):
    if self.pathing == "Dumb":
      return super.tick(duration)
    
  def collide(self, other):
    self.destroy()
    print("Missile hit!")
    
  def getDamage(self):
    if self.impactType == "Simple":
      return 10
    return 100000000000
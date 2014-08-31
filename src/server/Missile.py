from Entity import Entity

class Missile(Entity):
  def __init__(self, config, universe):
    super.__init__(config, universe)
    self.__dict__.update(config)
    
  def fire(self, tube):
    self.location = tube.ship.location + tube.relativeLocation
    self.rotation = physics.rotate(tube.ship.rotation + tube.relativeRotation, center=tube.ship.center)
    self.instantiate(self)

  def tick(self, duration):
    if self.pathing == "Dumb":
      return super.tick(duration)
    
  def collide(self, other):
    self.destroy()
    
  def getDamage(self):
    if self.impactType == "Simple":
      return 10
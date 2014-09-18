from Entity import Entity
import physics

class Missile(Entity):
  def __init__(self, config, universe):
    super().__init__(config, universe)
    self.__dict__.update(config)
    print("New Missile")
    
  def fire(self, tube):
    print("Starting to fire missile")
    self.location = tube.ship.location + ((tube.position * (tube.ship.radius + self.radius)) / tube.position.magnitude())
    print("Missile start loc:", self.location)
    print("Ship fire loc:", tube.ship.location)
    print("Ship radius:", tube.ship.radius)
    print("Tube location:", tube.position)
  #  self.rotation = physics.rotate(tube.ship.rotation + tube.orientation, center=tube.ship.center)
    self.rotation = physics.Vector(1,1,1)*(tube.position/tube.position.magnitude())
    self.velocity = self.rotation * 20
    self.instantiate()
    print("Fired Missile!")

  def tick(self, duration):
    if self.pathing == "Dumb":
      self.velocity += self.rotation*self.thrust
      return super().tick(duration)
    
  def collide(self, other):
    self.destroy()
    print("Missile hit!")
    
  def getDamage(self):
    if self.impactType == "Simple":
      return 10
    return 100000000000

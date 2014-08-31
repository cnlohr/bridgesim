from Entity import Entity

class Missile(Entity):
  def __init__(self, config, universe):
    super.__init__(self, universe)
    self.location = None
    self.rotation = None
    self.velocity = config['initialvelocity']
    self.thrust = config['thrust']
    self.turning = config['turning']
    self.drag = config['drag']
    self.pathing = config['pathing']
    self.energy = config['pathing']
    self.impactType = config['pathing']
    self.damage = config['damage']
    self.blastRadius = config['blastradius']
    
  def fire(self, tube):
    self.location = tube.ship.location + tube.relativeLocation
    self.rotation = physics.rotate(tube.ship.rotation + tube.relativeRotation, center=tube.ship.center)
    self.instantiate(self)

  def tick(self, duration):
    if self.pathing == "Dumb":
      return super.tick(self, duration)
    
    
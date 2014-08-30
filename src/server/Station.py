from Entity import Entity

class Station(Entity):
  def __init__(self, config):
    super.__init__(config)
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
    return super.tick(duration).extend([{[self.id, "weaponStocks"]:self.weaponStocks},
                                   {[self.id, "maxDock"]:self.maxDock},
                                   {[self.id, "docked"]:self.docked}])
  
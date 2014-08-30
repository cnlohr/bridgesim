from Entity import Entity

class Station(Entity):
  def __init__(self, config):
    super.__init__(config)
    self.weaponStocks = config['weaponStocks']
    self.maxDock = config['maxDock']
    self.docked = config['docked']
    self.producing = config['producing']
    self.rechargeRate = config['rechargeRate']

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

  def setProduction(self, thing):
    # thing should be a commodity of some sort
    self.building = thing
    self.buildProgress = 0

  def tick(self, duration):
    self.shields += self.shieldMultiplier * duration
    self.energy += self.energyMultiplier * duration

    if self.building:
      self.buildProgress += duration
      if self.buildProgress > self.building.buildCost:
        # We have built something!

        if self.building.name in self.weaponStocks:
          self.weaponStocks[self.building.name] += 1
        else:
          self.weaponStocks[self.building.name] = 1

        self.buildProgress -= self.building.buildCost

    if self.energy > 0:
      for ship in self.docked:
        if ship.energy < ship.maxEnergy:
          recharged = min(ship.maxEnergy - ship.energy, self.rechargeRate * duration, self.energy)
          ship.energy += recharged
          self.energy -= recharged

    return super.tick(duration).extend([{[self.id, "weaponStocks"]:self.weaponStocks},
                                   {[self.id, "maxDock"]:self.maxDock},
                                   {[self.id, "docked"]:self.docked}])

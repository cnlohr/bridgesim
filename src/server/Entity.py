class Entity:
  def __init__(self, universe):
    self.universe = universe
  
  def instantiate(self):
    self.universe.add(self)
    
  def destroy(self):
    self.universe.remove(self)
    
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

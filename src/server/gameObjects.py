from physics import *
import network as network
from random import randint

universe = None

def shutdown():
  network.shutdown()

class Universe:
  
  def __init__(self, TPS=30, difficulty=5):
    self.TPS = TPS
    self.difficulty = difficulty
    self.last_seen_tick = 0
    self.playerShips = []
    self.stations = []
    self.tubeAmmos = []
    self.enemies = []
    self.enemyGroups = []
    self.missiles = []
    self.enemyMissiles = []
    self.fighters = []
    self.referenceOrientation = [1,1,1] #this should be arbitrary; but changing it is useful for testing purposes sometimes.

  @property
  def timeMultiplier(self):
    return 1./TPS
    
  def tick(self, newTick):
    ticksToDo = newTick - self.last_seen_tick
    for i in self.physicsObjects:
      i.physics(ticksToDo)
    self.last_seen_tick = newTick
  
  @property
  def physicsObjects(self):
    return chain(self.playerShips, self.stations, self.enemyGroups, self.enemies, self.missiles, self.fighters)
  
  def state(self):
    print ("Player Ships:")
    for i in self.playerShips:
      print (" "+i.name)
    print ("Stations:")
    for i in self.stations:
      print (" "+i.name)
    print ("Ammo Types:")
    for i in self.tubeAmmos:
      print (" "+i.name)
    print ("Enemies:")
    for i in self.enemies:
      print (" "+i.name)
    print ("Enemy Groups:")
    for i in self.enemyGroups:
      print (" "+str(i.ID))
    print ("Missiles:")
    for i in self.missiles:
      print (" "+i.name)
    print ("Fighters:")
    for i in self.fighters:
      print (" "+i.name)
    
class TubeAmmo:
  name = "Uninitialized TubeAmmo"
  distance = 0
  loadCost = 0
  ammoLimit = 0
  buildCost = 0
  impactType = 0
  damage = 0
  blastRadius = 0
  thrust = 0
  turning = 0
  drag = 0
  pathing = 0
  energy = 0
  ammoGenerationWeight = 0
  def __init__(self, config):
    self.name = config['name']
    self.distance = float(config['distance'])
    self.loadCost = float(config['loadcost'])
    self.ammoLimit = float(config['ammolimit'])
    self.buildCost = float(config['buildcost'])
    self.impactType = float(config['impacttype'])
    self.damage = float(config['damage'])
    self.blastRadius = float(config['blastradius'])
    self.thrust = float(config['thrust'])
    self.turning = float(config['turning'])
    self.drag = float(config['drag'])
    self.pathing = float(config['pathing'])
    self.energy = float(config['energy'])
    self.ammoGenerationWeight = float(config['ammogenerationweight'])

class Station:
  location = [0,0,0]
  rotation = [1,0,0,0]
  velocity = [0,0,0]
  thrust = 0
  turning = 0
  shields = 500
  production = [.4,.1,.2,.3]
  underAttack = 0
  energy = 50000
  name = "DS1"
  stock = [4,1,2,3]
  canDock = 1
  health = 1000
  hasDocked = -1
  producing = 0
  progress = 0
  loadingWeapon = 0
  def __init__(self, i, universe):
    self.location = [(-1)**randint(1,2) * randint(500,5000),(-1)**randint(1,2) * randint(500,5000),0]
    self.rotation = [0,0,0,0]
    self.velocity = [0,0,0]
    self.thrust = 0
    self.turning = 0
    self.shields = 500
    self.production = [.4,.1,.2,.3]
    self.underAttack = 0
    self.energy = 50000
    self.name = "DS" + str(i+1)
    self.stock = [4,1,2,3]
    self.canDock = 1
    self.health = 1000
    self.hasDocked = -1
    self.producing = -1
    self.progress = 0
    self.loadingWeapon = 0
  def physics(self):
    if self.hasDocked >= 0:
      supply(self)
    if self.shields > 200:
      if self.producing == -1:
        min = 0
        for i in range(len(self.stock)):
          if self.stock[i]/self.production[i] < self.stock[min]/self.production[min]:
            min = i
        self.producing = min
        self.progress = universe.TPS * universe.tubeAmmos[self.producing].buildCost
      else:
        self.progress = self.progress - 1
      self.energy = self.energy + 2 * universe.timeMultiplier
      if self.progress == 0:
        self.stock[self.producing] = self.stock[self.producing] + 1
        self.producing = -1
    else:
      self.shields = self.shields + .03 * universe.timeMultiplier
    if self.shields < 500:
      self.shields = self.shields + .1 * universe.timeMultiplier
      self.energy = self.energy - 6 * universe.timeMultiplier
    if self.progress == 0:
      updates.extend(i.tick(duration))
      self.stock[self.producing] = self.stock[self.producing] + 1
      min = 0
      for i in range(len(self.stock)):
        if self.stock[i]/self.production[i] < self.stock[min]/self.production[min]:
          min = i
      self.producing = min
      self.progress = universe.TPS * universe.tubeAmmos[self.producing].buildCost
    network.update("/sta/"+self.name+"/loc", self.location)

  def dock(self, playerShip):
    if self.canDock == 1:
      self.canDock = -1
      self.hasDocked = playerShip
  def undock(self, playerShip):
    if self.hasDocked == playerShip:
      self.hasDocked = -1
      self.canDock = 1
  def supply(self):
    if playerShips[self.hasDocked].energy < 1000:
      playerShips[self.hasDocked].energy = playerShips[self.hasDocked].energy + 30 * timeMultiplier
    if playerShips[self.hasDocked].energy > 1000:
      playerShips[self.hasDocked].energy = 1000
      self.energy = self.energy - 30 * timeMultiplier
    self.loadingWeapon = self.loadingWeapon + 1
    if self.loadingWeapon > 2 * TPS:
      for i in range(4):
        if playerShips[self.hasDocked].ammunition[i] < playerShips[self.hasDocked].ammunitionMax[i] & self.loadingWeapon > 0:
          playerShips[self.hasDocked].ammunition[i] = playerShips[self.hasDocked].ammunition[i] + 1
          self.loadingWeapon = 0
  def damage(self, damage, sourceType, source, location, frequency):
    if frequency != -1:
      if damage > 5 * self.shields:
        damage = damage - 5 * self.shields
      else:
        self.shields[shieldHit] = self.shields - damage/5
        damage = 0
    else:
      if damage > 5 * self.shields * self.shieldResistance[frequency]:
        damage = damage - 5 * self.shields * self.shieldResistance[frequency]
      else:
        self.shields = self.shields - damage/(5 * self.shieldResistance[frequency])
        damage = 0
    self.health = self.health - damage
    if self.health <= 0:
      #explode here
      print(self.name + "was killed by" + source + "using" + sourceType)

class Tube:
  loadingProgress = -1
  unloadingProgress = -1
  ammoType = -1
  location = [0,0,0]
  velocity = [0,0,0]
  playerID = -1
  def __init__(self, location, velocity, playerID):
    self.location = list(location)
    self.velocity = list(velocity)
    self.playerID = playerID
  def load(self, ammo):
    global tubeAmmos
    self.unloadingProgress = -1
    if self.ammoType == -1:
      self.loadingProgress = tubeAmmos[ammo].loadCost
      self.ammoType = ammo
  def unload(self):
    global tubeAmmos
    self.loadingProgress = -1
    if self.ammoType != -1:
      self.unloadingProgress = tubeAmmos[self.ammoType].loadCost
  def physics(self):
    if self.loadingProgress > 0:
      self.loadingProgress = self.loadingProgress - 1
    if self.unloadingProgress > 0:
      self.unloadingProgress = self.unloadingProgress - 1
    if self.loadingProgress == 0:
      self.loadingProgress = -1
    if self.unloadingProgress == 0:
      self.ammoType = -1
      self.unloadingProgress = -1
  def fire(self, target):
    global playerShips
    global missiles
    s = playerMissile(self.ammoType, target, self.playerID, self.location, self.rotation, self.velocity)
    #TODO add the tube loc,vel,rot to the player loc,vel,rot in a sensible way
    missiles.append(s)
    
class Beam:
  damage = 0
  distance = 0
  spread = 0
  facing = 0
  loadingProgress = -1
  antimissile = -1
  loadingCost = 0
  playerID = -1
  def __init__(self, playerID, damage, distance, spread, facing, antimissile, loadTime):
    global TPS
    self.playerID = playerID
    self.damage = damage
    self.distance = distance
    self.spread = spread
    self.facing = facing
    self.antimissile = antimissile
    self.loadingCost = TPS * loadTime
  def physics(self, target, targetType):
    global enemies
    global enemyMissiles
    global playerShips
    if self.antimissile == -1:
      if self.targetType == "enemy":
        if Distance(playerShips[self.playerID].location, enemies[self.target].location) <= self.distance:
          enemies[self.target].damage(self.damage, "Beam", playerShips[self.playerID].name, playerShips[self.playerID].location, playerShips[self.playerID].frequency)
    
class playerMissile:
  location = [0,0,0]
  rotation = [0,0,0,0]
  velocity = [0,0,0]
  thrust = 0
  turning = 0
  drag = 0
  pathing = 0
  energy = 0
  impactType = 0
  damage = 0
  blastRadius = 0
  target = -1
  def __init__(self, ammoID, enemyID, playerID, location, rotation, velocity):
    global tubeAmmos
    global enemies
    global playerShips
    if enemyID > -1:
      self.target = enemyID
    else:
      print("No valid target assigned")
    self.location = list(location)
    self.rotation = list(rotation)
    self.velocity = list(velocity)
    self.thrust = tubeAmmos[ammoID].thrust
    self.turning = tubeAmmos[ammoID].turning
    self.drag = tubeAmmos[ammoID].drag
    self.pathing = tubeAmmos[ammoID].pathing
    self.energy = tubeAmmos[ammoID].energy
    self.impactType = tubeAmmos[ammoID].impactType
    self.damage = tubeAmmos[ammoID].damage
    self.blastRadius = tubeAmmos[ammoID].blastRadius
  def physics(self):
    if self.pathing == 0: #0 indicates omnipotent homing - this should never miss.
      self.rotation = OrientationQuaternion(self.location, universe.enemies[self.target].location, universe.referenceOrientation)
      velocityMultiplier = 100
      if Distance(self.location, universe.enemies[self.target].location) < velocityMultiplier:
        velocityMultiplier = Distance(self.location, universe.enemies[self.target].location)
      self.velocity = VectorMultiply(velocityMultiplier, OrientationVector(self.rotation, universe.referenceOrientation))
      self.location = VectorAdd(self.location, VectorMultiply(universe.timeMultiplier, self.velocity))
    if self.pathing == 1: #1 indicates linear homing (turn towards present target location)
      self.rotation = TurnTowards(self.rotation, self.location, VectorAdd(self.location, VectorMultiply(-1, universe.enemies[self.target].location)), self.turning, universe.referenceOrientation, universe.timeMultiplier)
      self.velocity = VectorMultiply(velocityMultiplier, OrientationVector(self.rotation, universe.referenceOrientation))
      self.location = VectorAdd(self.location, VectorMultiply(universe.timeMultiplier, self.velocity))
    if self.pathing == 2: #2 indicates second order homing (turn towards future target location)
      self.rotation = TurnTowards(self.rotation, self.location, VectorAdd(self.location, VectorMultiply(-1, universe.enemies[self.target].location)), self.turning, universe.referenceOrientation, universe.timeMultiplier)
      self.velocity = VectorMultiply(velocityMultiplier, OrientationVector(self.rotation, universe.referenceOrientation))
      self.location = VectorAdd(self.location, VectorMultiply(universe.timeMultiplier, self.velocity))
    if self.pathing == 3: #3 indicates unguided fire (move in a straight line)
      self.velocity = VectorAdd(VectorMultiply(1-self.drag, self.velocity), VectorMultiply(self.thrust, OrientationVector(self.rotation, universe.referenceOrientation)))
      self.location = VectorAdd(self.location, VectorMultiply(universe.timeMultiplier, self.velocity))
    #if self.pathing == 4: #4 indicates target leading unguided fire (move in a straight line towards future target location)
    #if self.pathing == 5: #5 indicates an absolute destination (linear homing towards a specified location)
    if Distance(self.location, universe.enemies[self.target].location) < 5:
      impact(self)
  def impact(self):
    if self.impactType == 0: # omnipotent impact: instantly kills its target.
      universe.enemies[self.target].explode(enemies[self.target])
      del universe.enemies[self.target]
    if self.impactType == 1: # explosive impact: damages every ship and missile within the blast radius, with damage reduced by distance.
      for i in range(len(universe.enemies)):
        s = len(universe.enemies) - i - 1
        if Distance(self.location, universe.enemies[s].location) < self.blastRadius:
          universe.enemies[s].health = universe.enemies[s].health - self.damage * (1 - Distance(self.location, universe.enemies[s].location)/self.blastRadius)
          if universe.enemies[s].health <= 0:
            universe.enemies[s].explode(enemies[s])
            del universe.enemies[s]
      for i in range(len(universe.missiles)):
        s = len(universe.missiles) - i - 1
        if Distance(self.location, universe.missiles[s].location) < self.blastRadius/2:
          del universe.missiles[s]
      for i in range(len(universe.playerShips)):
        s = len(universe.playerShips) - i - 1
        if Distance(self.location, universe.playerShips[s].location) < self.blastRadius:
          universe.playerShips[s].health = universe.playerShips[s].health - self.damage * (1 - Distance(self.location, universe.playerShips[s].location)/self.blastRadius)
          if universe.playerShips[s].health <= 0:
            universe.playerShips[s].explode(universe.playerShips[s])
            del universe.playerShips[s]
    #if self.impactType == 2: # single target impact: damages the target ship, but nothing else.
    #if self.impactType == 3: # mine deployment: creates a mine object that will explode if a ship gets near enough to it.
    #if self.impactType == 4: # bait deployment: creates a fake station that will lure close enemies. Very minimal health.
    #if self.impactType == 5: # cluster bomb: selects 6 nearby points randomly, and sets off an explosive at each point.
    #if self.impactType == 6: # nuke cluster bomb: run. Just, run.
    #if self.impactType == 7: # poison cloud; deals steady damage to anything entering it
    #if self.impactType == 8: # EMP explosion
    #TODO primitive collision detection.
    
class PlayerShip:
  location = [0,0,0]
  rotation = [1,0,0,0]
  velocity = [0,0,0]
  drag = .01 
  thrust = 1
  turning = 1
  accelerating = 0
  orientationTarget = [0,0,0,0]
  turning = [0,0,0,0]
  scanningSpeed = 1
  repairCrews = [] #TODO implement
  tubes = [] #TODO
  beams = [] #TODO
  fighters = [] #TODO implement
  shields = [100,100]
  shieldResistance = [1,1,1,1,1]
  name = "Fartemis"
  energy = 1000
  dockedAt = 0
  power = [1,1,1,1,1,1,1,1]
  heatLevel = [0,0,0,0,0,0,0,0]
  cooling = [0,0,0,0,0,0,0,0]
  availableCooling = 8 - sum(cooling)
  shipType = "Light Cruiser"
  shipID = 0
  targetingType = -1
  targetingID = 0
  scanningID = -1
  scanningProgress = [0] #TODO use a dictionary for this.
  ammunition = [2,8,4,4]
  ammunitionMax = [3,12,6,6]
  def __init__(self, initID, initName, universe):
    self.scanningProgress = [0] * len(universe.enemies)
    self.shipID = initID
    self.name = initName
  def physics(self):
    global timeMultiplier
    #TODO get player input here
    if self.turning != [0,0,0,0]:
      self.rotation = QuaternionMult(self.turning, self.rotation)
    elif self.orientationTarget != [0,0,0,0]:
      self.rotation = TurnTowards(self.rotation, self.location, OrientationVector(self.orientationTarget), self.turning, universe.referenceOrientation, universe.timeMultiplier)
    self.velocity = VectorAdd(VectorMultiply((1 - self.drag), self.velocity), VectorMultiply(universe.timeMultiplier * self.accelerating * self.thrust * self.power[5], OrientationVector(self.rotation, universe.referenceOrientation)))
    self.location = VectorAdd(self.location, VectorMultiply(universe.timeMultiplier, self.velocity))
    #TODO handle firing missiles, beams
  def fire(self, tubeID):
    self.tubes[tubeID].fire(self.targetingID)
  def damage(self, damage, sourceType, source, location, frequency):
    angle = Angle(OrientationVector(OrientationQuaternion(self.location, location, universe.referenceOrientation)), OrientationVector(self.rotation))
    shieldHit = 0
    if angle >= math.pi/2: #Front Shields hit
      shieldHit = 0
    if frequency != -1:
      if damage > 5 * self.shields[shieldHit]:
        damage = damage - 5 * self.shields[shieldHit]
      else:
        self.shields[shieldHit] = self.shields[shieldHit] - damage/5
        damage = 0
    else:
      if damage > 5 * self.shields[shieldHit] * self.shieldResistance[frequency]:
        damage = damage - 5 * self.shields[shieldHit] * self.shieldResistance[frequency]
      else:
        self.shields[shieldHit] = self.shields[shieldHit] - damage/(5 * self.shieldResistance[frequency])
        damage = 0
    self.health = self.health - damage
    if self.health <= 0:
      #explode here
      print(self.name + "was killed by" + source + "using" + sourceType)

class EnemyGroup:
  ID = "Uninitialized ID"
  location = [0,0,0]
  rotation = [0,0,0,0]
  velocity = [0,0,0]
  target = -1
  targetLocation = [0,0,0]
  def __init__(self, idnumber, universe):
    self.ID = idnumber
    self.location = [((-1)**randint(1,2))*randint(10000,50000),((-1)**randint(1,2))*randint(10000,50000),0]
    min = 0
    dist = [0] * len(universe.stations)
    for i in range(len(universe.stations)):
      dist[i] = Distance(self.location, universe.stations[i].location)
      if dist[i] < dist[min]:
        min = i
    self.rotation = OrientationQuaternion(self.location, universe.stations[min].location, universe.referenceOrientation)
    self.velocity = 100*Normalize(OrientationVector(self.rotation, universe.referenceOrientation))
    self.targetLocation = universe.stations[min].location
    for i in range(universe.difficulty):
      name = chr(int(self.ID%26+ord("A")))+ chr(int(self.ID/26)+ord("A")) + str(i).zfill(2)
      shipType = "Generic Ship Type"
      s = enemyShip(self.location, self.rotation, self.velocity, name, self.ID, shipType)
      universe.enemies.append(s)
  def physics(self):
    if self.target > -1:
      if Distance(universe.playerShips[self.target], self.location) > 5000:
        self.target = -1
    if self.target == -1:
      for i in range(len(universe.playerShips)):
          if Distance(self.location, universe.playerShips[i].location) < 3000:
            self.target = i
    if self.target == -1:
      dist = [0] * len(universe.stations)
      min = 0
      for i in range(len(universe.stations)):
        dist[i] = Distance(self.location, universe.stations[i].location)
        if dist[i] < dist[min]:
          min = i
      self.targetLocation = list(universe.stations[min].location)
      self.rotation = OrientationQuaternion(self.location, universe.stations[min].location, universe.referenceOrientation)
      self.velocity = 100*Normalize(OrientationVector(self.rotation, universe.referenceOrientation))

class enemyShip():
  location = [0,0,0]
  rotation = [0,0,0,0]
  velocity = [0,0,0]
  drag = .03
  thrust = 1
  turning = 1
  repairCrews = []
  tubes = []
  beams = []
  fighters = []
  shields = [100,100]
  shieldResistance = [1,1,1,1,1]
  name = "Unnamed"
  shipType = -1
  groupID = -1
  health = 600
  target = -1
  targetLocation = [0,0,0]
  def __init__(self, location, rotation, velocity, name, groupID, shipType):
    self.location = list(location)
    for i in range(len(self.location)):
      self.location[i] = self.location[i] + randint(-50, 50)
    self.rotation = list(rotation)
    self.velocity = list(velocity)
    self.name = name
    self.groupID = groupID
    self.shipType = shipType
  def physics(self):
    self.target = universe.enemyGroups[self.groupID].target
    if self.target == -1:
      self.targetLocation = list(universe.enemyGroups[self.groupID].targetLocation)
    else:
      self.targetLocation = list(universe.playerShips[self.target].location)
    if Distance(self.location, self.targetLocation) > 2*Magnitude(self.velocity)/self.drag + 50:
      self.rotation = TurnTowards(self.rotation, self.location, self.targetLocation, self.turning, universe.referenceOrientation, universe.timeMultiplier)
      self.velocity = VectorAdd(VectorMultiply((1 - self.drag), self.velocity), VectorMultiply(universe.timeMultiplier * self.thrust, OrientationVector(self.rotation, universe.referenceOrientation)))
      self.location = VectorAdd(self.location, VectorMultiply(universe.timeMultiplier, self.velocity))
    else:
      self.rotation = TurnTowards(self.rotation, self.location, self.targetLocation, self.turning, universe.referenceOrientation, universe.timeMultiplier)
      self.velocity = VectorMultiply(1-self.drag, self.velocity)
      self.location = VectorAdd(self.location, VectorMultiply(universe.timeMultiplier, self.velocity))
    #TODO put some firing here.
    network.update("/ene/"+self.name+"/loc", self.location)

  def damage(self, damage, sourceType, source, location, frequency):
    angle = Angle(OrientationVector(OrientationQuaternion(self.location, location), universe.referenceOrientation), OrientationVector(self.rotation))
    shieldHit = 0
    if angle >= math.pi/2: #Front Shields hit
      shieldHit = 0
    if frequency != -1:
      if damage > 5 * self.shields[shieldHit]:
        damage = damage - 5 * self.shields[shieldHit]
      else:
        self.shields[shieldHit] = self.shields[shieldHit] - damage/5
        damage = 0
    else:
      if damage > 5 * self.shields[shieldHit] * self.shieldResistance[frequency]:
        damage = damage - 5 * self.shields[shieldHit] * self.shieldResistance[frequency]
      else:
        self.shields[shieldHit] = self.shields[shieldHit] - damage/(5 * self.shieldResistance[frequency])
        damage = 0
    self.health = self.health - damage
    if self.health <= 0:
      #explode here
      print(self.name + "was killed by" + source + "using" + sourceType)

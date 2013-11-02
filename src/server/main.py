from ctypes import *
import time
import math

# Load in functions
cent = CDLL("../network/cent.so")
StartCentServer = cent.StartCentServer;
StartCentServer.restype = c_void_p;
CreateCent = cent.CreateCent;
CreateCent.restype = c_void_p;
ChangeValue = cent.ChangeValue;
ChangeValue.argtypes = [c_void_p, c_void_p, c_int]
CentServerAddCB = cent.CentServerAddCB;
CentServerAddCB.argtypes = [ c_void_p, c_char_p, c_void_p, c_void_p ];
CentGetDataFromCent_Float = cent.CentGetDataFromCent;
CentGetDataFromCent_Float.argtypes = [ c_void_p ];
CentGetDataFromCent_Float.restype = POINTER(c_float)

#types
CENTCB = CFUNCTYPE( c_void_p, c_void_p, c_void_p, c_void_p );

def my_callback_function( conn, data, ids ):
        fields = CentGetDataFromCent_Float( data );

server_handle = StartCentServer(b"0.0.0.0", 8553);
CentServerAddCB( server_handle, b"/*", CENTCB(my_callback_function), 44 );


#TODO check if the player is close enough to dock, handle moving them in to docked position
#TODO make drag on entities vary with TPS
#TODO handle explosion events, playerShipDamaged events, etc
#TODO make the player able to send messages
#TODO finish enemy AI
#  make the enemy able to attack
#  make the enemy move to a good attacking position
#  account for enemy damage

from random import randint
import math

playerShips = []
stations = []
tubeAmmos = []
enemies = []
enemyGroups = []
missiles = []
enemyMissiles = []
fighters = []
referenceOrientation = [1,1,1] #this should be arbitrary; but changing it is useful for testing purposes sometimes.
TPS = 30
timeMultiplier = 1/TPS
difficulty = 5

def VectorMultiply(scalar, vector):
  result = [0] * len(vector)
  for i in range(len(vector)):
    result[i] = scalar * vector[i]
  return result

def VectorAdd(a, b):
  c = [0] * len(b)
  for i in range(len(b)):
    c[i] = a[i] + b[i]
  return c

def Dot(a,b): #Dot returns the dot product of two vectors. The vectors must be of the same length, or else Dot will return 0.
  if len(a) == len(b):
    c = 0
    for i in range(len(a)):
      c = c + a[i] * b[i]
    return c
  print("Dot was given vectors of diffrent lengths. a:", a, "b:", b, "Returning 0.")
  return 0

def Cross(a,b): #Cross returns the cross product of 2 vectors of length 3, or a zero vector if the vectors are not both length 3.
  if len(a) == 3 & len(b) == 3:
    c = [a[1]*b[2] - a[2]*b[1], a[2]*b[0] - a[0]*b[2], a[0]*b[1] - a[1]*b[0]]
    return c
  print("Cross was given a vector whose length is not 3. a:", a, "b:", b, "Returning a zero vector.")
  return [0,0,0]

def Normalize(a): #Normalize returns a normalized vector, unless it is given a zero vector, in which case it returns the zero vector, and complains.
  s = 0
  c = [0] * len(a)
  for i in range(len(a)):
    s = s + a[i]**2
  s = math.sqrt(s)
  if s == 0:
    print("Normalize was given a zero vector. This is not necessarily an error; returning zero vector.")
    return c
  for i in range(len(a)):
    c[i] = a[i]/s
  return c

def Magnitude(a): #Magnitude returns the square root of the sum of the numbers of a list squared.
  c = 0
  for i in range(len(a)):
    c = c + a[i]**2
  return math.sqrt(c)

def Distance(a, b): #Distance returns the distance between two vectors of length 3.
  if len(a) == 3 & len(b) == 3:
    c = (a[0]-b[0])**2 + (a[1]-b[1])**2 + (a[2]-b[2])**2
    return math.sqrt(c)
  print("Distance was given vectors whose lengths are not both 3. a:", a, "b:", b, "Returning 0.")
  return 0

def Angle(a,b):
  return math.acos(Dot(a,b)/(Magnitude(a)*Magnitude(b)))

def AngleVectorToQuaternion(angle, vector):
  normvector = Normalize(list(vector))
  angle = angle/2
  quaternion = [math.cos(angle), math.sin(angle)*normvector[0], math.sin(angle)*normvector[1], math.sin(angle)*normvector[2]]
  return Normalize(quaternion)

def OrientationQuaternion(location, target):
  global referenceOrientation
  reference = Normalize(referenceOrientation)
  facing = [0,0,0]
  for i in range(3):
    facing[i] = target[i] - location[i]
  if Magnitude(facing) == 0:
    return [1,0,0,0]
  perpendicular = Cross(reference, facing)
  angle = Angle(reference, facing)
  quaternion = AngleVectorToQuaternion(angle, perpendicular)
  return quaternion

def QuaternionMultiply(apoint, bpoint):
  a = list(apoint)
  b = list(bpoint)
  if len(a) == 3:
    a = [0, a[0], a[1], a[2]]
  if len(b) == 3:
    b = [0, b[0], b[1], b[2]]
  if len(a) == 4 & len(b) == 4:
    result = [0,0,0,0]
    result[0] = a[0]*b[0] - a[1]*b[1] - a[2]*b[2] - a[3]*b[3]
    result[1] = a[0]*b[1] + a[1]*b[0] + a[2]*b[3] - a[3]*b[2]
    result[2] = a[0]*b[2] + a[2]*b[0] + a[3]*b[1] - a[1]*b[3]
    result[3] = a[0]*b[3] + a[3]*b[0] + a[1]*b[2] - a[2]*b[1]
    return result
  print("QuaternionMultiply was given lists of the wrong length. Returning identity quaternion.", a, b)
  return [1,0,0,0]

def RotateVectorByQuaternion(vectorpoint, quaternionpoint):
  vector = list(vectorpoint)
  quaternion = Normalize(list(quaternionpoint))
  inversequaternion = [quaternion[0], -quaternion[1], -quaternion[2], -quaternion[3]]
  result = QuaternionMultiply(QuaternionMultiply(quaternion, vector), inversequaternion)
  vectorresult = [result[1], result[2], result[3]]
  if math.fabs(result[0]) > 10 ** (-15):
    print("RotateVectorByQuaternion gave a non-zero real result for", vector, quaternion)
  return vectorresult

def RotateQuaternionByQuaternion(apoint, bpoint):
  a = Normalize(list(apoint))
  b = Normalize(list(bpoint))
  inverseb = [b[0], -b[1], -b[2], -b[3]]
  result = QuaternionMultiply(QuaternionMultiply(b, a), inverseb)
  return result

def TurnTowards(rotationpoint, locationpoint, targetLocationpoint, turning):
  global timeMultiplier
  facing = OrientationVector(list(rotationpoint))
  rotation = list(rotationpoint)
  location = list(locationpoint)
  targetLocation = list(targetLocationpoint)
  targetFacing = [0,0,0]
  for i in range(3):
    targetFacing[i] = targetLocation[i] - location[i]
  if Magnitude(targetFacing) == 0:
    return rotation
  perpendicular = Cross(facing, targetFacing)
  angle = Angle(facing, targetFacing)
  if angle > timeMultiplier * .4 * turning:
    angle = timeMultiplier * .4 * turning
  if angle < -timeMultiplier * .4 * turning:
    angle = -timeMultiplier * .4 * turning
  rotationQuaternion = AngleVectorToQuaternion(angle, perpendicular)
  result = RotateQuaternionByQuaternion(rotation, rotationQuaternion)
  return result

def DerollFacing(quaternionpoint): #doesn't work yet
  q = Normalize(list(quaternionpoint))
  roll  = math.atan2(2*q[2]*q[0] - 2*q[1]*q[3], 1 - 2*q[2]*q[2] - 2*q[3]*q[3])
  vector = Normalize(OrientationVector(q))
  derolled = RotateQuaternionByQuaternion(AngleVectorToQuaternion(-1 * roll, vector),q)
  return derolled
  
def CheckRoll(quaternionpoint):
  q = list(quaternionpoint)
  roll  = atan2(2*q[2]*q[0] - 2*q[1]*q[3], 1 - 2*q[2]*q[2] - 2*q[3]*q[3])
  return roll

def OrientationVector(quaternionpoint):
  global referenceOrientation
  quaternion = list(quaternionpoint)
  reference = Normalize(referenceOrientation)
  return RotateVectorByQuaternion(reference, quaternion)

def Tick(input):
  for i in range(input):
    for i in playerShips:
      #i.getInput()
      i.physics()
    for i in stations:
      i.physics()
    for i in enemyGroups:
      i.physics()
    for i in enemies:
      i.physics()
    for i in missiles:
      i.physics()
    for i in fighters:
      #i.getInput()
      i.physics()

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
  def init(self, weaponLine):
    properties = weaponLine.split()
    self.name = properties[0]
    self.distance = float(properties[1])
    self.loadCost = float(properties[2])
    self.ammoLimit = float(properties[3])
    self.buildCost = float(properties[4])
    self.impactType = float(properties[5])
    self.damage = float(properties[6])
    self.blastRadius = float(properties[7])
    self.thrust = float(properties[8])
    self.turning = float(properties[9])
    self.drag = float(properties[10])
    self.pathing = float(properties[11])
    self.energy = float(properties[12])
    self.ammoGenerationWeight = float(properties[13])

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
  def init(self, i):
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
    global TPS
    global timeMultiplier
    global weapons
    global playerShips
    global tubeAmmos
    if self.hasDocked >= 0:
      supply(self)
    if self.shields > 200:
      if self.producing == -1:
        min = 0
        for i in range(len(self.stock)):
          if self.stock[i]/self.production[i] < self.stock[min]/self.production[min]:
            min = i
        self.producing = min
        self.progress = TPS * tubeAmmos[self.producing].buildCost
      else:
        self.progress = self.progress - 1
      self.energy = self.energy + 2 * timeMultiplier
      if self.progress == 0:
        self.stock[self.producing] = self.stock[self.producing] + 1
        self.producing = -1
    else:
      self.shields = self.shields + .03 * timeMultiplier
    if self.shields < 500:
      self.shields = self.shields + .1 * timeMultiplier
      self.energy = self.energy - 6 * timeMultiplier
    if self.progress == 0:
      self.stock[self.producing] = self.stock[self.producing] + 1
      min = 0
      for i in range(len(self.stock)):
        if self.stock[i]/self.production[i] < self.stock[min]/self.production[min]:
          min = i
      self.producing = min
      self.progress = TPS * tubeAmmos[self.producing].buildCost
    floats = c_float * 3
    myvar = floats(self.location[:])
    ChangeValue( server_handle, CreateCent( b"/e/sta/"+self.name+"/loc", 0x80, 1, 12, myvar ), 1 );
  def dock(self, playerShip):
    if self.canDock == 1:
      self.canDock = -1
      self.hasDocked = playerShip
  def undock(self, playerShip):
    if self.hasDocked == playerShip:
      self.hasDocked = -1
      self.canDock = 1
  def supply(self):
    global timeMultiplier
    global TPS
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
  def init(self, location, velocity, playerID):
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
    s = playerMissile()
    #TODO add the tube loc,vel,rot to the player loc,vel,rot in a sensible way
    s.init(self.ammoType, target, self.playerID, self.location, self.rotation, self.velocity)
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
  def init(self, playerID, damage, distance, spread, facing, antimissile, loadTime):
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
  def init(self, ammoID, enemyID, playerID, location, rotation, velocity):
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
    global timeMultiplier
    global tubeAmmos
    global enemies
    if self.pathing == 0: #0 indicates omnipotent homing - this should never miss.
      self.rotation = OrientationQuaternion(self.location, enemies[self.target].location)
      velocityMultiplier = 100
      if Distance(self.location, enemies[self.target].location) < velocityMultiplier:
        velocityMultiplier = Distance(self.location, enemies[self.target].location)
      self.velocity = VectorMultiply(velocityMultiplier, OrientationVector(self.rotation))
      self.location = VectorAdd(self.location, VectorMultiply(timeMultiplier, self.velocity))
    if self.pathing == 1: #1 indicates linear homing (turn towards present target location)
      self.rotation = TurnTowards(self.rotation, self.location, VectorAdd(self.location, VectorMultiply(-1, enemies[self.target].location)), self.turning)
      self.velocity = VectorMultiply(velocityMultiplier, OrientationVector(self.rotation))
      self.location = VectorAdd(self.location, VectorMultiply(timeMultiplier, self.velocity))
    if self.pathing == 2: #2 indicates second order homing (turn towards future target location)
      self.rotation = TurnTowards(self.rotation, self.location, VectorAdd(self.location, VectorMultiply(-1, enemies[self.target].location)), self.turning)
      self.velocity = VectorMultiply(velocityMultiplier, OrientationVector(self.rotation))
      self.location = VectorAdd(self.location, VectorMultiply(timeMultiplier, self.velocity))
    if self.pathing == 3: #3 indicates unguided fire (move in a straight line)
      self.velocity = VectorAdd(VectorMultiply(1-self.drag, self.velocity), VectorMultiply(self.thrust, OrientationVector(self.rotation)))
      self.location = VectorAdd(self.location, VectorMultiply(timeMultiplier, self.velocity))
    #if self.pathing == 4: #4 indicates target leading unguided fire (move in a straight line towards future target location)
    #if self.pathing == 5: #5 indicates an absolute destination (linear homing towards a specified location)
    if Distance(self.location, enemies[self.target].location) < 5:
      impact(self)
  def impact(self):
    global enemies
    global missiles
    global playerShips
    if self.impactType == 0: # omnipotent impact: instantly kills its target.
      enemies[self.target].explode(enemies[self.target])
      del enemies[self.target]
    if self.impactType == 1: # explosive impact: damages every ship and missile within the blast radius, with damage reduced by distance.
      for i in range(len(enemies)):
        s = len(enemies) - i - 1
        if Distance(self.location, enemies[s].location) < self.blastRadius:
          enemies[s].health = enemies[s].health - self.damage * (1 - Distance(self.location, enemies[s].location)/self.blastRadius)
          if enemies[s].health <= 0:
            enemies[s].explode(enemies[s])
            del enemies[s]
      for i in range(len(missiles)):
        s = len(missiles) - i - 1
        if Distance(self.location, missiles[s].location) < self.blastRadius/2:
          del missiles[s]
      for i in range(len(playerShips)):
        s = len(playerShips) - i - 1
        if Distance(self.location, playerShips[s].location) < self.blastRadius:
          playerShips[s].health = playerShips[s].health - self.damage * (1 - Distance(self.location, playerShips[s].location)/self.blastRadius)
          if playerShips[s].health <= 0:
            playerShips[s].explode(playerShips[s])
            del playerShips[s]
    #if self.impactType == 2: # single target impact: damages the target ship, but nothing else.
    #if self.impactType == 3: # mine deployment: creates a mine object that will explode if a ship gets near enough to it.
    #if self.impactType == 4: # bait deployment: creates a fake station that will lure close enemies. Very minimal health.
    #if self.impactType == 5: # cluster bomb: selects 6 nearby points randomly, and sets off an explosive at each point.
    #if self.impactType == 6: # nuke cluster bomb: run. Just, run.
    #if self.impactType == 7: # poison cloud; deals steady damage to anything entering it
    #if self.impactType == 8: # EMP explosion
    #TODO primitive collision detection.
    
class PlayerShip:
  global enemies
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
  scanningProgress = [0] * len(enemies) #TODO use a dictionary for this.
  ammunition = [2,8,4,4]
  ammunitionMax = [3,12,6,6]
  def init(self, initID, initName):
    self.shipID = initID
    self.name = initName
  def physics(self):
    global timeMultiplier
    #TODO get player input here
    if self.turning != [0,0,0,0]:
      self.rotation = QuaternionMult(self.turning, self.rotation)
    elif self.orientationTarget != [0,0,0,0]:
      self.rotation = TurnTowards(self.rotation, self.location, OrientationVector(self.orientationTarget), self.turning)
    self.velocity = VectorAdd(VectorMultiply((1 - self.drag), self.velocity), VectorMultiply(timeMultiplier * self.accelerating * self.thrust * self.power[5], OrientationVector(self.rotation)))
    self.location = VectorAdd(self.location, VectorMultiply(timeMultiplier, self.velocity))
    #TODO handle firing missiles, beams
  def fire(self, tubeID):
    self.tubes[tubeID].fire(self.targetingID)
  def damage(self, damage, sourceType, source, location, frequency):
    angle = Angle(OrientationVector(OrientationQuaternion(self.location, location)), OrientationVector(self.rotation))
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

class enemyGroup:
  global enemyGroups
  ID = "Uninitialized ID"
  location = [0,0,0]
  rotation = [0,0,0,0]
  velocity = [0,0,0]
  target = -1
  targetLocation = [0,0,0]
  def init(self, idnumber):
    global difficulty
    global stations
    global enemies
    self.ID = idnumber
    self.location = [((-1)**randint(1,2))*randint(10000,50000),((-1)**randint(1,2))*randint(10000,50000),0]
    min = 0
    dist = [0] * len(stations)
    for i in range(len(stations)):
      dist[i] = Distance(self.location, stations[i].location)
      if dist[i] < dist[min]:
        min = i
    self.rotation = OrientationQuaternion(self.location, stations[min].location)
    self.velocity = 100*Normalize(OrientationVector(self.rotation))
    self.targetLocation = stations[min].location
    for i in range(difficulty):
      name = "A" + str(0) + str(i)
      shipType = "Generic Ship Type"
      s = enemyShip()
      s.init(self.location, self.rotation, self.velocity, name, self.ID, shipType)
      enemies.append(s)
  def physics(self):
    global stations
    global playerShips
    global enemies
    if self.target > -1:
      if Distance(playerShips[self.target], self.location) > 5000:
        self.target = -1
    if self.target == -1:
      for i in range(len(playerShips)):
          if Distance(self.location, playerShips[i].location) < 3000:
            self.target = i
    if self.target == -1:
      dist = [0] * len(stations)
      min = 0
      for i in range(len(stations)):
        dist[i] = Distance(self.location, stations[i].location)
        if dist[i] < dist[min]:
          min = i
      self.targetLocation = list(stations[min].location)
      self.rotation = OrientationQuaternion(self.location, stations[min].location)
      self.velocity = 100*Normalize(OrientationVector(self.rotation))

class enemyShip():
  global playerShips
  global stations
  global enemyGroups
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
  def init(self, location, rotation, velocity, name, groupID, shipType):
    self.location = list(location)
    for i in range(len(self.location)):
      self.location[i] = self.location[i] + randint(-50, 50)
    self.rotation = list(rotation)
    self.velocity = list(velocity)
    self.name = name
    self.groupID = groupID
    self.shipType = shipType
  def physics(self):
    global timeMultiplier
    global enemyGroups
    global playerShips
    self.target = enemyGroups[self.groupID].target
    if self.target == -1:
      self.targetLocation = list(enemyGroups[self.groupID].targetLocation)
    else:
      self.targetLocation = list(playerShips[self.target].location)
    if Distance(self.location, self.targetLocation) > 2*Magnitude(self.velocity)/self.drag + 50:
      self.rotation = TurnTowards(self.rotation, self.location, self.targetLocation, self.turning)
      self.velocity = VectorAdd(VectorMultiply((1 - self.drag), self.velocity), VectorMultiply(timeMultiplier * self.thrust, OrientationVector(self.rotation)))
      self.location = VectorAdd(self.location, VectorMultiply(timeMultiplier, self.velocity))
    else:
      self.rotation = TurnTowards(self.rotation, self.location, self.targetLocation, self.turning)
      self.velocity = VectorMultiply(1-self.drag, self.velocity)
      self.location = VectorAdd(self.location, VectorMultiply(timeMultiplier, self.velocity))
    #TODO put some firing here.
    floats = c_float * 3
    myvar = floats(self.location[:])
    ChangeValue( server_handle, CreateCent( b"/e/ene/"+self.name+"/loc", 0x80, 1, 12, myvar ), 1 );
  def damage(self, damage, sourceType, source, location, frequency):
    angle = Angle(OrientationVector(OrientationQuaternion(self.location, location)), OrientationVector(self.rotation))
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
      
def initStations(a):
  global stations
  for i in range(a):
    s = Station()
    s.init(i)
    stations.append(s)

def initWeapons():
  global tubeAmmos
  f = open('weapons.txt')
  weaponLines = f.readlines()
  for i in range(len(weaponLines)):
    if weaponLines[i][0] != '#':
      s = TubeAmmo()
      s.init(weaponLines[i])
      tubeAmmos.append(s)

def initEnemyGroups(a):
  global enemyGroups
  for i in range(a):
    s = enemyGroup()
    s.init(i)
    enemyGroups.append(s)

def init():
  initWeapons()
  initStations(4)
  spawnGroups(5)
  initPlayers()

initStations(4)
initWeapons()
initEnemyGroups(2)


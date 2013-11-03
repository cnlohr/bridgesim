import math

DEBUG = True

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
  if DEBUG:
    print("Dot was given vectors of diffrent lengths. a:", a, "b:", b, "Returning 0.")
    return 0

def Cross(a,b): #Cross returns the cross product of 2 vectors of length 3, or a zero vector if the vectors are not both length 3.
  if len(a) == 3 & len(b) == 3:
    c = [a[1]*b[2] - a[2]*b[1], a[2]*b[0] - a[0]*b[2], a[0]*b[1] - a[1]*b[0]]
    return c
  if DEBUG:
    print("Cross was given a vector whose length is not 3. a:", a, "b:", b, "Returning a zero vector.")
    return [0,0,0]

def Normalize(a): #Normalize returns a normalized vector, unless it is given a zero vector, in which case it returns the zero vector, and complains.
  s = 0
  c = [0] * len(a)
  for i in range(len(a)):
    s = s + a[i]**2
  s = math.sqrt(s)
  if s == 0:
    if DEBUG:
      print("Normalize was given a zero vector. This is not necessarily an error; returning zero vector.")
      return c
    return
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
  if DEBUG:
    print("Distance was given vectors whose lengths are not both 3. a:", a, "b:", b, "Returning 0.")
    return 0

def Angle(a,b):
  cos=Dot(Normalize(a),Normalize(b))
  if cos > 1:
    cos = 1
  if cos < -1:
    cos = -1
  return math.acos(cos)

def AngleVectorToQuaternion(angle, vector):
  normvector = Normalize(list(vector))
  angle = angle/2
  quaternion = [math.cos(angle), math.sin(angle)*normvector[0], math.sin(angle)*normvector[1], math.sin(angle)*normvector[2]]
  return Normalize(quaternion)

def OrientationQuaternion(location, target, referenceOrientation):
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
  if DEBUG:
    print("QuaternionMultiply was given lists of the wrong length. Returning identity quaternion.", a, b)
    return [1,0,0,0]

def RotateVectorByQuaternion(vectorpoint, quaternionpoint):
  vector = list(vectorpoint)
  quaternion = Normalize(list(quaternionpoint))
  inversequaternion = [quaternion[0], -quaternion[1], -quaternion[2], -quaternion[3]]
  result = QuaternionMultiply(QuaternionMultiply(quaternion, vector), inversequaternion)
  vectorresult = [result[1], result[2], result[3]]
  if math.fabs(result[0]) > 10 ** (-15):
    if DEBUG:
      print("RotateVectorByQuaternion gave a non-zero real result for", vector, quaternion)
  return vectorresult

def RotateQuaternionByQuaternion(apoint, bpoint):
  a = Normalize(list(apoint))
  b = Normalize(list(bpoint))
  inverseb = [b[0], -b[1], -b[2], -b[3]]
  result = QuaternionMultiply(QuaternionMultiply(b, a), inverseb)
  return result

def TurnTowards(rotationpoint, locationpoint, targetLocationpoint, turning, referenceOrientation, timeMultiplier):
  facing = OrientationVector(list(rotationpoint), referenceOrientation)
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

def OrientationVector(quaternionpoint, referenceOrientation):
  quaternion = list(quaternionpoint)
  reference = Normalize(referenceOrientation)
  return RotateVectorByQuaternion(reference, quaternion)

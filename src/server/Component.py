from physics import Vector

class Component:
    def __init__(self, ship, config):
        self.ship = ship

        self.model = "ball"
        self.hp = 1
        self.mass = 1000
        self.radius = 1
        self.position = Vector()
        self.orientation = Vector(1, 0, 0)
        self.energy = 0.0
        self.idle = True

        self.__dict__.update(config)
        self.orientation = Vector(self.orientation)
        self.position = Vector(self.position)
        print(self.hp)

    def energyNeeded(self):
        if self.hp > 0:
            return .1
        else:
            return 0

    def takeDamage(self, amount):
        applied = min(self.hp, amount)
        self.hp -= applied
        return amount - applied

    def isDead(self):
        return self.hp == 0

    def tick(self, duration):
        return {}

class HullSection(Component):
    def __init__(self, ship, config):
        super().__init__(ship, config)

    def tick(self, duration):
        return super().tick(duration)

class CrewStation(Component):
    def __init__(self, ship, config):
        super().__init__(ship, config)

    def tick(self, duration):
        return super().tick(duration)

class Drive(Component):
    def __init__(self, ship, config):
        self.throttle = 0.0
        self.thrustVector = Vector()
        super().__init__(ship, config)

    def energyNeeded(self):
        if self.hp > 0:
            return self.throttle
        else:
            return 0

    def tick(self, duration):
        self.thrustVector = self.orientation * self.energy * self.throttle * duration
        return super().tick(duration)

class WeaponsStation(Component):
    def __init__(self, ship, config):
        super().__init__(ship, config)

        self.target = None
        self.payload = None
        self.loadTime = 0
        self.loadStatus = "Empty"

    def load(self, payload):
        print("Loading")
        if self.weapons == "tube":
            if self.loadStatus == "Empty":
                self.loadStatus = "Loading"
                self.loadTime = payload.loadTime
                self.payload = payload

    def unload(self, payload):
        if self.weapons == "tube":
            if self.loadStatus == "Loading":
                self.loadStatus = "Unloading"

    def fire(self):
        print("Firing...")
        if self.weapons == "tube":
            print("check 1", self.loadStatus, self.hp, self.energy)
            if self.loadStatus == "Loaded" and self.hp > 0 and self.energy > .1:
                print("check 2")
                self.payload.fire(self)
                self.loadStatus = "Empty"
                self.payload = None
        else:
          print("Damn...")
          pass
            # Fire the phasers here

    def energyNeeded(self):
        if self.weapons == "phaser" or self.loadStatus == "Loading" or self.loadStatus == "Unloading":
            return 1
        else:
            return .1

    def tick(self, duration):
        print("Ticking tube", duration)
        if self.loadStatus == "Loading":
            self.loadTime -= duration * self.energy
            if self.loadTime <= 0:
                self.loadStatus = "Loaded"

        if self.loadStatus == "Unloading":
            self.loadTime += duration * self.energy
            if self.loadTime >= self.payload.loadTime:
                self.loadStatus = "Empty"
                self.payload = None

class ShieldGenerator(Component):
    def __init__(self, ship, config):
        super().__init__(ship, config)

        self.baseRadius = self.radius
        self.enabled = False

    def takeDamage(self, amount):
        if self.enabled:
            applied = min(amount, self.shieldHp)
            self.shieldHp -= applied
            amount -= applied

        if self.shieldHp <= 0 or not self.enabled:
            applied = min(amount, self.hp)
            self.hp -= applied
            amount -= applied

        return amount

    def enable(self):
        self.radius = self.shieldRadius
        self.enabled = True

    def disable(self):
        self.radius = self.baseRadius
        self.enabled = False

    def energyNeeded(self):
        if self.enabled:
            return 1
        else:
            return .2

    def tick(self, duration):
        if self.hp > 0:
            self.shieldHp += self.shieldRecharge * duration * self.energy

COMPONENT_CLASSES = {
    "Component": Component,
    "HullSection": HullSection,
    "CrewStation": CrewStation,
    "Drive": Drive,
    "WeaponsStation": WeaponsStation,
    "ShieldGenerator": ShieldGenerator
}
def findComponent(name):
    if name in COMPONENT_CLASSES:
        return COMPONENT_CLASSES[name]
    else:
        return None

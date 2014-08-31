from physics import Vector

class Component:
    def __init__(self, ship, config):
        self.ship = ship

        self.model = "ball"
        self.hp = 1
        self.mass = 1000
        self.position = Vector()
        self.orientation = Vector(1, 0, 0)
        self.energy = 0.0
        self.idle = True

        self.__dict__.update(config)

    def energyNeeded(self):
        if self.hp > 0:
            return .1
        else:
            return 0

    def tick(self, duration):
        return {}

class HullSection(Component):
    def __init__(self, ship, config):
        super.__init__(self, ship, config)

    def tick(self, duration):
        return super.tick(duration)

class CrewStation(Component):
    def __init__(self, ship, config):
        super.__init__(self, ship, config)

    def tick(self, duration):
        return super.tick(duration)

class Drive(Component):
    def __init__(self, ship, config):
        self.throttle = 0.0
        self.thrustVector = Vector()
        super.__init__(self, ship, config)

    def energyNeeded(self):
        if self.hp > 0:
            return self.throttle
        else:
            return 0

    def tick(self, duration):
        self.thrustVector = self.orientation * self.energy * self.thrust * duration
        return super.tick(duration)

class WeaponsStation(Component):
    def __init__(self, ship, config):
        super.__init__(self, ship, config)

        self.target = None
        self.payload = None
        self.loadTime = 0
        self.loadStatus = "Empty"

    def load(self, payload):
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
        if self.weapons == "tube":
            if self.loadStatus == "Loaded" and self.hp > 0 and self.energy > .1:
                self.payload.fire(self)
                self.loadStatus = "Empty"
                self.payload = None
        else:
            # Fire the phasers here

    def energyNeeded(self):
        if self.weapons == "phaser" or self.loadStatus == "Loading" or self.loadStatus == "Unloading":
            return 1
        else:
            return .1

    def tick(self, duration):
        if self.loadStatus == "Loading":
            self.loadTime -= duration * self.energy
            if self.loadTime <= 0:
                self.loadStatus = "Loaded"

        if self.loadStatus == "Unloading":
            self.loadTime += duration * self.energy
            if self.loadTime >= self.payload.loadTime:
                self.loadStatus = "Empty"
                self.payload = None

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

from physics import Vector

class Component:
    def __init__(self, ship, config):
        self.ship = ship

        self.model = "ball"
        self.hp = 1
        self.mass = 1000
        self.position = Vector()
        self.orientation = Vector(0, 0, 0)
        self.energy = 0.0
        self.idle = True

        self.__dict__.update(config)

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
        self.working = True
        self.thrustVector = Vector()
        super.__init__(self, ship, config)

    def tick(self, duration):
        consumption = duration * self.throttle * self.energy
        if self.ship.energy >= consumption:
            self.ship.energy -= consumption
            self.thrustVector = self.orientation * 
            
            self.working = True
            self.ship.energy -= min(self.ship.energy, duration * self.throttle * self.energy)
        else:
            self.working = False
        

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

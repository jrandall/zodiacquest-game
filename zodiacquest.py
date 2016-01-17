#!/usr/bin/env python3
from itertools import chain
from collections.abc import Mapping

class Inventory: 
    def __init__(self, people=[], wands=[], papers=[], runes=[], others=[]):
        self.people = people
        self.wands = wands
        self.papers = papers
        self.runes = runes
        self.others = others

    def things(self):
        return list(chain(self.people, 
                          self.wands, 
                          self.papers, 
                          self.runes, 
                          self.others))

    def empty_p(self):
        return len(self.things()) == 0

    def __str__(self):
        if self.empty_p():
            return "no items"
        else:
            return "[%s]" % (", ".join([str(thing) for thing in self.things()]))

class Region:
    def __init__(self, name, short_name, monument=None, **kwargs):
        self.name = name
        self.short_name = short_name
        self.portals = Portals(self)
        self.monument = monument
        self.inventory = Inventory(**kwargs)

    def add_portal(self, portal):
        self.portals.add_portal(portal, portal.destination(self))

    def names(self):
        return [self.name, self.short_name]

    def __str__(self):
        return "%s (%s)" % (self.name, self.short_name)

    def describe(self):
        descriptions = [str(self)]
        if len(self.portals) == 1:
            descriptions.append("with a portal to %s" % str(self.portals[0].destination(self)))
        elif len(self.portals) == 2:
            descriptions.append("with portals to %s and %s" % tuple([str(portal.destination(self)) for portal in self.portals]))
        elif len(self.portals) > 2:
            descriptions.append("with portals to %s" % (", ".join([str(portal.destination(self)) for portal in self.portals])))
        if self.monument:
            descriptions.append("here you see a monument to %s" % (str(self.monument)))
        if not self.inventory.empty_p():
            descriptions.append("and some things: %s" % (str(self.inventory)))
        return "; ".join(descriptions)


class Portal:
    def __init__(self, region_a, region_b, cost):
        self._region_a = region_a
        self._region_b = region_b
        self._cost = cost
        self._region_a.add_portal(self)
        self._region_b.add_portal(self)

    def __str__(self):
        return "Portal between %s and %s costing %s" % (str(self._region_a), str(self._region_b), self._cost)

    def destination(self, region):
        if region.name == self._region_a.name:
            return self._region_b
        elif region.name == self._region_b.name:
            return self._region_a
        else:
            print("ERROR: Portal destination requested for region %s not connected to portal: %s" % (region, self))

    def transit(self, You):
        print("Portal.transit(): TODO")
        return You

class Portals(Mapping):
    def __init__(self, from_region):
        self._from_region = from_region
        self._portals = []
        self._destination_region_lookup = dict()

    def add_portal(self, portal, destination_region):
        self._portals.append(portal)
        for region_name in destination_region.names():
            self._destination_region_lookup[region_name] = portal

    def __getitem__(self, key):
        return self._destination_region_lookup[key]

    def __iter__(self):
        for portal in self._portals:
            yield portal

    def __len__(self):
        return len(self._portals)

    def __str__(self):
        return "Portals to %s" % ([str(portal) for portal in self._portals])

class Person:
    def __init__(self, name, region, coins=0, **kwargs):
        self.name = name
        self.region = region
        self.inventory = Inventory(**kwargs)
        self.coins = coins

    def __str__(self):
        return self.name
    
    def describe(self):
        descriptions = ["%s" % (str(self))]
        if self.coins > 0:
            descriptions.append("with %s coins" % (self.coins))
        descriptions.append("at %s" % (self.region.describe()))
        if not self.inventory.empty_p():
            descriptions.append("carrying %s" % (str(self.inventory)))
        return ", ".join(descriptions)

class You(Person):
    def __init__(self, region, **kwargs):
        super(You, self).__init__("You", region, **kwargs)

class Regions(Mapping):
    def __init__(self):
        self._regions = []
        self._region_lookup = dict()

    def add_region(self, region):
        self._regions.append(region)
        self._region_lookup[region.name] = region
        self._region_lookup[region.short_name] = region

    def __getitem__(self, key):
        return self._region_lookup[key]

    def __iter__(self):
        for region in self._regions:
            yield region

    def __len__(self):
        return len(self._regions)


class World:
    def __init__(self):
        self.regions = Regions()
        self.regions.add_region(Region("YE OLD HOME TOWN", "A"))
        self.regions.add_region(Region("TRANSITION MEADOW", "B"))
        self.regions.add_region(Region("OPEN ZONE", "C"))
        self.regions.add_region(Region("TRANSITION GLEN", "D"))
        self.regions.add_region(Region("GARDENS OF IVES", "E"))
        self.regions.add_region(Region("MOUNTAIN HEIGHTS", "F"))
        self.regions.add_region(Region("MAMMOTH REEF COVE", "G"))
        self.regions.add_region(Region("NORTHINGTON EAST", "H"))
        self.regions.add_region(Region("PINELANDS OF OUR GODDESS", "I"))
        self.regions.add_region(Region("ABANDONED PLAINS", "J"))
        self.regions.add_region(Region("LEIGHTON PASS", "K"))
        self.regions.add_region(Region("FOURIER PLAZA AT AMALFI VERDI", "L"))
        self.regions.add_region(Region("STONESIDE VALLEY", "M"))
        self.regions.add_region(Region("MOTHER-OF-OUR-EARTH REEDSWAMP", "N"))
        self.regions.add_region(Region("GLADE OF SUNNINESS", "O"))
        self.regions.add_region(Region("REALM OF HONESTY", "P"))
        self.regions.add_region(Region("VELVET WOLD", "Q"))
        self.regions.add_region(Region("LOST WOODS OF BALFOUR", "R"))
        self.regions.add_region(Region("LONELY HILLS", "S"))
        self.regions.add_region(Region("WILDERNESS EVENT PAVILION", "T"))
        self.regions.add_region(Region("SOUTHINGTON EAST", "U"))

        # Page 1 Portals
        Portal(self.regions["YE OLD HOME TOWN"], self.regions["TRANSITION MEADOW"], 1)
        Portal(self.regions["YE OLD HOME TOWN"], self.regions["TRANSITION GLEN"], 1)
        Portal(self.regions["TRANSITION MEADOW"], self.regions["GARDENS OF IVES"], 1)
        Portal(self.regions["TRANSITION MEADOW"], self.regions["MOUNTAIN HEIGHTS"], 1)
        Portal(self.regions["TRANSITION MEADOW"], self.regions["OPEN ZONE"], 1)
        Portal(self.regions["TRANSITION GLEN"], self.regions["GARDENS OF IVES"], 1)
        Portal(self.regions["GARDENS OF IVES"], self.regions["MOUNTAIN HEIGHTS"], 1)
        Portal(self.regions["OPEN ZONE"], self.regions["MOUNTAIN HEIGHTS"], 2)
        Portal(self.regions["OPEN ZONE"], self.regions["MAMMOTH REEF COVE"], 3)
        Portal(self.regions["OPEN ZONE"], self.regions["PINELANDS OF OUR GODDESS"], 2)
        Portal(self.regions["MOUNTAIN HEIGHTS"], self.regions["PINELANDS OF OUR GODDESS"], 1)
        Portal(self.regions["MOUNTAIN HEIGHTS"], self.regions["ABANDONED PLAINS"], 1)
        Portal(self.regions["MOUNTAIN HEIGHTS"], self.regions["LOST WOODS OF BALFOUR"], 3)

        # Page 2 Portals
        Portal(self.regions["MAMMOTH REEF COVE"], self.regions["NORTHINGTON EAST"], 2)
        Portal(self.regions["MAMMOTH REEF COVE"], self.regions["PINELANDS OF OUR GODDESS"], 3)
        Portal(self.regions["PINELANDS OF OUR GODDESS"], self.regions["NORTHINGTON EAST"], 2)
        Portal(self.regions["PINELANDS OF OUR GODDESS"], self.regions["ABANDONED PLAINS"], 3)
        Portal(self.regions["PINELANDS OF OUR GODDESS"], self.regions["LEIGHTON PASS"], 2)
        Portal(self.regions["NORTHINGTON EAST"], self.regions["LEIGHTON PASS"], 3)
        Portal(self.regions["NORTHINGTON EAST"], self.regions["FOURIER PLAZA AT AMALFI VERDI"], 3)
        Portal(self.regions["ABANDONED PLAINS"], self.regions["LEIGHTON PASS"], 2)
        Portal(self.regions["LEIGHTON PASS"], self.regions["FOURIER PLAZA AT AMALFI VERDI"], 2)

        # Page 3 Portals
        Portal(self.regions["TRANSITION GLEN"], self.regions["STONESIDE VALLEY"], 1)
        Portal(self.regions["GARDENS OF IVES"], self.regions["MOTHER-OF-OUR-EARTH REEDSWAMP"], 2)
        Portal(self.regions["MOUNTAIN HEIGHTS"], self.regions["MOTHER-OF-OUR-EARTH REEDSWAMP"], 3)
        Portal(self.regions["MOUNTAIN HEIGHTS"], self.regions["REALM OF HONESTY"], 2)
        Portal(self.regions["MOUNTAIN HEIGHTS"], self.regions["VELVET WOLD"], 1)
        Portal(self.regions["MOUNTAIN HEIGHTS"], self.regions["GLADE OF SUNNINESS"], 1)
        Portal(self.regions["STONESIDE VALLEY"], self.regions["MOTHER-OF-OUR-EARTH REEDSWAMP"], 1)
        Portal(self.regions["STONESIDE VALLEY"], self.regions["REALM OF HONESTY"], 3)
        Portal(self.regions["MOTHER-OF-OUR-EARTH REEDSWAMP"], self.regions["REALM OF HONESTY"], 2)
        Portal(self.regions["REALM OF HONESTY"], self.regions["VELVET WOLD"], 1)
        Portal(self.regions["VELVET WOLD"], self.regions["GLADE OF SUNNINESS"], 1)

        # Page 4 Portals
        Portal(self.regions["ABANDONED PLAINS"], self.regions["LOST WOODS OF BALFOUR"], 1)
        Portal(self.regions["LEIGHTON PASS"], self.regions["LOST WOODS OF BALFOUR"], 2)
        Portal(self.regions["LEIGHTON PASS"], self.regions["LONELY HILLS"], 2)
        Portal(self.regions["FOURIER PLAZA AT AMALFI VERDI"], self.regions["LONELY HILLS"], 2)
        Portal(self.regions["FOURIER PLAZA AT AMALFI VERDI"], self.regions["SOUTHINGTON EAST"], 1)
        Portal(self.regions["GLADE OF SUNNINESS"], self.regions["LOST WOODS OF BALFOUR"], 2)
        Portal(self.regions["LOST WOODS OF BALFOUR"], self.regions["LONELY HILLS"], 3)
        Portal(self.regions["LOST WOODS OF BALFOUR"], self.regions["WILDERNESS EVENT PAVILION"], 2)
        Portal(self.regions["LONELY HILLS"], self.regions["WILDERNESS EVENT PAVILION"], 3)
        Portal(self.regions["LONELY HILLS"], self.regions["SOUTHINGTON EAST"], 2)
        Portal(self.regions["GLADE OF SUNNINESS"], self.regions["WILDERNESS EVENT PAVILION"], 3)
        Portal(self.regions["WILDERNESS EVENT PAVILION"], self.regions["SOUTHINGTON EAST"], 2)

        
def main():
    world = World()
    you = You(world.regions["A"], coins=15)

    print(you.describe())

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
from itertools import chain
from collections.abc import Mapping

ZODIACS = ["ARIES", "TAURUS", "GEMINI", 
          "CANCER", "LEO", "VIRGO", 
          "LIBRA", "SCORPIO", "SAGITTARIUS", 
          "CAPRICORN", "AQUARIUS", "PISCES"]

GEMS = ["GEM", 
        "DIAMOND", "EMERALD", "AGATE", 
        "RUBY", "PEARL", "SARDONYX", "ZIRCON", 
        "SAPPHIRE", "CITRINE", "LAPISLAZULI", 
        "GARNET", "AMETHYST", "BLOODSTONE", 
        "OPAL", 
        "MOONSTONE", "AGATE", 
        "JASPER", "ONYX",
        "JADE"]

GO_CMD="G"
QUIT_CMD="Q"

class Inventory: 
    def __init__(self, people=[], wands=[], papers=[], runes=[], other_things=[], strings=[]):
        self.people = people
        self.wands = wands
        self.papers = papers
        self.runes = runes
        self.other_things = other_things
        self.strings = strings
        self._thing_lookup = dict()
        for thing in self.things:
            self._thing_lookup[thing] = 1

    @property
    def things(self):
        return list(chain(self.people, 
                          self.wands, 
                          self.papers, 
                          self.runes, 
                          self.other_things))

    @property
    def empty_p(self):
        return len(self.things) + len(self.strings) == 0

    @property
    def have_gem_p(self):
        for gem in GEMS:
            if gem in self.things:
                return True
        return False

    @property
    def have_zodiac_p(self):
        for zodiac in ZODIACS:
            if zodiac in self.things:
                return True
        return False

    def have_thing_p(self, thing):
        return thing in self._thing_lookup

    def __str__(self):
        if self.empty_p:
            return "no things or strings"
        else:
            return "[%s]" % (", ".join(list(chain(
                            [str(thing) for thing in self.things],
                            ["'%s'" % string for string in self.strings],
                            ))))


class Region:
    def __init__(self, world, name, short_name, monument=None, **kwargs):
        self._world = world
        self.name = name
        self.short_name = short_name
        self.portals = RegionPortals(self)
        self.monument = monument
        self.inventory = Inventory(**kwargs)

    def add_portal(self, portal):
        self.portals.add_portal(portal, portal.destination(self))

    @property
    def names(self):
        return [self.name, self.short_name]

    def __str__(self):
        return "%s (%s)" % (self.name, self.short_name)

class Portal:
    def __init__(self, region_a, region_b, cost):
        self._region_a = region_a
        self._region_b = region_b
        self._cost = cost
        self._region_a.add_portal(self)
        self._region_b.add_portal(self)

    def __str__(self):
        return "Portal between %s and %s costing %s" % (str(self._region_a), str(self._region_b), self._cost)

    @property
    def listed_cost(self):
        return self._cost

    def cost(self, you):
        # cost for you (possibly depending on whether or not you have a gem)
        if self.listed_cost == 3:
            if you.have_gem_p:
                return 1
        return self.listed_cost

    def destination(self, region):
        if region.name == self._region_a.name:
            return self._region_b
        elif region.name == self._region_b.name:
            return self._region_a
        else:
            print("ERROR: Portal destination requested for region %s not connected to portal: %s" % (region, self))

    def transit(self, you):
        # move you to destination if you can afford it
        destination = self.destination(you.region)
        if you.coins >= self.cost(you):
            you.coins -= self.cost(you)
            you.region = destination
        else:
            print("Sorry, you cannot afford to go to %s" % destination)
            return False
        return True

class Portals(Mapping):
    def __init__(self):
        self._portals = []

    def add_portal(self, portal):
        self._portals.append(portal)

    def __getitem__(self, i):
        return self._portals[i]

    def __iter__(self):
        for portal in self._portals:
            yield portal

    def __len__(self):
        return len(self._portals)

class RegionPortals(Mapping):
    def __init__(self, from_region):
        self._from_region = from_region
        self._portals = []
        self._destination_region_lookup = dict()

    def add_portal(self, portal, destination_region):
        self._portals.append(portal)
        for region_name in destination_region.names:
            self._destination_region_lookup[region_name] = portal

    def __getitem__(self, key):
        return self._destination_region_lookup[key]

    def __iter__(self):
        for portal in self._portals:
            yield portal

    def __len__(self):
        return len(self._portals)

    def __str__(self):
        return "Portals from %s: %s" % (self._from_region, [str(portal) for portal in self._portals])

class Person:
    def __init__(self, name, region, coins=0, **kwargs):
        self.name = name
        self.region = region
        self.inventory = Inventory(**kwargs)
        self.coins = coins

    @property
    def have_gem_p(self):
        return self.inventory.have_gem_p or self.region.inventory.have_gem_p

    def __str__(self):
        return self.name

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
    def _construct_regions(self):
        self.regions = Regions()
        # Page 1 regions
        self.regions.add_region(Region(self, "YE OLD HOME TOWN", "A"))
        self.regions.add_region(Region(self, "TRANSITION MEADOW", "B"))
        self.regions.add_region(Region(self, "OPEN ZONE", "C"))
        self.regions.add_region(Region(self, "TRANSITION GLEN", "D"))
        self.regions.add_region(Region(self, "GARDENS OF IVES", "E"))
        self.regions.add_region(Region(self, "MOUNTAIN HEIGHTS", "F"))
        # Page 2 regions
        self.regions.add_region(Region(self, "MAMMOTH REEF COVE", "G"))
        self.regions.add_region(Region(self, "NORTHINGTON EAST", "H"))
        self.regions.add_region(Region(self, "PINELANDS OF OUR GODDESS", "I"))
        self.regions.add_region(Region(self, "ABANDONED PLAINS", "J"))
        self.regions.add_region(Region(self, "LEIGHTON PASS", "K"))
        self.regions.add_region(Region(self, "FOURIER PLAZA AT AMALFI VERDI", "L"))
        # Page 3 regions
        self.regions.add_region(Region(self, "STONESIDE VALLEY", "M"))
        self.regions.add_region(Region(self, "MOTHER-OF-OUR-EARTH REEDSWAMP", "N"))
        self.regions.add_region(Region(self, "GLADE OF SUNNINESS", "O"))
        self.regions.add_region(Region(self, "REALM OF HONESTY", "P"))
        self.regions.add_region(Region(self, "VELVET WOLD", "Q"))
        # Page 4 regions
        self.regions.add_region(Region(self, "LOST WOODS OF BALFOUR", "R"))
        self.regions.add_region(Region(self, "LONELY HILLS", "S"))
        self.regions.add_region(Region(self, "WILDERNESS EVENT PAVILION", "T"))
        self.regions.add_region(Region(self, "SOUTHINGTON EAST", "U"))

    def _construct_portals(self):
        self.portals = Portals()
        # Page 1 Portals
        self.portals.add_portal(Portal(self.regions["YE OLD HOME TOWN"], self.regions["TRANSITION MEADOW"], 1))
        self.portals.add_portal(Portal(self.regions["YE OLD HOME TOWN"], self.regions["TRANSITION GLEN"], 1))
        self.portals.add_portal(Portal(self.regions["TRANSITION MEADOW"], self.regions["GARDENS OF IVES"], 1))
        self.portals.add_portal(Portal(self.regions["TRANSITION MEADOW"], self.regions["MOUNTAIN HEIGHTS"], 1))
        self.portals.add_portal(Portal(self.regions["TRANSITION MEADOW"], self.regions["OPEN ZONE"], 1))
        self.portals.add_portal(Portal(self.regions["TRANSITION GLEN"], self.regions["GARDENS OF IVES"], 1))
        self.portals.add_portal(Portal(self.regions["GARDENS OF IVES"], self.regions["MOUNTAIN HEIGHTS"], 1))
        self.portals.add_portal(Portal(self.regions["OPEN ZONE"], self.regions["MOUNTAIN HEIGHTS"], 2))
        self.portals.add_portal(Portal(self.regions["OPEN ZONE"], self.regions["MAMMOTH REEF COVE"], 3))
        self.portals.add_portal(Portal(self.regions["OPEN ZONE"], self.regions["PINELANDS OF OUR GODDESS"], 2))
        self.portals.add_portal(Portal(self.regions["MOUNTAIN HEIGHTS"], self.regions["PINELANDS OF OUR GODDESS"], 1))
        self.portals.add_portal(Portal(self.regions["MOUNTAIN HEIGHTS"], self.regions["ABANDONED PLAINS"], 1))
        self.portals.add_portal(Portal(self.regions["MOUNTAIN HEIGHTS"], self.regions["LOST WOODS OF BALFOUR"], 3))
        # Page 2 Portals
        self.portals.add_portal(Portal(self.regions["MAMMOTH REEF COVE"], self.regions["NORTHINGTON EAST"], 2))
        self.portals.add_portal(Portal(self.regions["MAMMOTH REEF COVE"], self.regions["PINELANDS OF OUR GODDESS"], 3))
        self.portals.add_portal(Portal(self.regions["PINELANDS OF OUR GODDESS"], self.regions["NORTHINGTON EAST"], 2))
        self.portals.add_portal(Portal(self.regions["PINELANDS OF OUR GODDESS"], self.regions["ABANDONED PLAINS"], 3))
        self.portals.add_portal(Portal(self.regions["PINELANDS OF OUR GODDESS"], self.regions["LEIGHTON PASS"], 2))
        self.portals.add_portal(Portal(self.regions["NORTHINGTON EAST"], self.regions["LEIGHTON PASS"], 3))
        self.portals.add_portal(Portal(self.regions["NORTHINGTON EAST"], self.regions["FOURIER PLAZA AT AMALFI VERDI"], 3))
        self.portals.add_portal(Portal(self.regions["ABANDONED PLAINS"], self.regions["LEIGHTON PASS"], 2))
        self.portals.add_portal(Portal(self.regions["LEIGHTON PASS"], self.regions["FOURIER PLAZA AT AMALFI VERDI"], 2))
        # Page 3 Portals
        self.portals.add_portal(Portal(self.regions["TRANSITION GLEN"], self.regions["STONESIDE VALLEY"], 1))
        self.portals.add_portal(Portal(self.regions["GARDENS OF IVES"], self.regions["MOTHER-OF-OUR-EARTH REEDSWAMP"], 2))
        self.portals.add_portal(Portal(self.regions["MOUNTAIN HEIGHTS"], self.regions["MOTHER-OF-OUR-EARTH REEDSWAMP"], 3))
        self.portals.add_portal(Portal(self.regions["MOUNTAIN HEIGHTS"], self.regions["REALM OF HONESTY"], 2))
        self.portals.add_portal(Portal(self.regions["MOUNTAIN HEIGHTS"], self.regions["VELVET WOLD"], 1))
        self.portals.add_portal(Portal(self.regions["MOUNTAIN HEIGHTS"], self.regions["GLADE OF SUNNINESS"], 1))
        self.portals.add_portal(Portal(self.regions["STONESIDE VALLEY"], self.regions["MOTHER-OF-OUR-EARTH REEDSWAMP"], 1))
        self.portals.add_portal(Portal(self.regions["STONESIDE VALLEY"], self.regions["REALM OF HONESTY"], 3))
        self.portals.add_portal(Portal(self.regions["MOTHER-OF-OUR-EARTH REEDSWAMP"], self.regions["REALM OF HONESTY"], 2))
        self.portals.add_portal(Portal(self.regions["REALM OF HONESTY"], self.regions["VELVET WOLD"], 1))
        self.portals.add_portal(Portal(self.regions["VELVET WOLD"], self.regions["GLADE OF SUNNINESS"], 1))
        # Page 4 Portals
        self.portals.add_portal(Portal(self.regions["ABANDONED PLAINS"], self.regions["LOST WOODS OF BALFOUR"], 1))
        self.portals.add_portal(Portal(self.regions["LEIGHTON PASS"], self.regions["LOST WOODS OF BALFOUR"], 2))
        self.portals.add_portal(Portal(self.regions["LEIGHTON PASS"], self.regions["LONELY HILLS"], 2))
        self.portals.add_portal(Portal(self.regions["FOURIER PLAZA AT AMALFI VERDI"], self.regions["LONELY HILLS"], 2))
        self.portals.add_portal(Portal(self.regions["FOURIER PLAZA AT AMALFI VERDI"], self.regions["SOUTHINGTON EAST"], 1))
        self.portals.add_portal(Portal(self.regions["GLADE OF SUNNINESS"], self.regions["LOST WOODS OF BALFOUR"], 2))
        self.portals.add_portal(Portal(self.regions["LOST WOODS OF BALFOUR"], self.regions["LONELY HILLS"], 3))
        self.portals.add_portal(Portal(self.regions["LOST WOODS OF BALFOUR"], self.regions["WILDERNESS EVENT PAVILION"], 2))
        self.portals.add_portal(Portal(self.regions["LONELY HILLS"], self.regions["WILDERNESS EVENT PAVILION"], 3))
        self.portals.add_portal(Portal(self.regions["LONELY HILLS"], self.regions["SOUTHINGTON EAST"], 2))
        self.portals.add_portal(Portal(self.regions["GLADE OF SUNNINESS"], self.regions["WILDERNESS EVENT PAVILION"], 3))
        self.portals.add_portal(Portal(self.regions["WILDERNESS EVENT PAVILION"], self.regions["SOUTHINGTON EAST"], 2))

    def __init__(self, valid_things_dict="9C.txt"):
        self._valid_things = dict()
        with open(valid_things_dict, 'r') as f:
            for line in f.readlines():
                thing_string = line.rstrip().upper()
                self._valid_things[thing_string] = True
        self._construct_regions()
        self._construct_portals()

    def valid_thing_p(self, string):
        """ is the string a valid thing? """
        return (string in self._valid_things)

    @property
    def valid_things(self):
        return self._valid_things.keys()

    @property
    def description(self):
        return "World has %s regions, %s portals, and %s strings recognised as valid things" % (
            len(self.regions), 
            len(self.portals), 
            len(self.valid_things)
            )

class You(Person):
    def __init__(self, region, **kwargs):
        super(You, self).__init__("You", region, **kwargs)
        self.quit = False
        self._command_history = []

    @property
    def step(self):
        return len(self._command_history)

    @property
    def description(self):
        descriptions = ["%s" % (str(self))]
        if self.coins > 0:
            descriptions.append("with %s coins" % (self.coins))
        else:
            descriptions.append("devoid of coins!")
        descriptions.append("at %s" % (self.region))
        if not self.inventory.empty_p:
            descriptions.append("carrying %s" % (str(self.inventory)))
        if self.region.monument:
            descriptions.append("here you see a monument to %s" % (str(self.region.monument)))
        if not self.region.inventory.empty_p:
            descriptions.append("and some things: %s" % (str(self.region.inventory)))
        # describe portals and their current cost
        portal_descriptions = []
        for portal in self.region.portals:
            portal_description = str(portal.destination(self.region))
            portal_cost = portal.cost(self)
            listed_cost = portal.listed_cost
            if listed_cost != portal_cost:
                # portal is at a special rate
                portal_description += " at a special cost of %s (normally %s)" % (portal_cost, listed_cost)
            else:
                portal_description += " at a cost of %s" % (portal_cost)
            portal_descriptions.append(portal_description)
        descriptions.append("with portals to:\n%s" % ("\n".join(portal_descriptions)))
        return "; ".join(descriptions)

    def transit(self, portal_name):
        if portal_name in self.region.portals:
            return self.region.portals[portal_name].transit(self)
        else:
            print("ERROR: you cannot get to %s from here" % (portal_name))
            return False

    @property
    def commands(self):
        cmds = []
        # get valid go commands (accessible and affordable portals)
        for portal in self.region.portals:
            cmds.append("%s%s" % (GO_CMD, portal.destination(self.region).short_name))
        return cmds

    def command(self, cmd):
        if cmd.startswith(GO_CMD):
            # GO (transit portal)
            dest = cmd[1:].upper()
            if not self.transit(dest):
                print("ERROR: could not transit to %s" % (dest))
                return False
        elif cmd.startswith(QUIT_CMD):
            self.quit = True
            print("\n".join(self._command_history))
        else:
            print("ERROR: did not understand command %s" % cmd)
            return False
        self._command_history.append(cmd)
        return True

def main():
    # create the world
    world = World()

    # describe the world
    print(world.description)

    # enter the world
    you = You(world.regions["A"], coins=15)

    # describe the world as you see it and accept commands from stdin
    while not you.quit:
        print(you.description)
        print("Commands: %s" % you.commands)
        you.command(input("%s> " % you.step).upper())

if __name__ == "__main__":
    main()

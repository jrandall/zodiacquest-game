#!/usr/bin/env python3
from collections.abc import Mapping
from itertools import chain

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

# Command prefixes
GO_CMD="G"
LEAVE_CMD="L "
TAKE_CMD="T "
QUIT_CMD="Q"

class Thing:
    def __init__(self, names=[], strings=[], moveable=True):
        self._names = list(names)
        self._strings = list(strings)
        self._moveable = moveable

    @property
    def moveable(self):
        return self._moveable

    @property
    def names(self):
        return self._names

    @property
    def strings(self):
        return self._strings

class Wand(Thing):
    def __init__(self, names, magic):
        super().__init__(names)
        self._magic = magic

class Paper(Thing):
    def __init__(self, names, sheets=1, color="", runes="", strings=""):
        super().__init__(names)
        self._sheets = sheets
        self._color = color
        self._runes = runes
        self._strings = strings

class Inventory:
    def __init__(self):
        self._things = []
        self._names_to_things = dict()
        self._strings_to_things = dict()

    def add(self, thing):
        self._things.append(thing)
        for name in thing.names:
            if name in self._names_to_things:
                self._names_to_things[name].append(thing)
            else:
                self._names_to_things[name] = [thing]
        for name in thing.strings:
            if name in self._strings_to_things:
                self._strings_to_things[name].append(thing)
            else:
                self._strings_to_things[name] = [thing]

    def get(self, name):
        if name in self._names_to_things:
            return self._names_to_things[name]
        else:
            return None
    
    def remove(self, thing):
        if thing.moveable:
            for name in thing.names:
                if name in self._names_to_things:
                    self._names_to_things[name] = [t for t in self._names_to_things[name] if t != thing]
                else:
                    raise Exception("ERROR: expected name %s in names_to_things")
            for string in thing.strings:
                if string in self._strings_to_things:
                    self._strings_to_things[string] = [s for s in self._strings_to_things[string] if s != thing]
                else:
                    raise Exception("ERROR: expected string %s in strings_to_things")
            try:
                self._things.remove(thing)
                return thing
            except Exception as e:
                raise Exception("ERROR: could not remove thing %s from inventory" % thing)
        else:
            print("Sorry, %s is not moveable" % (thing))
            return False

    @property
    def things(self):
        return self._things

    @property
    def thing_names(self):
        return list(chain.from_iterable([thing.names for thing in self._things]))
    
    @property
    def string_names(self):
        return list(chain.from_iterable([thing.strings for thing in self._things]))

    @property
    def all_names(self):
        return list(chain.from_iterable([self.thing_names, self.string_names]))

    @property
    def empty_p(self):
        return (len(self.all_names) == 0)

    @property
    def have_gem_p(self):
        all_names = self.all_names
        for gem in GEMS:
            if gem in all_names:
                return True
        return False

    @property
    def have_zodiac_p(self):
        all_names = self.all_names
        for zodiac in ZODIACS:
            if zodiac in all_names:
                return True
        return False

    def have_thing_p(self, thing):
        return thing in self._thing_lookup

    def __str__(self):
        if self.empty_p:
            return "no things or strings"
        else:
            return "\n".join(self.all_names)

class Region:
    def __init__(self, world, name, id, monument=None, **kwargs):
        self._world = world
        self._name = name
        self.id = id
        self.portals = RegionPortals(self)
        self.monument = monument
        self.inventory = Inventory(**kwargs)

    def add_portal(self, portal):
        self.portals.add_portal(portal, portal.destination(self))

    @property
    def name(self):
        return self._name

    @property
    def name_and_id(self):
        return [self.name, self.id]

    def __str__(self):
        return "%s (%s)" % (self.name, self.id)

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
        if region.id == self._region_a.id:
            return self._region_b
        elif region.id == self._region_b.id:
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
        for region_name in destination_region.name_and_id:
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

class Person(Thing):
    def __init__(self, names, moveable=False, **kwargs):
        super().__init__(names=names)
        self._moveable = moveable
#        self.magic = Magic(**kwargs)

    @property
    def id(self):
        return self._names[0]

    def __str__(self):
        return str(self.id)

class Regions(Mapping):
    def __init__(self):
        self._regions = []
        self._region_lookup = dict()

    def add_region(self, region):
        self._regions.append(region)
        self._region_lookup[region.name] = region
        self._region_lookup[region.id] = region

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

    def phrontiersman_magic(you, from_thing_name, to_thing_name):
        # I use Magic to phonetically change whatever you’d like into
        # a Thing by adding or changing a single sound at the
        # front. For example, I can transform an OCEAN into a POTION
        # or a BOSS into a SAUCE. (I never just add or change a single
        # letter while leaving the rest of the letters intact – that
        # would be a bit boring.)
        if you.region.inventory.get(from_thing_name):
            print("TODO: implement")
#            if from_thing_name == "ANSWER" and to_thing_name == "CANCER":
#                
                

    def _construct_things(self):
        r = self.regions["OPEN ZONE"]
        r.inventory.add(Person(["PHRONTIERSMAN", "FIGURE"], magic=World.phrontiersman_magic))

    def __init__(self, valid_things_dict="9C.txt"):
        self._valid_things = dict()
        with open(valid_things_dict, 'r') as f:
            for line in f.readlines():
                thing_string = line.rstrip().upper()
                self._valid_things[thing_string] = True
        self._construct_regions()
        self._construct_portals()
        self._construct_things()

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

class You:
    def __init__(self, region, coins=0, **kwargs):
        self.region = region
        self.coins = coins
        self._inventory = Inventory(**kwargs)
        self._command_history = []
        self.quit = False

    def __str__(self):
        return "You"
        
    @property
    def inventory(self):
        return self._inventory

    @property
    def step(self):
        return len(self._command_history)

    @property
    def have_gem_p(self):
        return self.inventory.have_gem_p or self.region.inventory.have_gem_p

    @property
    def description(self):
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
        descriptions = ["%s" % (str(self))]
        if self.coins > 0:
            descriptions.append(", with %s coins" % (self.coins))
        else:
            descriptions.append(", devoid of coins!")
        descriptions.append(" in the region of %s" % (self.region))
        descriptions.append(" with portals to:\n%s" % ("\n".join(portal_descriptions)))
        if not self.inventory.empty_p:
            descriptions.append("\nCarrying: %s" % (str(self.inventory)))
        if self.region.monument:
            descriptions.append("\nThere is a monument to %s here!!!" % (str(self.region.monument)))
        if not self.region.inventory.empty_p:
            descriptions.append("\nYou see some 'things': %s" % (str(self.region.inventory)))
        return "".join(descriptions)

    def go(self, portal_id):
        if portal_id in self.region.portals:
            return self.region.portals[portal_id].transit(self)
        else:
            print("ERROR: you cannot get to %s from here" % (portal_id))
            return False

    def take(self, id):
        things = self.region.inventory.get(id)
        if len(things) > 1:
            print("ERROR: attempted to take more than one thing: %s" % id)
            return False
        elif len(things) < 1:
            print("ERROR: no thing to take: %s" % id)
            return False
        else:
            thing = self.region.inventory.remove(things[0])
            if thing:
                self.inventory.add(thing)
        return thing

    def leave(self, id):
        things = self.inventory.get(id)
        if len(things) > 1:
            print("ERROR: attempted to leave more than one thing: %s" % id)
            return False
        elif len(things) < 1:
            print("ERROR: no thing to leave: %s" % id)
            return False
        else:
            self.region.inventory.add(self.inventory.remove(things[0]))
        return things[0]

    @property
    def commands(self):
        cmds = []
        # valid go commands (accessible and affordable portals)
        for portal in self.region.portals:
            cmds.append("%s%s" % (GO_CMD, portal.destination(self.region).id))
        # valid drop commands (all things in my inventory)
        for thing in self.inventory.things:
            cmds.append("%s%s" % (LEAVE_CMD, thing.id))
        # valid take commands (all things in region inventory that are moveable)
        for thing in self.region.inventory.things:
            if thing.moveable:
                cmds.append("%s%s" % (TAKE_CMD, thing.id))
        return cmds

    def command(self, cmd):
        if cmd.startswith(GO_CMD):
            # GO (transit portal)
            dest = cmd[len(GO_CMD):].upper()
            if not self.go(dest):
                print("ERROR: could not go to %s" % (dest))
                return False
        elif cmd.startswith(TAKE_CMD):
            name = cmd[len(TAKE_CMD):].upper()
            if not self.take(name):
                print("ERROR: could not take %s" % (name))
                return False
        elif cmd.startswith(LEAVE_CMD):
            name = cmd[len(LEAVE_CMD):].upper()
            if not self.leave(name):
                print("ERROR: could not leave %s" % (name))
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

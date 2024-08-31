"""
Stores the ARGB colors that are used in BasePNGLoader.as
"""

class KAGMapItem:
    """
    Used to store the name, color, rotation and team of an item in the KAG map.
    """
    def __init__(self, name: str, color: tuple, rotation: int = 0, team: int = 0):
        self.name = name
        self.color = color
        self.rotation = rotation
        self.team = team

class KagColor:
    """
	Stores the ARGB colors that are used in BasePNGLoader.as
    """
    def __init__(self):
        self.vanilla_colors = [
            # TODO: these should be CBlob or CTile classes instead of just a dictionary
            # TODO: organize these into sections
            # TODO: figure out how to use the getTeamFromChannel & getAngleFromChannel,
            # TODO: and in BasePNGLoader.as for team / rotation
			KAGMapItem("sky",                   (255, 165, 189, 200)),
			KAGMapItem("tile_ground",           (255, 132, 71, 21)),
			KAGMapItem("tile_ground_back",      (255, 59, 20, 6)),
			KAGMapItem("tile_stone",            (255, 139, 104, 73)),
			KAGMapItem("tile_thickstone",       (255, 66, 72, 75)),
			KAGMapItem("tile_bedrock",          (255, 45, 52, 45)),
			KAGMapItem("tile_gold",             (255, 254, 165, 61)),
			KAGMapItem("tile_castle",           (255, 100, 113, 96)),
			KAGMapItem("tile_castle_back",      (255, 49, 52, 18)),
			KAGMapItem("tile_castle_moss",      (255, 100, 143, 96)),
			KAGMapItem("tile_castle_back_moss", (255, 49, 82, 18)),
			KAGMapItem("tile_grass",            (255, 100, 155, 13)),
			KAGMapItem("tile_wood",             (255, 196, 135, 21)),
			KAGMapItem("tile_wood_back",        (255, 85,42, 17)),
			KAGMapItem("water_air",             (255, 46, 129, 166)),
			KAGMapItem("water_backdirt",        (255, 51, 85, 102)), # TODO, needs implementation
			KAGMapItem("princess",              (255, 251, 135, 255)),
			KAGMapItem("necromancer",           (255, 158, 58, 187)),
			KAGMapItem("necromancer_teleport",  (255, 98, 26, 131)), # TODO, needs implementation
			KAGMapItem("redbarrier",            (255, 228, 55, 113)),
			KAGMapItem("tent",                  (255, 0, 255, 255)), # TODO, needs implementation with saving, called 'blue main spawn' in code -----
			KAGMapItem("tent",                  (255, 255, 0, 0), team = 1),
			KAGMapItem("tent",                  (255, 157, 202, 34), team = 2),
			KAGMapItem("tent",                  (255, 211, 121, 224), team = 3),
			KAGMapItem("tent",                  (255, 205, 97, 32), team = 4),
			KAGMapItem("tent",                  (255, 46, 229, 162), team = 5),
			KAGMapItem("tent",                  (255, 95, 132, 236), team = 6),
			KAGMapItem("tent",                  (255, 196, 207, 161), team = 7),
			KAGMapItem("ctf_flag",              (255, 0, 200, 200)), # called 'blue spawn' in kag code
			KAGMapItem("ctf_flag",              (255, 200, 0, 0), team = 1),
			KAGMapItem("ctf_flag",              (255, 158, 58, 204), team = 3),
			KAGMapItem("ctf_flag",              (255, 79, 155, 127), team = 5),
			KAGMapItem("ctf_flag",              (255, 65, 73, 240), team = 6),
			KAGMapItem("ctf_flag",              (255, 151, 167, 146), team = 7), # -----
			KAGMapItem("knight_shop",           (255, 255, 190, 190)),
			KAGMapItem("builder_shop",          (255, 190, 255, 190)),
			KAGMapItem("archer_shop",           (255, 255, 255, 190)),
			KAGMapItem("boat_shop",             (255, 200, 190, 255)),
			KAGMapItem("vehicle_shop",          (255, 230, 230, 230)),
			KAGMapItem("quarters",              (255, 240, 190, 255)),
			KAGMapItem("kitchen",               (255, 255, 217, 217)),
			KAGMapItem("nursery",               (255, 217, 255, 223)),
			KAGMapItem("research",              (255, 225, 225, 225)),
			KAGMapItem("workbench",             (255, 0, 255, 0)),
			KAGMapItem("campfire",              (255, 251, 226, 139)),
			KAGMapItem("saw",                   (255, 202, 164, 130)),
			KAGMapItem("tree",                  (255, 13, 103, 34)),
			KAGMapItem("bush",                  (255, 91, 126, 24)),
			KAGMapItem("grain",                 (255, 162, 183, 22)),
			KAGMapItem("flowers",               (255, 255, 102, 255)),
			KAGMapItem("log",                   (255, 160, 140, 40)),
			KAGMapItem("shark",                 (255, 44, 175, 222)),
			KAGMapItem("fish",                  (255, 121, 168, 163)),
			KAGMapItem("bison",                 (255, 183, 86, 70)),
			KAGMapItem("chicken",               (255, 141, 38, 20)),
			KAGMapItem("ladder",                (255, 43, 21, 9)),
			KAGMapItem("platform",              (255, 255, 146, 57)),
			KAGMapItem("platform",          (255, 255, 146, 56), rotation = 90),
			KAGMapItem("platform",         (255, 255, 146, 55), rotation = 180),
			KAGMapItem("platform",         (255, 255, 146, 54), rotation = 270),
			KAGMapItem("wooden_door",     (255, 26, 78, 131), rotation = 90),
			KAGMapItem("wooden_door",      (255, 26, 78, 130)),
			KAGMapItem("wooden_door",     (255, 148, 27, 27), rotation = 90, team = 1),
			KAGMapItem("wooden_door",      (255, 148, 27, 26), team = 1),
			KAGMapItem("wooden_door",    (255, 148, 148, 148), rotation = 90, team = -1),
			KAGMapItem("wooden_door",     (255, 148, 148, 147), team = -1),
			KAGMapItem("stone_door",      (255, 80, 90, 160), rotation = 90),
			KAGMapItem("stone_door",       (255, 80, 90, 159)),
			KAGMapItem("stone_door",      (255, 160, 90, 80), rotation = 90, team = 1),
			KAGMapItem("stone_door",       (255, 160, 90, 79), team = 1),
			KAGMapItem("stone_door",     (255, 160, 160, 160), team = -1, rotation = 90),
			KAGMapItem("stone_door",      (255, 160, 160, 159), team = -1),
			KAGMapItem("trapblock",           (255, 56, 76, 142)),
			KAGMapItem("trapblock",           (255, 142, 56, 68), team = 1),
			KAGMapItem("trapblock",          (255, 100, 100, 100), team = -1),
			KAGMapItem("bridge",              (255, 56, 76, 222)),
			KAGMapItem("bridge",              (255, 222, 56, 68), team = 1),
			KAGMapItem("bridge",             (255, 222, 222, 222), team = -1),
			KAGMapItem("spikes",                (255, 180, 42, 17)),
			KAGMapItem("spikes_ground",         (255, 180, 97, 17)), # TODO, needs implementation ---
			KAGMapItem("spikes_castle",         (255, 180, 42, 94)), # ! do we need these spikes variations?
			KAGMapItem("spikes_wood",           (255, 200, 42, 94)), # -----
			KAGMapItem("drill",                 (255, 210, 120, 0)),
			KAGMapItem("trampoline",            (255, 187, 59, 253)),
			KAGMapItem("lantern",               (255, 241, 231, 177)),
			KAGMapItem("crate",                 (255, 102, 0, 0)),
			KAGMapItem("bucket",                (255, 255, 220, 120)),
			KAGMapItem("sponge",                (255, 220, 0, 180)),
			KAGMapItem("chest",                 (255, 240, 193, 80)),
			KAGMapItem("fishy",                 (255, 121, 168, 163)),
			KAGMapItem("lever",                 (255, 0, 255, 255)), # apparently lever & the main blue spawn both use same color, so we can't actually use the lever
			KAGMapItem("pressure_plate",        (255, 16, 255, 255)),
			KAGMapItem("push_button",           (255, 32, 255, 255)),
			KAGMapItem("coin_slot",             (255, 48, 255, 255)),
			KAGMapItem("sensor",                (255, 64, 255, 255)),
			KAGMapItem("diode",                 (255, 255, 0, 255)),
			KAGMapItem("inverter",              (255, 255, 16, 255)),
			KAGMapItem("junction",              (255, 255, 32, 255)),
			KAGMapItem("magazine",              (255, 255, 48, 255)),
			KAGMapItem("oscillator",            (255, 255, 64, 255)),
			KAGMapItem("randomizer",            (255, 255, 80, 255)),
			KAGMapItem("resistor",              (255, 255, 96, 255)),
			KAGMapItem("toggle",                (255, 255, 112, 255)),
			KAGMapItem("transistor",            (255, 255, 128, 255)),
			KAGMapItem("wire",                  (255, 255, 144, 255)),
			KAGMapItem("emitter",               (255, 255, 160, 255)),
			KAGMapItem("receiver",              (255, 255, 176, 255)),
			KAGMapItem("elbow",                 (255, 255, 192, 255)),
			KAGMapItem("tee",                   (255, 255, 208, 255)),
			KAGMapItem("steak",                 (255, 219, 136, 103)),
			KAGMapItem("burger",                (255, 205, 142, 75)),
			KAGMapItem("heart",                 (255, 255, 40, 80)),
			KAGMapItem("catapult",              (255, 103, 229, 165)),
			KAGMapItem("ballista",              (255, 100, 210, 160)),
			KAGMapItem("mounted_bow",           (255, 56, 232, 184)),
			KAGMapItem("longboat",              (255, 0, 51, 255)),
			KAGMapItem("warboat",               (255, 50, 140, 255)),
			KAGMapItem("dinghy",                (255, 201, 158, 246)),
			KAGMapItem("raft",                  (255, 70, 110, 155)),
			KAGMapItem("airship",               (255, 255, 175, 0)),
			KAGMapItem("bomber",                (255, 255, 190, 0)),
			KAGMapItem("mat_bombs",             (255, 251, 241, 87)),
			KAGMapItem("mat_waterbombs",        (255, 210, 200, 120)),
			KAGMapItem("mat_arrows",            (255, 200, 210, 70)),
			KAGMapItem("mat_bombarrows",        (255, 200, 180, 10)),
			KAGMapItem("mat_waterarrows",       (255, 200, 160, 10)),
			KAGMapItem("mat_firearrows",        (255, 230, 210, 70)),
			KAGMapItem("mat_bolts",             (255, 230, 230, 170)),
			KAGMapItem("mine",                  (255, 90, 100, 255)),
			KAGMapItem("mine",                  (255, 255, 160, 90), team = 1),
			KAGMapItem("mine",                  (255, 215, 75, 255), team = -1),
			KAGMapItem("boulder",               (255, 161, 149, 133)),
			KAGMapItem("satchel",               (255, 170, 100, 0)),
			KAGMapItem("keg",                   (255, 220, 60, 60)),
			KAGMapItem("mat_gold",              (255, 255, 240, 160)),
			KAGMapItem("mat_stone",             (255, 190, 190, 175)),
			KAGMapItem("mat_wood",              (255, 200, 190, 140)),
			KAGMapItem("mook_knight",           (255, 255, 95, 25)),
			KAGMapItem("mook_archer",           (255, 25, 255, 182)),
			KAGMapItem("mook_spawner",          (255, 62, 1, 0)),
			KAGMapItem("mook_spawner_10",       (255, 86, 6, 44)),
			KAGMapItem("dummy",                 (255, 231, 140, 67)),
			KAGMapItem("lamp",                  (255, 255, 255,  32)),
			KAGMapItem("dispenser",             (255, 255, 255,  16)),
			KAGMapItem("spiker",                (255, 255, 255,  64)),
			KAGMapItem("tunnel",                (255, 220, 217, 254)),
			KAGMapItem("tunnel",                (255, 243, 217, 220), team = 1),
			KAGMapItem("tunnel",                (255, 243, 217, 254), team = -1),
			KAGMapItem("obstructor",            (255, 255, 255, 48)),
			KAGMapItem("bolter",                (255, 255, 255, 0)),
			KAGMapItem("factory",               (255, 255, 217, 237)),
			KAGMapItem("barracks",              (255, 217, 218, 255)),
			KAGMapItem("storage",               (255, 217, 255, 239))
        ]

    def get_color_by_name(self, name: str) -> tuple:
        """
        Retrieves a color by its name.

        Args:
            name (str): The name of the color to retrieve.

        Returns:
            tuple: The color of the item with the matching name, or None if no match is found.
        """

        for item in self.vanilla_colors:
            if item.name == name:
                return item.color

        return None

    def get_name_by_color(self, color: tuple) -> str:
        """
        Retrieves the name of an item by its color.

        Args:
            color (tuple): The color of the item to retrieve.

        Returns:
            str: The name of the item with the matching color, or None if no match is found.
        """
        for item in self.vanilla_colors:
            if item.color == color:
                return item.name

        return None

    def is_rotatable(self, name: str):
        """
        Checks if an item with the given name is rotatable.

        Args:
            name (str): The name of the item to check.

        Returns:
            bool: True if the item is rotatable, False otherwise.
        """
        for item in self.vanilla_colors:
            if item.name == name:
                if item.rotation != 0:
                    return True

        return False

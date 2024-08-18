from base.CBlobList import CBlobList

class KagColor:
	def __init__(self):
		self.BlobList = CBlobList()
		self.vanilla_colors = { # the _0 / _1 is for team, -1 = no team
								# r0 = up, r90 = right, r180 = down, r270 = left
								# if we have a red wooden door rotated left, it would be 'wooden_door_1_r270'
								# if a blob only has 1 available team in the list it won't have a _1 or _-1
								# TODO: these should be CBlob or CTile classes instead of just a dictionary
								# TODO: organize these into sections
								# TODO: figure out how to use the getTeamFromChannel & getAngleFromChannel in BasePNGLoader.as for team / rotation
			"sky": (255, 165, 189, 200),
			"tile_ground": (255, 132, 71, 21),
			"tile_ground_back": (255, 59, 20, 6),
			"tile_stone": (255, 139, 104, 73),
			"tile_thickstone": (255, 66, 72, 75),
			"tile_bedrock": (255, 45, 52, 45),
			"tile_gold": (255, 254, 165, 61),
			"tile_castle": (255, 100, 113, 96),
			"tile_castle_back": (255, 49, 52, 18),
			"tile_castle_moss": (255, 100, 143, 96),
			"tile_castle_back_moss": (255, 49, 82, 18),
			"tile_grass": (255, 100, 155, 13),
			"tile_wood": (255, 196, 135, 21),
			"tile_wood_back": (255, 85,42, 17),
			"water_air": (255, 46, 129, 166),
			"water_backdirt": (255, 51, 85, 102), # TODO: needs implementation
			"princess": (255, 251, 135, 255),
			"necromancer": (255, 158, 58, 187),
			"necromancer_teleport": (255, 98, 26, 131), # TODO: needs implementation
			"redbarrier": (255, 228, 55, 113),
			"tent_0": (255, 0, 255, 255), # TODO: needs implementation with saving, called 'blue main spawn' in code -----
			"tent_1": (255, 255, 0, 0),
			"tent_2": (255, 157, 202, 34),
			"tent_3": (255, 211, 121, 224),
			"tent_4": (255, 205, 97, 32),
			"tent_5": (255, 46, 229, 162),
			"tent_6": (255, 95, 132, 236),
			"tent_7": (255, 196, 207, 161),
			"ctf_flag_0": (255, 0, 200, 200), # called 'blue spawn' in kag code
			"ctf_flag_1": (255, 200, 0, 0),
			"ctf_flag_3": (255, 158, 58, 204),
			"ctf_flag_5": (255, 79, 155, 127),
			"ctf_flag_6": (255, 65, 73, 240),
			"ctf_flag_7": (255, 151, 167, 146), # -----
			"knight_shop": (255, 255, 190, 190),
			"builder_shop": (255, 190, 255, 190),
			"archer_shop": (255, 255, 255, 190),
			"boat_shop": (255, 200, 190, 255),
			"vehicle_shop": (255, 230, 230, 230),
			"quarters": (255, 240, 190, 255),
			"kitchen": (255, 255, 217, 217),
			"nursery": (255, 217, 255, 223),
			"research": (255, 225, 225, 225),
			"workbench": (255, 0, 255, 0),
			"campfire": (255, 251, 226, 139),
			"saw": (255, 202, 164, 130),
			"tree": (255, 13, 103, 34),
			"bush": (255, 91, 126, 24),
			"grain": (255, 162, 183, 22),
			"flowers": (255, 255, 102, 255),
			"log": (255, 160, 140, 40),
			"shark": (255, 44, 175, 222),
			"fish": (255, 121, 168, 163),
			"bison": (255, 183, 86, 70),
			"chicken": (255, 141, 38, 20),
			"ladder": (255, 43, 21, 9),
			"platform_r0": (255, 255, 146, 57), # TODO: needs implementation -----
			"platform_r90": (255, 255, 146, 56),
			"platform_r180": (255, 255, 146, 55),
			"platform_r270": (255, 255, 146, 54),
			"wooden_door_0_r90": (255, 26, 78, 131), # unclear for doors, may be wrong rotation
			"wooden_door_0_r0": (255, 26, 78, 130),
			"wooden_door_1_r90": (255, 148, 27, 27),
			"wooden_door_1_r0": (255, 148, 27, 26),
			"wooden_door_-1_r90": (255, 148, 148, 148),
			"wooden_door_-1_r0": (255, 148, 148, 147),
			"stone_door_0_r90": (255, 80, 90, 160),
			"stone_door_0_r0": (255, 80, 90, 159),
			"stone_door_1_r90": (255, 160, 90, 80),
			"stone_door_1_r0": (255, 160, 90, 79),
			"stone_door_-1_r90": (255, 160, 160, 160),
			"stone_door_-1_r0": (255, 160, 160, 159),
			"trapblock_0": (255, 56, 76, 142),
			"trapblock_1": (255, 142, 56, 68),
			"trapblock_-1": (255, 100, 100, 100),
			"bridge_0": (255, 56, 76, 222),
			"bridge_1": (255, 222, 56, 68),
			"bridge_-1": (255, 222, 222, 222), # -----
			"spikes": (255, 180, 42, 17),
			"spikes_ground": (255, 180, 97, 17), # TODO: needs implementation ---
			"spikes_castle": (255, 180, 42, 94), # ! do we need these spikes variations?
			"spikes_wood": (255, 200, 42, 94), # -----
			"drill": (255, 210, 120, 0),
			"trampoline": (255, 187, 59, 253),
			"lantern": (255, 241, 231, 177),
			"crate": (255, 102, 0, 0),
			"bucket": (255, 255, 220, 120),
			"sponge": (255, 220, 0, 180),
			"chest": (255, 240, 193, 80),
			"fishy": (255, 121, 168, 163),
			# "lever": (255, 0, 255, 255), # apparently lever & the main blue spawn both use same color, so we can't actually place the lever
			"pressure_plate": (255, 16, 255, 255),
			"push_button": (255, 32, 255, 255),
			"coin_slot": (255, 48, 255, 255),
			"sensor": (255, 64, 255, 255),
			"diode": (255, 255, 0, 255),
			"inverter": (255, 255, 16, 255),
			"junction": (255, 255, 32, 255),
			"magazine": (255, 255, 48, 255),
			"oscillator": (255, 255, 64, 255),
			"randomizer": (255, 255, 80, 255),
			"resistor": (255, 255, 96, 255),
			"toggle": (255, 255, 112, 255),
			"transistor": (255, 255, 128, 255),
			"wire": (255, 255, 144, 255),
			"emitter": (255, 255, 160, 255),
			"receiver": (255, 255, 176, 255),
			"elbow": (255, 255, 192, 255),
			"tee": (255, 255, 208, 255),
			"steak": (255, 219, 136, 103),
			"burger": (255, 205, 142, 75),
			"heart": (255, 255, 40, 80),
			"catapult": (255, 103, 229, 165),
			"ballista": (255, 100, 210, 160),
			"mounted_bow": (255, 56, 232, 184),
			"longboat": (255, 0, 51, 255),
			"warboat": (255, 50, 140, 255),
			"dinghy": (255, 201, 158, 246),
			"raft": (255, 70, 110, 155),
			"airship": (255, 255, 175, 0),
			"bomber": (255, 255, 190, 0),
			"mat_bombs": (255, 251, 241, 87),
			"mat_waterbombs": (255, 210, 200, 120),
			"mat_arrows": (255, 200, 210, 70),
			"mat_bombarrows": (255, 200, 180, 10),
			"mat_waterarrows": (255, 200, 160, 10),
			"mat_firearrows": (255, 230, 210, 70),
			"mat_bolts": (255, 230, 230, 170),
			"mine_0": (255, 90, 100, 255), # TODO: needs implementation ---
			"mine_1": (255, 255, 160, 90),
			"mine_-1": (255, 215, 75, 255), # -----
			"boulder": (255, 161, 149, 133),
			"satchel": (255, 170, 100, 0),
			"keg": (255, 220, 60, 60),
			"mat_gold": (255, 255, 240, 160),
			"mat_stone": (255, 190, 190, 175),
			"mat_wood": (255, 200, 190, 140),
			"mook_knight": (255, 255, 95, 25),
			"mook_archer": (255, 25, 255, 182),
			"mook_spawner": (255, 62, 1, 0),
			"mook_spawner_10": (255, 86, 6, 44),
			"dummy": (255, 231, 140, 67),
			"lamp": (255, 255, 255,  32),
			"dispenser": (255, 255, 255,  16),
			"spiker": (255, 255, 255,  64),
			"tunnel_0": (255, 220, 217, 254),
			"tunnel_1": (255, 243, 217, 220),
			"tunnel_-1": (255, 243, 217, 254),
			"obstructor": (255, 255, 255, 48),
			"bolter": (255, 255, 255, 0),
			"factory": (255, 255, 217, 237),
			"barracks": (255, 217, 218, 255),
			"storage": (255, 217, 255, 239),
		}

	# return ARGB color
	def getColor(self, name: str) -> tuple:
		return self.vanilla_colors[name]

	# return RGB color
	def getColorRGB(self, name: str) -> tuple:
		return self.tiles[name][1:]

	def getTileNames(self) -> list:
		return list(self.tiles.keys())

	def getTileColors(self) -> list:
		return list(self.tiles.values())
# Minecraft Village Procedural Generator main file
from mcpi.minecraft import Minecraft

import paths
import positioning
import houses

mc = Minecraft.create()
paths.debugging = False

village_centre = positioning.determine_village_location(8**2)
mc.player.setTilePos(village_centre[0], village_centre[1] + 50, village_centre[2])
village = houses.Village(village_centre)

village.generate_houses()
paths.generate_paths(village.houses, 3)

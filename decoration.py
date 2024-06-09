from mcpi import minecraft
from mcpi import block

mc = minecraft.Minecraft.create()

# A module containing a list of classes that construct interior and exterior decorations.

class Decoration:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

class Lamp(Decoration):
    def build(self, direction, coordinate):
        if coordinate == 'z':
            # Foundation
            mc.setBlocks(self.x, self.y - 5, self.z, self.x, self.y - 1, self.z, 1, 5)

            # Base
            mc.setBlocks(self.x, self.y, self.z, self.x, self.y, self.z, block.STONE_BRICK.id)

            # Pole
            mc.setBlocks(self.x, self.y + 1, self.z, self.x, self.y + 3, self.z, block.FENCE_SPRUCE.id)

            # Support 1
            mc.setBlock(self.x, self.y + 4, self.z, block.FENCE_SPRUCE.id)

            # Support 2
            mc.setBlock(self.x + direction, self.y + 4, self.z, block.FENCE_SPRUCE.id)
            
            # Temporary block to fix fence gap 
            mc.setBlock(self.x - direction, self.y + 4, self.z, block.STONE.id, 3)
            mc.setBlock(self.x - direction, self.y + 4, self.z, block.AIR.id)

            # Lantern
            mc.setBlock(self.x + direction, self.y + 3, self.z, block.GLOWSTONE_BLOCK.id)

        elif coordinate == 'x':
            # Foundation
            mc.setBlocks(self.x, self.y - 5, self.z, self.x, self.y - 1, self.z, 1, 5)
            
            # Base
            mc.setBlocks(self.x, self.y, self.z, self.x, self.y, self.z, block.STONE_BRICK.id)
    
            # Pole
            mc.setBlocks(self.x, self.y + 1, self.z, self.x, self.y + 3, self.z, block.FENCE_SPRUCE.id)

            # Support 1
            mc.setBlock(self.x, self.y + 4, self.z, block.FENCE_SPRUCE.id)

            # Support 2
            mc.setBlock(self.x, self.y + 4, self.z + direction, block.FENCE_SPRUCE.id, 3)

            # Temporary block to fix fence gap 
            mc.setBlock(self.x, self.y + 4, self.z - direction, block.STONE.id)
            mc.setBlock(self.x, self.y + 4, self.z - direction, block.AIR.id)

            # Lantern
            mc.setBlock(self.x, self.y + 3, self.z + direction, block.GLOWSTONE_BLOCK.id)


def bulldoze_central_path_area(x, y, z, height):
    # Path
    mc.setBlocks(x - 5, y + 1, z - 1, x + 5, y + height, z + 1, block.AIR.id)
    mc.setBlocks(x - 1, y + 1, z - 5, x + 1, y + height, z + 5, block.AIR.id)

    # Path corners
    mc.setBlocks(x - 2, y + 1, z - 2, x - 4, y + height, z - 3, block.AIR.id)
    mc.setBlocks(x - 2, y + 1, z - 4, x - 3, y + height, z - 4, block.AIR.id)

    mc.setBlocks(x - 2, y + 1, z + 2, x - 4, y + height, z + 3, block.AIR.id)
    mc.setBlocks(x - 2, y + 1, z + 4, x - 3, y + height, z + 4, block.AIR.id)

    mc.setBlocks(x + 2, y + 1, z + 2, x + 4, y + height, z + 3, block.AIR.id)
    mc.setBlocks(x + 2, y + 1, z + 4, x + 3, y + height, z + 4, block.AIR.id)

    mc.setBlocks(x + 2, y + 1, z - 2, x + 4, y + height, z - 3, block.AIR.id)
    mc.setBlocks(x + 2, y + 1, z - 4, x + 3, y + height, z - 4, block.AIR.id)


def build_central_path(x, y, z, height):
    bulldoze_central_path_area(x, y, z, height)
    # Path
    mc.setBlocks(x - 3, y, z - 1, x - 5, y, z + 1, block.GRAVEL.id)
    mc.setBlocks(x + 3, y, z - 1, x + 5, y, z + 1, block.GRAVEL.id)

    mc.setBlocks(x - 1, y, z - 3, x + 1, y, z - 5, block.GRAVEL.id)
    mc.setBlocks(x - 1, y, z + 3, x + 1, y, z + 5, block.GRAVEL.id)

    # Path corners
    mc.setBlocks(x - 2, y, z - 2, x - 4, y, z - 3, block.GRAVEL.id)
    mc.setBlocks(x - 2, y, z - 4, x - 3, y, z - 4, block.GRAVEL.id)

    mc.setBlocks(x - 2, y, z + 2, x - 4, y, z + 3, block.GRAVEL.id)
    mc.setBlocks(x - 2, y, z + 4, x - 3, y, z + 4, block.GRAVEL.id)

    mc.setBlocks(x + 2, y, z + 2, x + 4, y, z + 3, block.GRAVEL.id)
    mc.setBlocks(x + 2, y, z + 4, x + 3, y, z + 4, block.GRAVEL.id)

    mc.setBlocks(x + 2, y, z - 2, x + 4, y, z - 3, block.GRAVEL.id)
    mc.setBlocks(x + 2, y, z - 4, x + 3, y, z - 4, block.GRAVEL.id)

class Well(Decoration):
    def build(self):
        build_central_path(self.x, self.y, self.z, 5)

        # Base Walls
        mc.setBlocks(self.x - 2, self.y + 1, self.z - 1, self.x - 2, self.y - 1, self.z + 1, block.STONE_BRICK.id)
        mc.setBlocks(self.x + 2, self.y + 1, self.z - 1, self.x + 2, self.y - 1, self.z + 1, block.STONE_BRICK.id)

        mc.setBlocks(self.x - 1, self.y + 1, self.z - 2, self.x + 1, self.y - 1, self.z - 2, block.STONE_BRICK.id)
        mc.setBlocks(self.x - 1, self.y + 1, self.z + 2, self.x + 1, self.y - 1, self.z + 2, block.STONE_BRICK.id)

        # Bottom
        mc.setBlocks(self.x - 1, self.y - 2, self.z - 1, self.x + 1, self.y - 2, self.z + 1, block.STONE_BRICK.id)

        # Water
        mc.setBlocks(self.x - 1, self.y, self.z - 1, self.x + 1, self.y - 1, self.z + 1, block.WATER.id)

        # Roof support poles
        mc.setBlocks(self.x - 1, self.y + 2, self.z + 2, self.x - 1, self.y + 4, self.z + 2, block.FENCE.id)
        mc.setBlocks(self.x + 1, self.y + 2, self.z + 2, self.x + 1, self.y + 4, self.z + 2, block.FENCE.id)
        
        mc.setBlocks(self.x - 2, self.y + 2, self.z - 1, self.x - 2, self.y + 4, self.z - 1, block.FENCE.id)
        mc.setBlocks(self.x - 2, self.y + 2, self.z + 1, self.x - 2, self.y + 4, self.z + 1, block.FENCE.id)

        mc.setBlocks(self.x - 1, self.y + 2, self.z - 2, self.x - 1, self.y + 4, self.z - 2, block.FENCE.id)
        mc.setBlocks(self.x + 1, self.y + 2, self.z - 2, self.x + 1, self.y + 4, self.z - 2, block.FENCE.id)

        mc.setBlocks(self.x + 2, self.y + 2, self.z - 1, self.x + 2, self.y + 4, self.z - 1, block.FENCE.id)
        mc.setBlocks(self.x + 2, self.y + 2, self.z + 1, self.x + 2, self.y + 4, self.z + 1, block.FENCE.id)

        # Roof Stairs
        mc.setBlocks(self.x - 2, self.y + 5, self.z - 1, self.x - 2, self.y + 5, self.z + 1, 134)
        mc.setBlocks(self.x + 2, self.y + 5, self.z - 1, self.x + 2, self.y + 5, self.z + 1, 134, 1)

        mc.setBlocks(self.x - 1, self.y + 5, self.z - 2, self.x + 1, self.y + 5, self.z - 2, 134, 2)
        mc.setBlocks(self.x - 1, self.y + 5, self.z + 2, self.x + 1, self.y + 5, self.z + 2, 134, 3)

        # Roof Center
        mc.setBlocks(self.x - 1, self.y + 5, self.z - 1, self.x + 1, self.y + 5, self.z + 1, 5, 1)

class Fountain(Decoration):

    def build(self):
        # Path
        build_central_path(self.x, self.y, self.z, 5)

        # Base (3x3)
        mc.setBlocks(self.x - 1, self.y, self.z - 1, self.x + 1, self.y, self.z + 1, block.STONE_BRICK.id)

        # Pole
        mc.setBlocks(self.x, self.y + 1, self.z, self.x, self.y + 4, self.z, block.STONE_BRICK.id)

        # Walls
        mc.setBlocks(self.x - 2, self.y + 1, self.z - 1, self.x - 2, self.y + 1, self.z + 1, block.STAIRS_STONE_BRICK.id)
        mc.setBlocks(self.x + 2, self.y + 1, self.z - 1, self.x + 2, self.y + 1, self.z + 1, block.STAIRS_STONE_BRICK.id, 1)

        mc.setBlocks(self.x - 1, self.y + 1, self.z - 2, self.x + 1, self.y + 1, self.z - 2, block.STAIRS_STONE_BRICK.id, 2)
        mc.setBlocks(self.x - 1, self.y + 1, self.z + 2, self.x + 1, self.y + 1, self.z + 2, block.STAIRS_STONE_BRICK.id, 3)

        # Water
        mc.setBlocks(self.x, self.y + 5, self.z, self.x, self.y + 5, self.z, block.WATER.id)
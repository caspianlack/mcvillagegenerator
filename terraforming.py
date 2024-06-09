from cmath import log
import random
import time

from mcpi.minecraft import Minecraft

from positioning import find_ground_levels
from positioning import air_blocks
from positioning import ground_blocks

from trees import remove_tree
from trees import tree_blocks
from trees import log_blocks

mc = Minecraft.create()

random.seed(float(time.time()))

levels_dropped = False
generate_tall = False
terraformed_below = False
levels_to_drop = 0
default_terrain_pallet = 'grass'

terrain_layer_1 = {'grass' : (2, 0), 'sand' : (12, 0), 'red_sand' :  (12, 1), 'snow' : (80, 0), 'gravel' : (13, 0), 'corse_dirt' : (3, 1), 'terracotta':  (172, 0), 'podzol' : (3, 2), 'mycelium' : (110, 0)}
terrain_layer_2 = {'grass' : (3, 0), 'sand' : (12, 0), 'red_sand' : (172, 0), 'snow' :  (3, 0), 'gravel' : (13, 0), 'corse_dirt' : (3, 0), 'terracotta':  (159, 1), 'podzol' : (3, 0), 'mycelium' :   (3, 0)}
terrain_layer_3 = {'grass' : (1, 0), 'sand' : (24, 0), 'red_sand' :   (1, 0), 'snow' :  (1, 0), 'gravel' :  (1, 0), 'corse_dirt' : (1, 0), 'terracotta': (159, 12), 'podzol' : (1, 0), 'mycelium' :   (1, 0)}


def terraform(coords: 'tuple[int, int, int]', x_extends: int, z_extends: int) -> None:
    """
        Arguments:
            coords (tuple[int, int, int]): The minimum coordinates of the structure
            x_extends (int): How far the structure extends in the x direction
            z_extends (int): How far the structure extends in the z direction
            
        Returns:
            None
    """    

    #Adjusts lengths to consider pillars
    x_length = x_extends + 2
    z_length = z_extends + 2

    corner_coords = {'x': coords[0] - 1, 'y': coords[1], 'z': coords[2] - 1} #Adjusts coords to consider pillars
    centre_coords = {'x': coords[0] + (x_length - 1) / 2, 'z': coords[2] + (z_length - 1) / 2}

    #randomise base size
    x_increase = round(random.randint(0, 9) * 0.15)
    z_increase = round(random.randint(0, 9) * 0.15)

    x_length += x_increase
    z_length += z_increase

    #randomise centre
    centre_coords['x'] -= (x_increase + 0.5) + random.randint(-1, 1)
    centre_coords['z'] -= (z_increase + 0.5) + random.randint(-1, 1)

    lowest_point, highest_point = find_ground_levels(corner_coords['x'], corner_coords['x'] + x_length, corner_coords['z'], corner_coords['z'] + z_length)

    global levels_dropped
    global generate_tall
    generate_tall = False

    global default_terrain_pallet
    default_terrain_pallet = determine_terrain_pallet(centre_coords['x'], lowest_point, centre_coords['z'])

    #Remove blocks in house are and above house
    mc.setBlocks(corner_coords['x'], corner_coords['y'], corner_coords['z'], corner_coords['x'] + x_length, 255, corner_coords['z'] + z_length, 0)

    #If the house is above the min ground level, terraform under
    if lowest_point + 1 < corner_coords['y']: 
        terraform_below(x_length, z_length, lowest_point, corner_coords, centre_coords)

    #If the house is below the max ground level, terraform above
    if highest_point + 1 > corner_coords['y'] - 1:

        #Adjust to give house more room
        corner_coords['x'] -= 2
        corner_coords['z'] -= 2
        centre_coords['x'] -= 1
        centre_coords['z'] -= 1

        terraform_above(x_length + 2, z_length + 2, lowest_point, corner_coords, centre_coords)



def terraform_below(x_length: int, z_length: int, lowest_point: int, corner_coords: 'tuple[int, int, int]', centre_coords: 'tuple[int, int, int]') -> None:
    """
    Arguments:
        x_length (int): The area length in the x direction
        z_length (int): The area length in the z direction
        lowest_point (int): The lowest ground level in the area
        corner_coords (tuple[int, int, int]): Minimum coordinates of the area
        centre_coords (tuple[int, int, int]): Centre coordinates of the area
        
    Returns:
        None
    """ 

    global default_terrain_pallet

    #Fill volume under house
    mc.setBlocks(corner_coords['x'] - 1, corner_coords['y'] - 1, corner_coords['z'] - 1, corner_coords['x'] + x_length, lowest_point + 1, corner_coords['z'] + z_length, terrain_layer_1[default_terrain_pallet])
    if corner_coords['y'] - 2 - lowest_point > 0:
        mc.setBlocks(corner_coords['x'] - 1, corner_coords['y'] - 2, corner_coords['z'] - 1, corner_coords['x'] + x_length, lowest_point + 1, corner_coords['z'] + z_length, terrain_layer_2[default_terrain_pallet])
    if corner_coords['y'] - 5 - lowest_point > 0:
        mc.setBlocks(corner_coords['x'] - 1, corner_coords['y'] - 5, corner_coords['z'] - 1, corner_coords['x'] + x_length, lowest_point + 1, corner_coords['z'] + z_length, terrain_layer_3[default_terrain_pallet])

    global generate_tall
    generate_tall = False

    #Terraform below house
    level = 1
    terraform_down = True
    terraform_spiral(x_length, z_length, corner_coords, centre_coords, level, terraform_down)
    
    global terraformed_below
    terraformed_below = True

def terraform_above(x_length: int, z_length: int, lowest_point: int, corner_coords: 'tuple[int, int, int]', centre_coords: 'tuple[int, int, int]') -> None:
    """
    Arguments:z
        x_length (int): The area length in the x direction
        z_length (int): The area length in the z direction
        lowest_point (int): The lowest ground level in the area
        corner_coords (tuple[int, int, int]): Minimum coordinates of the area
        centre_coords (tuple[int, int, int]): Centre coordinates of the area
        
    Returns:
        None
    """ 

    global default_terrain_pallet

    #Ensure house is on appropriate block
    global terraformed_below
    if not terraformed_below:
        mc.setBlocks(corner_coords['x'] - 2, corner_coords['y'] - 1, corner_coords['z'] - 2, corner_coords['x'] + x_length + 4, corner_coords['y'] - 1, corner_coords['z'] + z_length + 4, terrain_layer_1[default_terrain_pallet])

    global generate_tall
    generate_tall = False
    mc.setBlocks(corner_coords['x'], corner_coords['y'], corner_coords['z'], corner_coords['x'] + x_length, 255, corner_coords['z'] + z_length, 0)

    #Terraform above house
    level = 0
    terraform_down = False
    terraform_spiral(x_length, z_length, corner_coords, centre_coords, level, terraform_down)
   

def terraform_spiral(x_length: int, z_length: int, corner_coords: 'tuple[int, int, int]', centre_coords: 'tuple[int, int, int]', level: int, terraform_down: bool) -> None:
    """
    Arguments:
        x_length (int): The area length in the x direction
        z_length (int): The area length in the z direction
        corner_coords (tuple[int, int, int]): Minimum coordinates of the area
        centre_coords (tuple[int, int, int]): Centre coordinates of the area
        level (int): Distance from the first terraforming of the area
        terraform_down (bool, optional): Whether terraforming occurs below or above the area. Defaults to True
        
    Returns:
        None
    """    

    global levels_dropped
    levels_dropped= False
    target_reached = False

    while not target_reached:  

            target_reached = True
            for i in range (corner_coords['x'] - 1 - level, corner_coords['x'] + x_length + level + 1):    #-Z
                if terraform_column(i, corner_coords['z'] - 1 - level, level, corner_coords, centre_coords, x_length, '-z', terraform_down) == False:
                    target_reached = False

            for i in range (corner_coords['z'] - level, corner_coords['z'] + z_length + level):           #-X
                if terraform_column(corner_coords['x'] - 1 - level, i, level, corner_coords, centre_coords, z_length, '-x', terraform_down) == False:
                    target_reached = False

            for i in range (corner_coords['x'] - 1 - level, corner_coords['x'] + x_length + level + 1):    #+Z
                if terraform_column(i, corner_coords['z'] + z_length + level, level, corner_coords, centre_coords, x_length, '+z', terraform_down) == False:
                    target_reached = False

            for i in range (corner_coords['z'] - level, corner_coords['z'] + z_length + level):           #+X
                if terraform_column(corner_coords['x'] + x_length + level, i, level, corner_coords, centre_coords, z_length, '+x', terraform_down) == False:
                    target_reached = False

            level += 1
            levels_dropped = False


#Terraforms a column of blocks
def terraform_column(x: int, z: int, level: int, corner_coords: 'tuple[int, int, int]', centre_coords: 'tuple[int, int, int]', length: int, face: str, terraform_down = True):
    """
    Arguments:
        x (int): The x coordinate of the column
        z (int): The z coordinate of the column
        level (int): Distance from the first terraforming of the area
        corner_coords (tuple[int, int, int]): Minimum coordinates of the area
        centre_coords (tuple[int, int, int]): Centre coordinates of the area
        length (int): The length of the current side of the area
        face (str): The direction of the current side of the area (+x, +z, -x, or -z)
        terraform_down (bool, optional): Whether terraforming occurs below or above the area. Defaults to True
        
    Returns:
        None
    """    

    MAX_WORLD_HEIGHT = 255
    MIN_WORLD_HEIGHT = 0

    if terraform_down == True:
        direction = -1
    else:
        direction = +1
    #direction constant decides whether to fill up or down
    
    level_block = mc.getBlock(x, corner_coords['y'] + level * direction + 1, z)

    if (terraform_down and (level_block not in ground_blocks or level_block in air_blocks)) or (not terraform_down and (level_block in ground_blocks or level_block not in air_blocks)):                     

        #determine appropriate height
        if 'z' in face:
            centre_offset = abs(x - centre_coords['x'])
        else:
            centre_offset = abs(z - centre_coords['z'])

        max_y = corner_coords['y'] + level * direction - 1
        max_y = max_y + ((1 / (((centre_offset * 3 + level * 2 + 0.5) / (length * 2)) / 2)) + (level / (length - 1)) - 1) * direction * -1

        #Tweak terraforming
        if terraform_down and max_y >= corner_coords['y'] or not terraform_down and max_y < corner_coords['y'] - 1: 
            max_y = corner_coords['y'] - 1
        if centre_offset == 0 and level > 4: 
            max_y = max_y + direction
        if face[1] == 'z' and centre_offset * 2 + 1 >= length:
            max_y = max_y + direction 

        down_blocks = []
        #Find ground level
        min_y = corner_coords['y']
        if terraform_down:
            down_blocks = list(reversed(list(mc.getBlocks(x, MIN_WORLD_HEIGHT, z, x, corner_coords['y'], z))))
            for ordinate in down_blocks:
                if ordinate in air_blocks:
                    min_y -= 1
                else:
                    break
            min_y += 1

        global generate_tall

        #If the appropriate ground hight is at the existing ground, end the function
        if terraform_down and max_y + 1 < min_y:
            return True

        #Adjust max_y based on relative elevation of terrain
        if generate_tall or (terraform_down and (int(max_y) + 1 - min_y > 3 and max_y < corner_coords['y'] - 2 and max_y > min_y + 1)) or (not terraform_down and max_y > corner_coords['y'] + 4):
            
            global levels_dropped
            global levels_to_drop

            max_y = max_y + direction

            if not levels_dropped:
                levels_to_drop += 1 
                levels_dropped = True     

            max_y = max_y + levels_to_drop * direction + 2
            generate_tall = True

            #If the appropriate ground hight is at the existing ground, end the function
            if max_y <= min_y:
                return True

        up_blocks = []
        #Clear column
        if not terraform_down:
            
            #Remove trees in range
            up_blocks = list(mc.getBlocks(x, MIN_WORLD_HEIGHT, z, x, MAX_WORLD_HEIGHT, z))
            for i in range (len(up_blocks)):
                if up_blocks[i] not in air_blocks:
                    terrain_max = MIN_WORLD_HEIGHT + i
                if up_blocks[i] in log_blocks or up_blocks[i] in tree_blocks:
                    remove_tree(x, min_y + i, z)
                    break   #It is unreasonable to expect any more than one tree in a column

            if not generate_tall:
                max_y += level
            
            if level > 2 and level < 3:
                max_y -= (level + 0.5)

            #If the appropriate ground hight is at the existing ground, end the function
            if max_y >= terrain_max + 1:
                return True

            mc.setBlocks(x, min_y, z, x, MAX_WORLD_HEIGHT, z, 0)


        global default_terrain_pallet
        terrain_pallet = default_terrain_pallet

        #Fill surface
        if max_y >= min_y:   
            if terraform_down:
                  
                #Remove trees
                for block in down_blocks:
                    if block in tree_blocks or block in log_blocks:
                        remove_tree(x, max_y, z)
                
                #Find terrain pallet to use
                terrain_pallet = determine_terrain_pallet(x, min_y - 1, z)

            mc.setBlocks(x, min_y, z, x, max_y, z, terrain_layer_1[terrain_pallet])
        
        elif terraform_down:
            return True
        
        #Fill area
        if max_y - 1 >= min_y:
            mc.setBlocks(x, min_y, z, x, max_y - 1, z, terrain_layer_2[terrain_pallet])

        #Randomise stone gen height   
        rand = random.randint(4, 9) / 3      
        if max_y - min_y > rand and max_y - rand - 1 >= min_y:
            mc.setBlocks(x, min_y, z, x, max_y - rand - 1, z, terrain_layer_3[terrain_pallet])

        #All filling goes down to min y to support gravity blocks (sand, gravel, etc)
        
        #Next level neighbor
        check_x = x
        check_z = z

        if face == '+x':
            check_x += 1
        elif face == '-x':
            check_x -= 1
        elif face == '+z':
            check_z += 1
        else:
            check_z -= 1

        #Check if more filling is necessary
        if terraform_down:
            if mc.getBlock(check_x, round(max_y - 1), check_z) in air_blocks:
                return False
            else:
                return True
        else:
            if mc.getBlock(check_x, round(max_y - 1), check_z) in air_blocks:
                return True
            else:
                return False

    else:
        if terraform_down:
            
            if 'z' in face:
                centre_offset = abs(x - centre_coords['x'])
            else:
                centre_offset = abs(z - centre_coords['z'])

            if centre_offset < 2 and corner_coords['y'] - level + 2 < corner_coords['y']:
                mc.setBlock(x, corner_coords['y'] - level + 2, z, terrain_layer_1[default_terrain_pallet])
        
        return True

def determine_terrain_pallet(x: int, y: int, z: int) -> str:
    """
    Arguments:
        x (int): The x coordinate to determine
        y (int): The y coordinate of the ground
        z (int): The z coordinate to determine

    Returns:
        terrain_pallet (str): The name of the terrain pallet the column uses. Either 'grass', 'sand', 'red_sand', 'snow', 'stone', 'gravel', 'corse_dirt', 'terracotta', 'podzol', or 'mycelium'.
    """ 

    block = tuple(mc.getBlockWithData(x, y, z))

    for k, v in terrain_layer_1.items():
        if v == block:
            return k

    #Support snow layers as well as snow
    if block == (78, 0):
        return 'snow'

    #Support sandstone as well as sand
    if block == (24, 0):
        return 'sand'

    #Support all terracotta
    if block[0] == 159:
        return 'terracotta'

    #Default to grass
    return 'grass'
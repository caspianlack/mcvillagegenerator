import mcpi.minecraft as minecraft
import random
import time
from math import sqrt
import terraforming
import positioning
import paths
mc = minecraft.Minecraft.create()
paths.debugging = False

def random_int_gen(min, max):                                           #RANDOM INT GENERATOR
    random.seed(float(time.time()))
    return random.randint(min, max)

def hollow_walls(p1, x, y, z, material, material_type):                 #GENERATES HOLLOW ROOMS
    mc.setBlocks(p1[0], p1[1], p1[2], 
                     p1[0] + x, p1[1] + y, p1[2] + z, 
                     material, material_type)
    
    mc.setBlocks(p1[0] + 1, p1[1], p1[2] + 1, 
                     p1[0] + x - 1, p1[1] + y, p1[2] + z - 1, 
                     0)

def set_wall(p1, x, y, z, material, material_type, variable, material6, material6_type):           #GENERATES INTERIOR WALL 
    if variable == 0:
        mc.setBlocks(p1[0] + x - 1, p1[1] + 1, p1[2] + 1, 
                     p1[0] + x + 1, p1[1] + + 1, p1[2] + z - 1, 
                     0)
        mc.setBlocks(p1[0] + x, p1[1] + 1, p1[2] + 1, 
                     p1[0] + x, p1[1] + y - 1, p1[2] + z - 1, 
                     material, material_type)
        mc.setBlocks(p1[0] + x, p1[1] + y, p1[2] + 1, 
                     p1[0] + x, p1[1] + y, p1[2] + z - 1, 
                     material6, material6_type)
    else:
        mc.setBlocks(p1[0] + 1, p1[1] + 1, p1[2] + z + 1, 
                     p1[0] + x - 1, p1[1] + 1, p1[2] + z - 1, 
                     0, 2)
        mc.setBlocks(p1[0] + 1, p1[1] + 1, p1[2] + z, 
                     p1[0] + x - 1, p1[1] + y - 1, p1[2] + z, 
                     material, material_type)
        mc.setBlocks(p1[0] + 1, p1[1] + y, p1[2] + z, 
                     p1[0] + x - 1, p1[1] + y, p1[2] + z, 
                     material6, material6_type)

def set_floor(p1, x, z, material, material_type, rotation):             #GENERATES FLOOR
    mc.setBlocks(p1[0] + 1, p1[1], p1[2] + 1, 
                     p1[0] + x - 1, p1[1], p1[2] + z - 1, 
                     material, material_type, rotation)

def set_door(point, xs, zs, variable):                                  #SETS DOORWAYS FOR INTERIOR
    n = random_int_gen(1, 3)
    m = abs(xs) % 2
    if variable == 0:
        if m == 1:
            mc.setBlocks(point[0] + xs, point[1] + 1, point[2] + n, 
                         point[0] + xs, point[1] + 2, point[2] + n, 
                         0)
        else:
            mc.setBlocks(point[0] + xs, point[1] + 1, point[2] + zs - n, 
                         point[0] + xs, point[1] + 2, point[2] + zs - n, 
                         0)
    else:
        if m == 1:
            mc.setBlocks(point[0] + n, point[1] + 1, point[2] + zs, 
                         point[0] + n, point[1] + 2, point[2] + zs, 
                         0)
        else:
            mc.setBlocks(point[0] + xs - n, point[1] + 1, point[2] + zs, 
                         point[0] + xs - n, point[1] + 2, point[2] + zs, 
                         0)


class House:                                                            #HOUSES CLASS
    def __init__(self, coords, center):                                 #center added as a parameter temporarily, later center should be accessed in a more practical way
        self.coords = list(coords)                                      #Coordinates of house and main door
        self.coords[1] = self.coords[1] + 1
        self.center = list(center)

        self.floors = 1                                                 #QUANTITY OF FLOORS
        self.x_extends = 0                                              #House measurements
        self.z_extends = 0                                              

        self.point = list(self.coords)
        self.rec_iterate = 0
        self.x_rec = 0
        self.z_rec = 0

        self.d_iter = 0
        self.dimension = 'x'                                            #dimension house is on and direction facing
        self.direction = 1
        self.door_coords = ()

        self.material1 = 5                                              #Walls
        self.material1_type = 0

        self.material2 = 17                                             #Support
        self.material2_type = 1

        self.material3 = 5                                              #Floor
        self.material3_type = 2

        self.mat_4_1_block = 5                                          #Roof main
        self.mat_4_1_block_data = 0
        self.mat_4_1_stairs = 53                                        #Stair direction will change by manipulating the block data value
        self.mat_4_1_slabs = 126                                        #Slab data will be extracted from block data and position will change by manipulating the block data value

        self.mat_4_2_block = 5                                          #Roof rail
        self.mat_4_2_block_data = 5
        self.mat_4_2_stairs = 164
        self.mat_4_2_slabs = 126

        self.material5 = 126                                            #Windows
        self.material5_type = 9

        self.material6 = 89                                             #light block
        self.material6_type = 0                             

        self.carpet_c = 14
        self.carpet_check = 0

        self.split = 0                       

    def roll_door(self):
        hx = self.coords[0]
        hz = self.coords[2]
        cx = self.center[0]
        cz = self.center[2]
        z_pos = True
        z_neg = True
        x_pos = True
        x_neg = True

        if hz > cz:
            z_pos = False
        if hz < cz:
            z_neg = False
        if hx > cx:
            x_pos = False
        if hx < cx:
            x_neg = False
        
        can_door = False

        while not can_door:
            roll = random.randint(1, 4)

            if roll == 1 and z_pos:
                self.dimension = 'z'
                self.direction = 1
                can_door = True
            elif roll == 2 and z_neg:
                self.dimension = 'z'
                self.direction = -1
                can_door = True
            elif roll == 3 and x_pos:
                self.dimension = 'x'
                self.direction = 1
                can_door = True
            elif roll == 4 and x_neg:
                self.dimension = 'x'
                self.direction = -1
                can_door = True

    def set_main_door(self):
        i = 0
        row = 0
        is_space = [] 

        if self.direction == 1 and self.dimension == 'x':
            blocks_list = list(mc.getBlocks(self.coords[0] + self.x_extends - 1, self.coords[1] + 3, self.coords[2] + 1,
                                            self.coords[0] + self.x_extends - 1, self.coords[1] + 3, self.coords[2] + self.z_extends - 1))

            while i < self.z_extends - 1:
                if blocks_list[i] == 0:
                    is_space.append(0)
                    row += 1

                    if row == 3:
                        mc.setBlocks(self.coords[0] + self.x_extends + 1, self.coords[1] + 1, self.coords[2] + 1 + i - 1,       #Clears window decorations
                                     self.coords[0] + self.x_extends + 1, self.coords[1] + 4, self.coords[2] + 1 + i + 1, 0)
                        mc.setBlocks(self.coords[0] + self.x_extends, self.coords[1] + 1, self.coords[2] + 1 + i - 1,           #Borders doorway
                                     self.coords[0] + self.x_extends, self.coords[1] + 4, self.coords[2] + 1 + i + 1, self.material1, self.material1_type)
                        mc.setBlocks(self.coords[0] + self.x_extends, self.coords[1] + 1, self.coords[2] + i + 1,
                                     self.coords[0] + self.x_extends, self.coords[1] + 2, self.coords[2] + i + 1, 0)
                        mc.setBlock(self.coords[0] + self.x_extends, self.coords[1] + 2, self.coords[2] + i + 1, 197, 9)        #Creates door
                        mc.setBlock(self.coords[0] + self.x_extends, self.coords[1] + 1, self.coords[2] + i + 1, 197, 1)
                        self.door_coords = (self.coords[0] + self.x_extends + 2, self.coords[1], self.coords[2] + 1 + i - 1)    #Sets door_coords
                        mc.setBlock(self.coords[0] + self.x_extends + 1, self.coords[1], self.coords[2] + 1 + i, self.mat_4_1_stairs, 1)
                        mc.setBlocks(self.coords[0] + self.x_extends, self.coords[1] - 1, self.coords[2] + i,
                                     self.coords[0] + self.x_extends + 2, self.coords[1] - 1, self.coords[2] + 2 + i, 4)
                        break

                else:
                    is_space.append(1)
                    row = 0
            i += 1
        elif self.direction == -1 and self.dimension == 'x':
            blocks_list = list(mc.getBlocks(self.coords[0] + 1, self.coords[1] + 3, self.coords[2] + 1,
                                            self.coords[0] + 1, self.coords[1] + 3, self.coords[2] + self.z_extends - 1))
            while i < self.z_extends - 1:
                if blocks_list[i] == 0:
                    is_space.append(0)
                    row += 1

                    if row == 3:
                        mc.setBlocks(self.coords[0] - 1, self.coords[1] + 1, self.coords[2] + 1 + i - 1,
                                     self.coords[0] - 1, self.coords[1] + 4, self.coords[2] + 1 + i + 1, 0)
                        mc.setBlocks(self.coords[0], self.coords[1] + 1, self.coords[2] + 1 + i - 1,
                                     self.coords[0], self.coords[1] + 4, self.coords[2] + 1 + i + 1, self.material1, self.material1_type)
                        mc.setBlocks(self.coords[0], self.coords[1] + 1, self.coords[2] + i + 1,
                                     self.coords[0], self.coords[1] + 2, self.coords[2] + i + 1, 0)
                        mc.setBlock(self.coords[0], self.coords[1] + 2, self.coords[2] + i + 1, 197, 9)
                        mc.setBlock(self.coords[0], self.coords[1] + 1, self.coords[2] + i + 1, 197, 1)
                        mc.setBlock(self.coords[0] - 1, self.coords[1], self.coords[2] + 1 + i, self.mat_4_1_stairs, 0)
                        mc.setBlocks(self.coords[0] - 2, self.coords[1] - 1, self.coords[2] + i,
                                    self.coords[0], self.coords[1] - 1, self.coords[2] + 2 + i, 4)
                        self.door_coords = (self.coords[0] - 2, self.coords[1], self.coords[2] + 1 + i - 1)
                        break
                else:
                    is_space.append(1)
                    row = 0
            i += 1
        elif self.direction == 1 and self.dimension == 'z':
            blocks_list = list(mc.getBlocks(self.coords[0] + 1, self.coords[1] + 3, self.coords[2] + self.z_extends - 1,
                                            self.coords[0] + self.x_extends - 1, self.coords[1] + 3, self.coords[2] + self.z_extends - 1))

            while i < self.x_extends - 1:
                if blocks_list[i] == 0:
                    is_space.append(0)
                    row += 1

                    if row == 3:
                        mc.setBlocks(self.coords[0] + 1 + i - 1, self.coords[1] + 1, self.coords[2] + self.z_extends + 1,
                                      self.coords[0] + 1 + i + 1, self.coords[1] + 4, self.coords[2] + self.z_extends + 1, 0)
                        mc.setBlocks(self.coords[0] + 1 + i - 1, self.coords[1] + 1, self.coords[2] + self.z_extends,
                                      self.coords[0] + 1 + i + 1, self.coords[1] + 4, self.coords[2] + self.z_extends, self.material1, self.material1_type)
                        mc.setBlocks(self.coords[0] + 1 + i, self.coords[1] + 1, self.coords[2] + self.z_extends,
                                      self.coords[0] + 1 + i, self.coords[1] + 2, self.coords[2] + self.z_extends, 0)
                        mc.setBlock(self.coords[0] + 1 + i, self.coords[1] + 2, self.coords[2] + self.z_extends, 197, 9)
                        mc.setBlock(self.coords[0] + 1 + i, self.coords[1] + 1, self.coords[2] + self.z_extends, 197, 1)
                        mc.setBlock(self.coords[0] + 1 + i, self.coords[1], self.coords[2] + self.z_extends + 1, self.mat_4_1_stairs, 3)
                        mc.setBlocks(self.coords[0] + i, self.coords[1] - 1, self.coords[2] + self.z_extends,
                                     self.coords[0] + 2 + i, self.coords[1] - 1, self.coords[2] + self.z_extends + 2, 4)
                        self.door_coords = (self.coords[0] + 1 + i, self.coords[1] - 1, self.coords[2] + self.z_extends + 2)
                        break
                else:
                    is_space.append(1)
                    row = 0
            i += 1

        elif self.direction == -1 and self.dimension == 'z':
            blocks_list = list(mc.getBlocks(self.coords[0] + 1, self.coords[1] + 3, self.coords[2] + 1,
                                            self.coords[0] + self.x_extends - 1, self.coords[1] + 3, self.coords[2] + 1))
            while i < self.x_extends - 1:
                if blocks_list[i] == 0:
                    is_space.append(0)
                    row += 1

                    if row == 3:
                        mc.setBlocks(self.coords[0] + 1 + i - 1, self.coords[1] + 1, self.coords[2] - 1,
                                      self.coords[0] + 1 + i + 1, self.coords[1] + 4, self.coords[2] - 1, 0)
                        mc.setBlocks(self.coords[0] + 1 + i - 1, self.coords[1] + 1, self.coords[2],
                                      self.coords[0] + 1 + i + 1, self.coords[1] + 4, self.coords[2], self.material1, self.material1_type)
                        mc.setBlocks(self.coords[0] + 1 + i, self.coords[1] + 1, self.coords[2],
                                      self.coords[0] + 1 + i, self.coords[1] + 2, self.coords[2], 0)
                        mc.setBlock(self.coords[0] + 1 + i, self.coords[1] + 2, self.coords[2], 197, 9)
                        mc.setBlock(self.coords[0] + 1 + i, self.coords[1] + 1, self.coords[2], 197, 1)
                        mc.setBlock(self.coords[0] + 1 + i, self.coords[1], self.coords[2] - 1, self.mat_4_1_stairs, 2)
                        mc.setBlocks(self.coords[0] + i, self.coords[1] - 1, self.coords[2] - 2,
                                     self.coords[0] + 2 + i, self.coords[1] - 1, self.coords[2], 4)
                        self.door_coords = (self.coords[0] + 1 + i, self.coords[1] - 1, self.coords[2] -2)
                        break
                    
                else:
                    is_space.append(1)
                    row = 0
            i += 1
                        
    def roll_floors(self):                                              #DETERMINES THE AMOUNT OF FLOORS
        area = self.x_extends * self.z_extends
        if area > 170: #150
            self.floors = 2
        else:
            self.floors = 1

    def roll_house_border(self):                                        #DETERMINES THE HOUSE BORDER
        if random_int_gen(0, 1) > 0:                                    #Dimensions are extended from the
            self.x_extends = random_int_gen(15, 25)                     #origin in the positive x and z
            self.z_extends = random_int_gen(10, 15)
        else:
            self.x_extends = random_int_gen(10, 15)
            self.z_extends = random_int_gen(15, 25)
        
    def generate_house_border(self):                                    #GENERATES THE HOUSE BORDER
        y = self.floors * 4 + 1

        hollow_walls(self.coords, self.x_extends, y, self.z_extends, self.material1, self.material1_type)
        set_floor(self.point, self.x_extends, self.z_extends, self.material3, self.material3_type, self.material3_rotation)


    def reroll_floor(self):                                             #RE-DETERMINES THE FLOOR MATERIAL

        mat3_dict_planks =  { 1 : 0,                                    #Oak planks         #Regular quartz
                              2 : 1,                                    #Spruce planks      #Chiseled quartz
                              3 : 2,                                    #Birch planks       #Quartz Pillar (up)
                              4 : 3,                                    #Jungle planks      #Quartz pillar (north)
                              5 : 5 }                                   #Dark planks        #Quartz pillar (east)

        time.sleep(0.5)
        mat3_type = random_int_gen(1, 5)
        self.material3_type = mat3_dict_planks[mat3_type]
    
    def roll_materials(self):                                           #DETERMINES ALL MATERIALS
                                                                        #WALLS
        mat1_dict =        { 1 : 5,                                     #Planks             \
                             2 : 80,                                    #Snow (block)
                             3 : 159 }                                  #Hardened clay 
            
        mat1_dict_planks = { 1 : 0,                                     #Oak planks
                             2 : 1,                                     #Spruce planks
                             3 : 2,                                     #Birch planks
                             4 : 3,                                     #Jungle planks
                             5 : 5 }                                    #Dark oak planks
    
        mat1_dict_snow =  { 1 : 0,                                      #Snow
                            2 : 0,
                            3 : 0,
                            4 : 0,
                            5 : 0 }

        mat1_dict_clay = { 1 : 0,                                       #White
                           2 : 3,                                       #Blue
                           3 : 5,                                       #Green
                           4 : 8,                                       #Gray
                           5 : 9 }                                      #Cyan
        
        mat1_cat = random_int_gen(1, 3)
        mat1_type = random_int_gen(1, 5)

        self.material1 = mat1_dict[mat1_cat]

        if mat1_cat == 1:
            self.material1_type = mat1_dict_planks[mat1_type]
        elif mat1_cat == 3:
            self.material1_type = mat1_dict_clay[mat1_type]
        else:
            self.material1_type = mat1_dict_snow[mat1_type]
                                                                        #SUPPORTS
        mat2_dict =      { 1 : 17,                                      #Log                
                           2 : 162,                                     #Log2
                           3 : 155 }                                    #Quartz Pillar                                         

        mat2_dict_log =  { 1 : 0,                                       #Oak
                           2 : 1 }                                      #Spruce
        
        mat2_dict_log2 = { 1 : 0,                                       #Dark oak
                           2 : 1 }                                      #Acacia

        mat2_dict_q_piller = {1 : 2,                                    #Pillar
                              2 : 2,
                              1 : 2,
                              2 : 2 }

        mat2_cat = random_int_gen(1, 3)
        mat2_type = random_int_gen(1, 2)

        self.material2 = mat2_dict[mat2_cat]

        if mat2_cat == 1:
            self.material2_type = mat2_dict_log[mat2_type]
        elif mat2_cat == 2:
            self.material2_type = mat2_dict_log2[mat2_type]
        else:
            self.material2_type = mat2_dict_q_piller[mat2_type]
                                                                        #FLOORS
        mat3_dict =      { 1 : 5,                                       #Planks             
                           2 : 155 }                                    #Quartz

        mat3_dict_planks = { 1 : 0,                                     #Oak
                             2 : 1,                                     #Spruce
                             3 : 2,                                     #Birch
                             4 : 3,                                     #Jungle
                             5 : 5 }                                    #Dark

        mat3_dict_Quartz = { 1 : 0,                                     #Quartz
                             2 : 1,                                     #Chiseled
                             3 : 2,                                     #Pillar
                             4 : 0,                                     #Quartz2
                             5 : 2 }                                    #Pillar2

        mat3_cat = random_int_gen(1, 2)
        mat3_type = random_int_gen(1, 5)
        
        self.material3 = mat3_dict[mat3_cat]

        if mat3_cat == 1:
            self.material3_type = mat3_dict_planks[mat3_type]
        elif mat3_cat == 2:
            self.material3_type = mat3_dict_Quartz[mat3_type]
        else:
            self.material3_type = 8

        self.material3_rotation = random_int_gen(2, 5)#direction randomiser incase quartz pillars are selected for floor
        
        if self.material1 == self.material3 and self.material1_type == self.material3_type:
            self.reroll_floor()

        mat5_dict =         { 1 : 126,                                  #CEILING  
                              2 : 44 }

        mat5_dict_plank =   { 1 : 8,
                              2 : 9,
                              3 : 13 }

        mat5_dict_stone =   { 1 : 8,
                              2 : 15 }

        coin_flip = random_int_gen(1, 2)
        if coin_flip == 1:
            self.material5 = 126
            coin_flip2 = random_int_gen(1, 3)
            self.material5_type = mat5_dict_plank[coin_flip2]
        else:
            self.material5 = 44
            coin_flip2 = random_int_gen(1, 2)
            self.material5_type = mat5_dict_stone[coin_flip2]

                                                                        #ROOF
        choice = random_int_gen(1, 6)                                   #MAIN
        if choice < 5:
            if choice == 1:                                             #Oak planks
                self.mat_4_1_block = 5
                self.mat_4_1_block_data = 0
                self.mat_4_1_slabs = 126
                self.mat_4_1_stairs = 53
            elif choice == 2:                                           #Quartz
                self.mat_4_1_block = 155
                self.mat_4_1_block_data = 7
                self.mat_4_1_slabs = 44
                self.mat_4_1_stairs = 156
            elif choice == 3:                                           #Spruce planks
                self.mat_4_1_block = 5
                self.mat_4_1_block_data = 1
                self.mat_4_1_slabs = 126
                self.mat_4_1_stairs = 134
            else:                                                       #Birch planks
                self.mat_4_1_block = 5
                self.mat_4_1_block_data = 2
                self.mat_4_1_slabs = 126
                self.mat_4_1_stairs = 135
        else:
            if choice == 5:                                             #Dark oak planks
                self.mat_4_1_block = 5
                self.mat_4_1_block_data = 5
                self.mat_4_1_slabs = 126
                self.mat_4_1_stairs = 164
            elif choice == 6:                                           #Stone bricks
                self.mat_4_1_block = 98                         
                self.mat_4_1_block_data = 5
                self.mat_4_1_slabs = 44
                self.mat_4_1_stairs = 109
            elif choice == 7:                                           #Bricks
                self.mat_4_1_block = 45                         
                self.mat_4_1_block_data = 4
                self.mat_4_1_slabs = 44
                self.mat_4_1_stairs = 108
            else:                                                       #Nether brick
                self.mat_4_1_block = 112                        
                self.mat_4_1_block_data = 6
                self.mat_4_1_slabs = 44
                self.mat_4_1_stairs = 114
        
        choice2 = random_int_gen(1, 6)                                  #RAIL
        while choice2 == choice:
            choice2 = random_int_gen(1, 6)
        if choice2 < 5:
            if choice2 == 1:                                            #Oak planks
                self.mat_4_2_block = 5
                self.mat_4_2_block_data = 0
                self.mat_4_2_slabs = 126
                self.mat_4_2_stairs = 53
            elif choice2 == 2:                                          #Quartz
                self.mat_4_2_block = 155
                self.mat_4_2_block_data = 7
                self.mat_4_2_slabs = 44
                self.mat_4_2_stairs = 156
            elif choice2 == 3:                                          #Spruce planks
                self.mat_4_2_block = 5
                self.mat_4_2_block_data = 1
                self.mat_4_2_slabs = 126
                self.mat_4_2_stairs = 134
            else:                                                       #Birch planks
                self.mat_4_2_block = 5
                self.mat_4_2_block_data = 2
                self.mat_4_2_slabs = 126
                self.mat_4_2_stairs = 135
        else:
            if choice2 == 5:                                            #Dark oak planks
                self.mat_4_2_block = 5
                self.mat_4_2_block_data = 5
                self.mat_4_2_slabs = 126
                self.mat_4_2_stairs = 164
            elif choice2 == 6:                                          #Stone bricks
                self.mat_4_2_block = 98                         
                self.mat_4_2_block_data = 5
                self.mat_4_2_slabs = 44
                self.mat_4_2_stairs = 109
            elif choice2 == 7:                                          #Bricks
                self.mat_4_2_block = 45                         
                self.mat_4_2_block_data = 4
                self.mat_4_2_slabs = 44
                self.mat_4_2_stairs = 108
            else:                                                       #Nether brick
                self.mat_4_2_block = 112                        
                self.mat_4_2_block_data = 6
                self.mat_4_2_slabs = 44
                self.mat_4_2_stairs = 114
        
        carpet_dict =      { 1 : 3,                                     #Blues
                             2 : 9,                                    
                             3 : 11,
                             4 : 15,                                    #Black
                             5 : 7,                                     #Grays
                             6 : 8,
                             7 : 5,                                     #Greens
                             8 : 13,
                             9 : 14}                                    #Red

        coin_flip = random_int_gen(1, 9)
        self.carpet_c = carpet_dict[coin_flip]
    
    def set_ceiling(self):
        mc.setBlocks(self.point[0] + 1, self.point[1] + 4, self.point[2] + 1, 
                     self.point[0] + self.x_extends - 1, self.point[1] + 4, self.point[2] + self.z_extends - 1, 
                     self.material5, self.material5_type)
        if self.floors == 2:
            mc.setBlocks(self.point[0] + 1, self.point[1] + 9, self.point[2] + 1, 
                     self.point[0] + self.x_extends - 1, self.point[1] + 9, self.point[2] + self.z_extends - 1, 
                     self.material5, self.material5_type)
    
    def recurse_floor_plan(self, x, z):                                 #FLOOR PLAN RECURSION
        x_len = x + 1
        z_len = z + 1
        split_x = x
        split_z = z
        if self.carpet_check == 1:
            self.carpet_check = 42
            mc.setBlocks(self.coords[0] + 2, self.coords[1] + 6, self.coords[2] + 2,
                         self.coords[0] + self.x_extends - 2, self.coords[1] + 6, self.coords[2] + self.z_extends - 2, 171, self.carpet_c)
        
        x_mid = int(x_len / 2)  
        z_mid = int(z_len / 2)
        
        if random_int_gen(0, 1) == 1 and x_len > 8:                
            l_space = 0
            r_space = 0
            
            while l_space < 3 or r_space < 3:                           #Splitting x in the z axis
                split_x = x_mid + random_int_gen(-1, 1)
                r_space = x_len - split_x - 1
                l_space = split_x - 2
                self.split = 0
                if self.rec_iterate == 0:
                    self.x_rec = split_x

        elif z_len > 8:
            u_space = 0
            d_space = 0
                
            while u_space < 3 or d_space < 3:                           #Splitting z in the x axis
                split_z = z_mid + random_int_gen(-1, 1)
                d_space = z_len - split_z - 1
                u_space = split_z - 2
                self.split = 1
                if self.rec_iterate == 0:
                    self.z_rec = split_z

        self.reroll_floor()                                             #Re-rolls floor material and sets walls, floor and interior door
        set_wall(self.point, split_x, 4, split_z, self.material1, self.material1_type, self.split, self.material6, self.material6_type)
        set_floor(self.point, split_x, split_z, self.material3, self.material3_type, self.material3_rotation)
        set_door(self.point, split_x, split_z, self.split)
        
        if split_z > 7 or split_x > 7:
            self.rec_iterate += 1
            self.recurse_floor_plan(split_x, split_z)

    def set_stairs(self):
        position = 0

        if self.floors == 2:
            if self.z_rec == 0:
                if self.dimension == 'x' and self.direction == -1:
                    position = 1
                elif self.dimension == 'x' and self.direction == 1 and self.door_coords[2] < (self.coords[2] + (self.z_extends // 2)):
                    position = 1
                elif self.dimension == 'x' and self.direction == 1 and self.door_coords[2] >= (self.coords[2] + (self.z_extends //2)):
                    position = 2
                elif self.dimension == 'z' and self.direction == 1:
                    position = 2
                elif self.dimension == 'z' and self.direction == -1:
                    position = 1
            elif self.x_rec == 0:
                if self.dimension == 'x' and self.direction == 1:
                    position = 3
                elif self.dimension == 'x' and self.direction == -1:
                    position = 1
                elif self.dimension == 'z' and self.direction == 1 and self.door_coords[0] < (self.coords[0] + (self.x_extends // 2)):
                    position = 1
                elif self.dimension == 'z' and self.direction == 1 and self.door_coords[0] >= (self.coords[0] + (self.x_extends // 2)):
                    position = 3
                elif self.dimension == 'z' and self.direction == -1:
                    position = 3

            if position == 1:
                mc.setBlocks(self.coords[0] + self.x_extends - 3, self.coords[1] + 1, self.coords[2] + self.z_extends - 3,
                             self.coords[0] + self.x_extends - 1, self.coords[1] + 5, self.coords[2] + self.z_extends - 1, 0)
                mc.setBlock(self.coords[0] + self.x_extends - 1, self.coords[1] + 1, self.coords[2] + self.z_extends - 3, self.mat_4_1_stairs, 2)
                mc.setBlock(self.coords[0] + self.x_extends - 1, self.coords[1] + 1, self.coords[2] + self.z_extends - 2, self.mat_4_1_stairs, 7)
                mc.setBlock(self.coords[0] + self.x_extends - 1, self.coords[1] + 2, self.coords[2] + self.z_extends - 2, self.mat_4_1_stairs, 2)
                mc.setBlock(self.coords[0] + self.x_extends - 1, self.coords[1] + 2, self.coords[2] + self.z_extends - 1, self.mat_4_1_stairs, 6)
                mc.setBlock(self.coords[0] + self.x_extends - 2, self.coords[1] + 2, self.coords[2] + self.z_extends - 1, self.mat_4_1_stairs, 4)
                mc.setBlock(self.coords[0] + self.x_extends - 2, self.coords[1] + 2, self.coords[2] + self.z_extends - 1, self.mat_4_1_stairs, 4)
                mc.setBlock(self.coords[0] + self.x_extends - 2, self.coords[1] + 3, self.coords[2] + self.z_extends - 1, self.mat_4_1_stairs, 1)
                mc.setBlock(self.coords[0] + self.x_extends - 3, self.coords[1] + 3, self.coords[2] + self.z_extends - 1, self.mat_4_1_stairs, 4)
                mc.setBlock(self.coords[0] + self.x_extends - 3, self.coords[1] + 3, self.coords[2] + self.z_extends - 2, self.mat_4_1_stairs, 6)
                mc.setBlock(self.coords[0] + self.x_extends - 3, self.coords[1] + 4, self.coords[2] + self.z_extends - 3, self.mat_4_1_stairs, 6)
                mc.setBlock(self.coords[0] + self.x_extends - 3, self.coords[1] + 4, self.coords[2] + self.z_extends - 2, self.mat_4_1_stairs, 3)
                mc.setBlock(self.coords[0] + self.x_extends - 3, self.coords[1] + 5, self.coords[2] + self.z_extends - 3, self.mat_4_1_stairs, 3)
            elif position == 2:
                mc.setBlocks(self.coords[0] + self.x_extends - 3, self.coords [1] + 1, self.coords[2] + 3,
                             self.coords[0] + self.x_extends - 1, self.coords[1] + 5, self.coords[2] + 1, 0)
                mc.setBlock(self.coords[0] + self.x_extends - 1, self.coords[1] + 1, self.coords[2] + 3, self.mat_4_1_stairs, 3)
                mc.setBlock(self.coords[0] + self.x_extends - 1, self.coords[1] + 1, self.coords[2] + 2, self.mat_4_1_stairs, 6)
                mc.setBlock(self.coords[0] + self.x_extends - 1, self.coords[1] + 2, self.coords[2] + 2, self.mat_4_1_stairs, 3)
                mc.setBlock(self.coords[0] + self.x_extends - 1, self.coords[1] + 2, self.coords[2] + 1, self.mat_4_1_stairs, 6)
                mc.setBlock(self.coords[0] + self.x_extends - 2, self.coords[1] + 2, self.coords[2] + 1, self.mat_4_1_stairs, 4)
                mc.setBlock(self.coords[0] + self.x_extends - 2, self.coords[1] + 3, self.coords[2] + 1, self.mat_4_1_stairs, 1)
                mc.setBlock(self.coords[0] + self.x_extends - 3, self.coords[1] + 3, self.coords[2] + 1, self.mat_4_1_stairs, 4)
                mc.setBlock(self.coords[0] + self.x_extends - 3, self.coords[1] + 3, self.coords[2] + 2, self.mat_4_1_stairs, 7)
                mc.setBlock(self.coords[0] + self.x_extends - 3, self.coords[1] + 4, self.coords[2] + 2, self.mat_4_1_stairs, 2)
                mc.setBlock(self.coords[0] + self.x_extends - 3, self.coords[1] + 4, self.coords[2] + 3, self.mat_4_1_stairs, 7)
                mc.setBlock(self.coords[0] + self.x_extends - 3, self.coords[1] + 5, self.coords[2] + 3, self.mat_4_1_stairs, 2)


            elif position == 3:
                mc.setBlocks(self.coords[0] + 1, self.coords[1] + 1, self.coords[2] + self.z_extends - 3,
                             self.coords[0] + 3, self.coords[1] + 1, self.coords[2] + self.z_extends - 1, 133)  #emerald
                mc.setBlocks(self.coords[0] + 1, self.coords[1] + 1, self.coords[2] + self.z_extends - 3,
                             self.coords[0] + 3, self.coords[1] + 5, self.coords[2] + self.z_extends - 1, 0)
                mc.setBlock(self.coords[0] + 1, self.coords[1] + 1, self.coords[2] + self.z_extends - 3, self.mat_4_1_stairs, 2)
                mc.setBlock(self.coords[0] + 1, self.coords[1] + 1, self.coords[2] + self.z_extends - 2, self.mat_4_1_stairs, 7)
                mc.setBlock(self.coords[0] + 1, self.coords[1] + 2, self.coords[2] + self.z_extends - 2, self.mat_4_1_stairs, 2)
                mc.setBlock(self.coords[0] + 1, self.coords[1] + 2, self.coords[2] + self.z_extends - 1, self.mat_4_1_stairs, 7)
                mc.setBlock(self.coords[0] + 2, self.coords[1] + 2, self.coords[2] + self.z_extends - 1, self.mat_4_1_stairs, 5)
                mc.setBlock(self.coords[0] + 2, self.coords[1] + 3, self.coords[2] + self.z_extends - 1, self.mat_4_1_stairs, 0)
                mc.setBlock(self.coords[0] + 3, self.coords[1] + 3, self.coords[2] + self.z_extends - 1, self.mat_4_1_stairs, 5)
                mc.setBlock(self.coords[0] + 3, self.coords[1] + 3, self.coords[2] + self.z_extends - 2, self.mat_4_1_stairs, 6)
                mc.setBlock(self.coords[0] + 3, self.coords[1] + 3, self.coords[2] + self.z_extends - 2, self.mat_4_1_stairs, 6)
                mc.setBlock(self.coords[0] + 3, self.coords[1] + 4, self.coords[2] + self.z_extends - 2, self.mat_4_1_stairs, 3)
                mc.setBlock(self.coords[0] + 3, self.coords[1] + 4, self.coords[2] + self.z_extends - 3, self.mat_4_1_stairs, 6)
                mc.setBlock(self.coords[0] + 3, self.coords[1] + 5, self.coords[2] + self.z_extends - 3, self.mat_4_1_stairs, 3)


    def search_wall_w(self, variant):                                   #SEARCH FOR WALLS WEST AND EAST
        i = 0                                                           #Iterates through outside of wall
        z1 = self.point[2] + 1                                          #returning a list with binary elements
        z2 = self.point[2] + 2

        if variant == 1:
            z1 = self.point[2] + self.z_extends - 2
            z2 = self.point[2] + self.z_extends - 1

        wall_ids = list(mc.getBlocks(self.point[0], self.point[1] + 3, z1,
                                     self.point[0] + self.x_extends, self.point[1] + 3, z1))
        is_space = list()
        
        while i < self.x_extends + 1:
            if wall_ids[i] == 0:
                is_space.append(0)
            else:
                is_space.append(1)
            i += 1

        return is_space
    
    def search_wall_n(self, variant):                                   #SEARCH FOR WALLS NORTH AND SOUTH
        i = 0                                                           #Iterates through outside of wall
        x1 = self.point[0] + 1                                          #returning a list with binary elements
        x2 = self.point[0] + 2

        if variant == 1:
            x1 = self.point[0] + self.x_extends - 2
            x2 = self.point[0] + self.x_extends - 1
        
        wall_ids = list(mc.getBlocks(x1, self.point[1] + 3, self.point[2],
                                      x1, self.point[1] + 3, self.point[2] + self.z_extends))
        is_space = list()

        while i < self.z_extends + 1:
            if wall_ids[i] == 0:
                is_space.append(0)
            else:
                is_space.append(1)
            i += 1
        return is_space

    def generate_windows_w(self, list, variant):                        #SETS AND GENERATES WINDOWS AND SOME SUPPORT WEST AND EAST
        is_space = list                                                 #Takes binary list as input
        space = 0                                                       #Generates windows and support depending on room sizes
        z = self.point[2]
        j = 0
        z_add = -1
        direction = 6

        if variant == 1:
            z = self.point[2] + self.z_extends
            z_add = 1
            direction = 7
            

        while j < self.x_extends + 1:
            if is_space[j] == 0:
                space += 1
            else:
                if space > 2:
                    mc.setBlocks(self.point[0] + j - 2, self.point[1] + 2, z,                                   #Sets glass
                                 self.point[0] + j - space + 1, self.point[1] + 3, z, 
                                 95, 0)
                    mc.setBlocks(self.point[0] + j - 2, self.point[1] + 1, z + z_add,                           #Sets Stair and slabs
                                 self.point[0] + j - space + 1, self.point[1] + 1, z + z_add, 
                                 self.mat_4_2_stairs, direction)
                    mc.setBlocks(self.point[0] + j - 2, self.point[1] + 4, z + z_add, 
                                 self.point[0] + j - space + 1, self.point[1] + 4, z + z_add, 
                                 self.mat_4_2_slabs, self.mat_4_2_block_data)
                if space > 8:
                    mc.setBlocks(self.point[0] + j - (space / 2) + (space / 6), self.point[1]+ 2, z,            #Divides windows
                                 self.point[0] + j - (space / 2) + (space / 6), self.point[1]+ 3, z, 
                                 self.material1, self.material1_type)
                    mc.setBlocks(self.point[0] + j - (space / 2) - (space / 6), self.point[1]+ 2, z, 
                                 self.point[0] + j - (space / 2) - (space / 6), self.point[1]+ 3, z, 
                                 self.material1, self.material1_type)
                    mc.setBlocks(self.point[0] + j - (space / 2) + (space / 6), self.point[1] + 1, z + z_add,   #Divides window ledged
                                 self.point[0] + j - (space / 2) + (space / 6), self.point[1] + 4, z + z_add, 
                                 0)
                    mc.setBlocks(self.point[0] + j - (space / 2) - (space / 6), self.point[1] + 1, z + z_add, 
                                 self.point[0] + j - (space / 2) - (space / 6), self.point[1] + 4, z + z_add, 
                                 0)
                if space > 6:
                    mc.setBlocks(self.point[0] + j - space / 2, self.point[1]+ 2, z,                            #Divides windows
                                 self.point[0] + j - space / 2, self.point[1]+ 3, z, 
                                 self.material1, self.material1_type)
                    mc.setBlocks(self.point[0] + j - space / 2, self.point[1]+ 1, z + z_add,                    #Divides Ledges
                                 self.point[0] + j - space / 2, self.point[1]+ 4, z + z_add, 
                                 0)
                if variant == 0 and j < self.x_extends and j > 0:                                               #Structual support
                    mc.setBlocks(self.point[0] + j, self.point[1], self.point[2] - 1,
                                 self.point[0] + j, self.point[1] + 4, self.point[2] - 1,
                                 self.material2, self.material2_type)
                elif variant == 1 and j < self.x_extends and j > 0:                                             #Structual support
                    mc.setBlocks(self.point[0] + j, self.point[1], self.point[2] + self.z_extends + 1,
                                 self.point[0] + j, self.point[1] + 4, self.point[2] + self.z_extends + 1,
                                 self.material2, self.material2_type)
                space = 0
            j += 1
    
    def generate_windows_n(self, list, variant):                        #SETS AND GENERATES WINDOWS AND SOME SUPPORT NORTH AND SOUTH
        is_space = list                                                 #Takes binary list as input
        space = 0                                                       #Generates windows and support depending on room sizes
        x = self.point[0]
        j = 0
        direction = 4
        x_add =  - 1

        if variant == 1:
            x = self.point[0] + self.x_extends
            x_add =  1
            direction = 5

        while j < self.z_extends + 1:
            if is_space[j] == 0:
                space += 1
            else:
                if space > 2:
                    mc.setBlocks(x, self.point[1] + 2, self.point[2] + j - 2,
                                 x, self.point[1] + 3, self.point[2] + j - space + 1,
                                 95, 0)
                    mc.setBlocks(x + x_add, self.point[1] + 1, self.point[2] + j - 2,
                                 x + x_add, self.point[1] + 1, self.point[2] + j - space + 1,
                                 self.mat_4_2_stairs, direction)
                    mc.setBlocks(x + x_add, self.point[1] + 4, self.point[2] + j - 2,
                                 x + x_add, self.point[1] + 4, self.point[2] + j - space + 1,
                                 self.mat_4_2_slabs, self.mat_4_2_block_data)
                if space > 8:
                    mc.setBlocks(x, self.point[1] + 2, self.point[2] + j - (space / 2) + (space / 6), 
                                 x, self.point[1] + 3, self.point[2] + j - (space / 2) + (space / 6), 
                                 self.material1, self.material1_type)
                    mc.setBlocks(x, self.point[1] + 2, self.point[2] + j - (space / 2) - (space / 6), 
                                 x, self.point[1] + 3, self.point[2] + j - (space / 2) - (space / 6), 
                                 self.material1, self.material1_type)
                    mc.setBlocks(x + x_add, self.point[1] + 1, self.point[2] + j - (space / 2) + (space / 6), 
                                 x + x_add, self.point[1] + 4, self.point[2] + j - (space / 2) + (space / 6), 
                                 0)
                    mc.setBlocks(x + x_add, self.point[1] + 1, self.point[2] + j - (space / 2) - (space / 6), 
                                 x + x_add, self.point[1] + 4, self.point[2] + j - (space / 2) - (space / 6), 
                                 0)
                if space > 6:
                    mc.setBlocks(x, self.point[1] + 2, self.point[2] + j - space / 2, 
                                 x, self.point[1] + 3, self.point[2] + j - space / 2, 
                                 self.material1, self.material1_type)
                    mc.setBlocks(x + x_add, self.point[1] + 1, self.point[2] + j - space / 2, 
                                 x + x_add, self.point[1] + 4, self.point[2] + j - space / 2, 
                                 0)
                if variant == 0 and j < self.z_extends and j > 0:                                               #Structual support
                    mc.setBlocks(self.point[0] - 1, self.point[1], self.point[2] + j,
                                 self.point[0] - 1, self.point[1] + 4, self.point[2] + j,
                                 self.material2, self.material2_type)
                if variant == 1 and j < self.z_extends and j > 0:                                               #Structual support
                    mc.setBlocks(self.point[0] + self.x_extends + 1, self.point[1], self.point[2] + j,
                                 self.point[0] + self.x_extends + 1, self.point[1] + 4, self.point[2] + j,
                                 self.material2, self.material2_type)
                space = 0
            j += 1

    def generate_windows(self):                                         #GENERATES WINDOWS AND SUPPORT
        is_space = self.search_wall_w(0)
        self.generate_windows_w(is_space, 0)
        is_space = self.search_wall_w(1)
        self.generate_windows_w(is_space, 1)
        is_space = self.search_wall_n(0)
        self.generate_windows_n(is_space, 0)
        is_space = self.search_wall_n(1)
        self.generate_windows_n(is_space, 1)
        if self.floors == 2:
            self.point[1] = self.point[1] - 5
        is_space = self.search_wall_w(0)
        self.generate_windows_w(is_space, 0)
        is_space = self.search_wall_w(1)
        self.generate_windows_w(is_space, 1)
        is_space = self.search_wall_n(0)
        self.generate_windows_n(is_space, 0)
        is_space = self.search_wall_n(1)
        self.generate_windows_n(is_space, 1)

    def generate_structural_support(self):                              #GENERATES BORDER SUPPORT
        mc.setBlocks(self.coords[0] - 1, self.coords[1], self.coords[2] - 1,
                     self.coords[0] - 1, self.coords[1] + self.floors * 5, self.coords[2] - 1,
                     self.material2, self.material2_type)
        mc.setBlocks(self.coords[0] - 1, self.coords[1], self.coords[2] + self.z_extends + 1,
                     self.coords[0] - 1, self.coords[1] + self.floors * 5, self.coords[2] + self.z_extends + 1,
                     self.material2, self.material2_type)
        mc.setBlocks(self.coords[0] + self.x_extends + 1, self.coords[1], self.coords[2] + self.z_extends + 1,
                     self.coords[0] + self.x_extends + 1, self.coords[1] + self.floors * 5, self.coords[2] + self.z_extends + 1,
                     self.material2, self.material2_type)
        mc.setBlocks(self.coords[0] + self.x_extends + 1, self.coords[1], self.coords[2] - 1,
                     self.coords[0] + self.x_extends + 1, self.coords[1] + self.floors * 5, self.coords[2] - 1,
                     self.material2, self.material2_type)

        mc.setBlocks(self.coords[0] - 1, self.coords[1] + 5, self.coords[2],
                     self.coords[0] - 1, self.coords[1] + 5, self.coords[2] + self.z_extends,
                     self.material2, self.material2_type + 8)
        
        mc.setBlocks(self.coords[0] + self.x_extends + 1, self.coords[1] + 5, self.coords[2],
                     self.coords[0] + self.x_extends + 1, self.coords[1] + 5, self.coords[2] + self.z_extends,
                     self.material2, self.material2_type + 8)
        
        mc.setBlocks(self.coords[0], self.coords[1] + 5, self.coords[2] - 1,
                     self.coords[0] + self.x_extends, self.coords[1] + 5, self.coords[2] - 1,
                     self.material2, self.material2_type + 4)
        
        mc.setBlocks(self.coords[0], self.coords[1] + 5, self.coords[2] + self.z_extends + 1,
                     self.coords[0] + self.x_extends, self.coords[1] + 5, self.coords[2] +self.z_extends + 1,
                     self.material2, self.material2_type + 4)
        if self.floors > 1:
            mc.setBlocks(self.coords[0] - 1, self.coords[1] + 10, self.coords[2],
                     self.coords[0] - 1, self.coords[1] + 10, self.coords[2] + self.z_extends,
                     self.material2, self.material2_type + 8)
        
            mc.setBlocks(self.coords[0] + self.x_extends + 1, self.coords[1] + 10, self.coords[2],
                         self.coords[0] + self.x_extends + 1, self.coords[1] + 10, self.coords[2] + self.z_extends,
                         self.material2, self.material2_type + 8)

            mc.setBlocks(self.coords[0], self.coords[1] + 10, self.coords[2] - 1,
                         self.coords[0] + self.x_extends, self.coords[1] + 10, self.coords[2] - 1,
                         self.material2, self.material2_type + 4)

            mc.setBlocks(self.coords[0], self.coords[1] + 10, self.coords[2] + self.z_extends + 1,
                         self.coords[0] + self.x_extends, self.coords[1] + 10, self.coords[2] +self.z_extends + 1,
                         self.material2, self.material2_type + 4)

    def generate_roof_g1(self):                                         #GENERATES ROOF
        if self.floors == 1:                                            #Roof gradient of 3 2/3
            self.point[1] = self.coords[1] + 5
        else:
            self.point[1] = self.coords[1] + 10
        fx = 0
        fy = 0
        y = 0
        main_length = self.z_extends + 3
        n = round(main_length / 26 * 3)
        last = 0

        for x in range((self.x_extends + 7 )// 2):
            fy = round(2 / 3 * fx)
            mc.setBlock(self.point[0] - 3 + fx, self.point[1] + fy, self.point[2] - 2, self.mat_4_2_block, self.mat_4_2_block_data)                                                     #SOUTH RAIL SIDE
            mc.setBlock(self.point[0] - 3 + fx, self.point[1] + fy, self.point[2] + self.z_extends + 2, self.mat_4_2_block, self.mat_4_2_block_data)                     
            mc.setBlock(self.point[0] + self.x_extends + 3 - fx, self.point[1] + fy, self.point[2] - 2, self.mat_4_2_block, self.mat_4_2_block_data)                                    #NORTH RAIL SIDE
            mc.setBlock(self.point[0] + self.x_extends + 3 - fx, self.point[1] + fy, self.point[2] + self.z_extends + 2, self.mat_4_2_block, self.mat_4_2_block_data)
            if fx % 3 == 0:
                mc.setBlocks(self.point[0] - 3 + fx, self.point[1] + fy, self.point[2] - 1,                                                                                             #SOUTH MAIN STAIRS
                             self.point[0] - 3 + fx, self.point[1] + fy, self.point[2] + self.z_extends + 1, self.mat_4_1_stairs)
                mc.setBlock((self.point[0] - 3 + fx, self.point[1] + 1 + fy, self.point[2] - 2, self.mat_4_2_slabs, self.mat_4_2_block_data))                                           #SOUTH RAIL SLABS
                mc.setBlock((self.point[0] - 3 + fx, self.point[1] - 1 + fy, self.point[2] - 2, self.mat_4_2_slabs, self.mat_4_2_block_data + 8))                        
                mc.setBlock((self.point[0] - 3 + fx, self.point[1] + 1 + fy, self.point[2] + self.z_extends + 2, self.mat_4_2_slabs, self.mat_4_2_block_data))                          #SOUTH RAIL
                mc.setBlock((self.point[0] - 3 + fx, self.point[1] - 1 + fy, self.point[2] + self.z_extends + 2, self.mat_4_2_slabs, self.mat_4_2_block_data + 8))       
                mc.setBlocks(self.point[0] + self.x_extends + 3 - fx, self.point[1] + fy, self.point[2] - 1,                                                                            #NORTH MAIN STAIRS
                             self.point[0] + self.x_extends + 3 - fx, self.point[1] + fy, self.point[2] + self.z_extends + 1, self.mat_4_1_stairs, 1)
                mc.setBlock((self.point[0] + self.x_extends + 3 - fx, self.point[1] + 1 + fy, self.point[2] - 2, self.mat_4_2_slabs, self.mat_4_2_block_data))                          #NORTH RAIL SLABS
                mc.setBlock((self.point[0] + self.x_extends + 3 - fx, self.point[1] - 1 + fy, self.point[2] - 2, self.mat_4_2_slabs, self.mat_4_2_block_data + 8))
                mc.setBlock((self.point[0] + self.x_extends + 3 - fx, self.point[1] + 1 + fy, self.point[2] + self.z_extends + 2, self.mat_4_2_slabs, self.mat_4_2_block_data))         #NORTH RAIL
                mc.setBlock((self.point[0] + self.x_extends + 3 - fx, self.point[1] - 1 + fy, self.point[2] + self.z_extends + 2, self.mat_4_2_slabs, self.mat_4_2_block_data + 8))
                last = 1

            elif (fx + 1) % 3 == 0:
                mc.setBlocks(self.point[0] - 3 + fx, self.point[1] + fy, self.point[2] - 1,                                                                                             #SOUTH MAIN BLOCKS
                             self.point[0] - 3 + fx, self.point[1] + fy, self.point[2] + self.z_extends + 1, self.mat_4_1_block, self.mat_4_1_block_data)
                mc.setBlock((self.point[0] - 3 + fx, self.point[1] + 1+ fy, self.point[2] - 2, self.mat_4_2_stairs))                                                                    #SOUTH RAIL
                mc.setBlock((self.point[0] - 3 + fx, self.point[1] + 1+ fy, self.point[2] + self.z_extends + 2, self.mat_4_2_stairs))           
                mc.setBlocks(self.point[0] + self.x_extends + 3 - fx, self.point[1] + fy, self.point[2] - 1,                                                                            #NORTH MAIN BLOCKS
                             self.point[0] + self.x_extends + 3 - fx, self.point[1] + fy, self.point[2] + self.z_extends + 1, self.mat_4_1_block, self.mat_4_1_block_data)
                mc.setBlock((self.point[0] + self.x_extends + 3 - fx, self.point[1] + 1+ fy, self.point[2] - 2, self.mat_4_2_stairs, 1))                                                #NORTH RAIL
                mc.setBlock((self.point[0] + self.x_extends + 3 - fx, self.point[1] + 1+ fy, self.point[2] + self.z_extends + 2, self.mat_4_2_stairs, 1))
                last = 2        
            elif (fx - 1) % 3 == 0:
                mc.setBlocks(self.point[0] - 3 + fx, self.point[1] + fy, self.point[2] - 1,                                                                                             #SOUTH MAIN SLABS
                             self.point[0] - 3 + fx, self.point[1] + fy, self.point[2] + self.z_extends + 1, self.mat_4_1_slabs, self.mat_4_1_block_data)
                mc.setBlocks(self.point[0] - 3 + fx, self.point[1] + fy, self.point[2] + (self.z_extends // 2) - n,                                                                     #SOUTH MAIN STAIRS (CENTER)
                             self.point[0] - 3 + fx, self.point[1] + fy, self.point[2] + (self.z_extends // 2) + n, self.mat_4_1_stairs)
                if ((self.z_extends // 2) - 1) > n:
                    n = n + 1
                mc.setBlock((self.point[0] - 3 + fx, self.point[1] - 1 + fy, self.point[2] - 2, self.mat_4_2_stairs, 5))                                                                #SOUTH RAIL
                mc.setBlock((self.point[0] - 3 + fx, self.point[1] - 1 + fy, self.point[2] + self.z_extends + 2, self.mat_4_2_stairs, 5))       
                mc.setBlocks(self.point[0] + self.x_extends + 3 - fx, self.point[1] + fy, self.point[2] - 1,                                                                            #NORTH MAIN SLABS
                             self.point[0] + self.x_extends + 3 - fx, self.point[1] + fy, self.point[2] + self.z_extends + 1, self.mat_4_1_slabs, self.mat_4_1_block_data)
                mc.setBlocks(self.point[0] + self.x_extends + 3 - fx, self.point[1] + fy, self.point[2] + (self.z_extends // 2) - n,                                                    #NORTH MAIN STAIRS (CENTER)
                             self.point[0] + self.x_extends + 3 - fx, self.point[1] + fy, self.point[2] + (self.z_extends // 2) + n, self.mat_4_1_stairs, 1)
                mc.setBlock((self.point[0] + self.x_extends + 3 - fx, self.point[1] - 1 + fy, self.point[2] - 2, self.mat_4_2_stairs, 4))                                               #NORTH RAIL
                mc.setBlock((self.point[0] + self.x_extends + 3 - fx, self.point[1] - 1 + fy, self.point[2] + self.z_extends + 2, self.mat_4_2_stairs, 4))  
                last = 3
            if fx > 2:
                mc.setBlock(self.point[0] + self.x_extends + 3 - fx, self.point[1] + fy - 1, self.point[2] - 1, self.material2, self.material2_type + 12)                                    #STRUCTURE (UNDER RAIL) NORTH
                mc.setBlock(self.point[0] + self.x_extends + 3 - fx, self.point[1] + fy - 1, self.point[2] + self.z_extends + 1, self.material2, self.material2_type + 12)
                mc.setBlock(self.point[0] + fx - 3, self.point[1] + fy - 1, self.point[2] - 1, self.material2, self.material2_type + 12)                                                     #STRUCTURE (UNDER RAIL) SOUTH
                mc.setBlock(self.point[0] + fx - 3, self.point[1] + fy - 1, self.point[2] + self.z_extends + 1, self.material2, self.material2_type + 12)
                mc.setBlocks(self.point[0] + fx - 3, self.point[1] + fy - 1, self.point[2],                                                                                             #WALL SOUTH
                             self.point[0] + fx - 3, self.point[1], self.point[2], self.material1, self.material1_type)                     
                mc.setBlocks(self.point[0] + fx - 3, self.point[1] + fy - 1, self.point[2] + self.z_extends,
                             self.point[0] + fx - 3, self.point[1], self.point[2] + self.z_extends, self.material1, self.material1_type)
                mc.setBlocks(self.point[0] + self.x_extends + 3 - fx, self.point[1], self.point[2],                                                                                     #WALL NORTH
                             self.point[0] + self.x_extends + 3 - fx, self.point[1] + fy - 1, self.point[2], self.material1, self.material1_type) 
                mc.setBlocks(self.point[0] + self.x_extends + 3 - fx, self.point[1], self.point[2] + self.z_extends,
                             self.point[0] + self.x_extends + 3 - fx, self.point[1] + fy - 1, self.point[2] + self.z_extends, self.material1, self.material1_type)
            fx += 1
        mc.setBlock(self.point[0] - 3, self.point[1] + 1, self.point[2] - 2, self.mat_4_2_stairs)                                                                                       #SOUTH SIDE RAILS
        mc.setBlock(self.point[0] - 3, self.point[1] + 1, self.point[2] + self.z_extends + 2, self.mat_4_2_stairs)
        mc.setBlock(self.point[0] - 2, self.point[1] + 1, self.point[2] + self.z_extends + 2, self.mat_4_2_block, self.mat_4_2_block_data)    
        mc.setBlock(self.point[0] - 2, self.point[1] + 1, self.point[2] +self.z_extends + 2, self.mat_4_2_block, self.mat_4_2_block_data)
        mc.setBlocks(self.point[0] - 3, self.point[1], self.point[2] - 1,
                     self.point[0] - 3, self.point[1], self.point[2] + self.z_extends + 1, self.mat_4_2_stairs)
        mc.setBlock(self.point[0] + self.x_extends + 3, self.point[1] + 1, self.point[2] - 2, self.mat_4_2_stairs, 1)                                                                   #NORTH SIDE RAILS
        mc.setBlock(self.point[0] + self.x_extends + 3, self.point[1] + 1, self.point[2] + self.z_extends + 2, self.mat_4_2_stairs, 1)
        mc.setBlock(self.point[0] + self.x_extends + 2, self.point[1] + 1, self.point[2] + self.z_extends + 2, self.mat_4_2_block, self.mat_4_2_block_data)    
        mc.setBlock(self.point[0] + self.x_extends + 2, self.point[1] + 1, self.point[2] +self.z_extends + 2, self.mat_4_2_block, self.mat_4_2_block_data)
        mc.setBlocks(self.point[0] + self.x_extends + 3, self.point[1], self.point[2] - 1,
                    self.point[0] + self.x_extends + 3, self.point[1], self.point[2] + self.z_extends + 1, self.mat_4_2_stairs, 1)
        mc.setBlocks(self.point[0] + self.x_extends // 2, self.point[1] + fy, self.point[2] - 2,
                      self.point[0] + (self.x_extends + 1) // 2, self.point[1] + fy, self.point[2] + self.z_extends + 2, self.mat_4_2_block, self.mat_4_2_block_data)
        mc.setBlocks(self.point[0] + self.x_extends // 2, self.point[1] + fy - 1, self.point[2] - 1,                                                                                    #STRUCTURE UNDER PEAK
                      self.point[0] + (self.x_extends + 1) / 2, self.point[1] + fy - 1, self.point[2] + self.z_extends + 1, self.material2, self.material2_type + 12)
        mc.setBlocks(self.point[0] + self.x_extends // 2, self.point[1] + fy - 2, self.point[2],                                                                                        #WALL (CENTER)
                      self.point[0] + (self.x_extends + 1) / 2, self.point[1], self.point[2], self.material1, self.material1_type)
        mc.setBlocks(self.point[0] + self.x_extends // 2, self.point[1] + fy - 2, self.point[2] + self.z_extends,                                            
                      self.point[0] + (self.x_extends + 1) / 2, self.point[1], self.point[2] + self.z_extends, self.material1, self.material1_type)
        if last != 2:
            mc.setBlocks(self.point[0] + self.x_extends // 2, self.point[1] + fy + 1, self.point[2] - 2,
                      self.point[0] + (self.x_extends + 1) / 2, self.point[1] + fy + 1, self.point[2] + self.z_extends + 2, self.mat_4_2_slabs, self.mat_4_2_block_data)
        else:
            mc.setBlocks(self.point[0] + self.x_extends // 2, self.point[1] + fy + 1, self.point[2] - 2,
                      self.point[0] + (self.x_extends + 1) / 2, self.point[1] + fy + 1, self.point[2] + self.z_extends + 2, self.mat_4_2_block, self.mat_4_2_block_data)
        if self.x_extends % 2 == 1:
            mc.setBlocks(self.point[0] + self.x_extends // 2, self.point[1] + fy + 1, self.point[2] - 2,
                      self.point[0] + self.x_extends // 2, self.point[1] + fy + 1, self.point[2] + self.z_extends + 2, self.mat_4_2_stairs)
            mc.setBlocks(self.point[0] + (self.x_extends + 1) / 2, self.point[1] + fy + 1, self.point[2] - 2,
                      self.point[0] + (self.x_extends + 1) / 2, self.point[1] + fy + 1, self.point[2] + self.z_extends + 2, self.mat_4_2_stairs, 1)

    def generate_rounded_roof(self):                            #Semi circle function implimented for even lenghth but hasnt been applied to roof
        x = 6300
        y = 113
        z = 508
        l = 20
        fx = - (l / 2)
        fy = 0
        prv_fy = 999

        mc.setBlock(x, y, z, 57)

        i = 0

        while i < l + 1:
            fy = round(sqrt((l/2)**2 - (fx)**2))
            mc.setBlock(x + fx, y + fy,z, 5)
            nxt_y = round(sqrt(abs((l/2)**2 - (fx + 1)**2)))
            if nxt_y > fy and fx < 0:
                mc.setBlocks(x + fx, y + fy, z,
                             x + fx, nxt_y -1 + y,z,
                             5)
                mc.setBlocks(x - fx, y + fy, z,
                             x - fx, nxt_y -1 + y,z,
                             5)
            prv_fy = fy
            fx += 1
            i += 1

    def generate_rooms(self):                                   #GENERATES A ROOM
        mc.setBlocks(self.coords[0] + 2, self.coords[1] + 1, self.coords[2] + 2,
                     self.coords[0] + self.x_extends - 2, self.coords[1] + 1, self.coords[2] + self.z_extends - 2, 171, self.carpet_c)
        self.recurse_floor_plan(self.x_extends, self.z_extends)
        if self.floors > 1:
            self.carpet_check = 1
            time.sleep(0.5)
            self.point[1] = self.point[1] + 5
            set_floor(self.point, self.x_extends, self.z_extends, self.material3, self.material3_type, self.material3_rotation)
            self.recurse_floor_plan(self.x_extends, self.z_extends)

    def load_house(self):                                       #LOADS THE HOUSES DIMENSIONS
        self.roll_house_border()
        self.roll_floors()
    def generate_border(self):                                  #GENETERATES THE SHELL OF THE HOUSE
        self.roll_materials()
        self.generate_house_border()
        self.roll_door()
    def generate_house(self):                                   #GENERATES HOUSE FROM COORDS
        self.set_ceiling()
        self.generate_rooms()
        self.generate_windows()
        self.set_main_door()
        self.set_stairs()
        self.generate_structural_support()
        self.generate_roof_g1()
    
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

def do_overlap(A, D, B, C):
    if A.x > C.x or B.x > D.x:
        return False
    if D.y > B.y or C.y > A.y:
        return False
    return True

class Village:
    def __init__(self, centre) -> None:
        self.center = list(centre)
        self.houses = []

    def generate_houses(self):
        i = 0
        while i < 5:
            self.generate_house()
            i += 1
        
    def generate_house(self):
        x = self.center[0] + random_int_gen(-60, 60)
        z = self.center[2] + random.randint(-60, 60)
        y = mc.getHeight(x, z)
        temp = positioning.find_ground_levels(x, x + 15, z, z + 15, 55, 130)
        y = temp[1]

        temp_house = House((x, y, z), (self.center))
        temp_house.load_house()
        can_spawn = True
        space = 9
        i = 0                                              #A __________        #B __________ 
                                                           # |          |       # |          |
        while i < len(self.houses):                        # |__________|D      # |__________|C
            A = Point(temp_house.coords[0] - space, temp_house.coords[2] + temp_house.z_extends + space)
            D = Point(temp_house.coords[0] + temp_house.x_extends + space, temp_house.coords[2] - space)
            B = Point(self.houses[i].coords[0] - space, self.houses[i].coords[2] + self.houses[i].z_extends + space)
            C = Point(self.houses[i].coords[0] + self.houses[i].x_extends + space, self.houses[i].coords[2] - space)
    
            if(do_overlap(A, D, B, C)):
                can_spawn = False
            i += 1
        
        if can_spawn:
            self.houses.append(temp_house)
            terraforming.terraform(temp_house.coords, temp_house.x_extends, temp_house.z_extends)
            temp_house.generate_border()
            temp_house.generate_house()

        else:            
            self.generate_house()

from mcpi.minecraft import Minecraft
from mcpi import block

mc = Minecraft.create()

import decoration

DEBUGGING = False

air_blocks = [0, 17, 18, 31, 32, 37, 38, 39, 40, 81, 83, 106, 127, 161, 162, 175]
liquids = [8, 9, 10, 11]

stair_orientation_ids = {
    'x': {
        1: 0,
        -1: 1,
    },

    'z': {
        1: 2,
        -1: 3,
    }
}

# Global lists
corner_paths = [] # (x, y, z, coordinate direction, goal, parent_path)
back_paths = []

blacklisted_house_dimensions = []


class Goal:
    def __init__(self, x, y, z, dimension, direction):
        self.x = x
        self.y = y
        self.z = z
        self.dimension = dimension
        self.direction = direction

class Goals:
    def __init__(self):
        self.goals = []

    def add(self, goal):
        self.goals.append(goal)

    # A method that finds and removes a goal from the goals list via its unique coordinates, (x, z)
    def find_and_remove(self, x, z):
        for i in range(len(self.goals)):
            if self.goals[i].x == x and self.goals[i].z == z:
                self.goals.pop(i)
                break
    
    def find(self, x, z):
        for goal in self.goals:
            if goal.x == x and goal.z == z:
                return True

        return False

    def clear(self):
        self.goals.clear()


class Path:
    def __init__(self, x, y, z, direction, width, parent_z_paths, parent_x_paths):
        self.x = x 
        self.y = y 
        self.z = z

        self.width = width
        self.length = 0

        self.direction = direction

        self.parent_z_paths = parent_z_paths
        self.parent_x_paths = parent_x_paths

        self.sub_paths = []


    def set_door_goal(self, goal: Goal):
        self.door_goal = goal


class x_Path(Path):
    def __init__(self, x, y, z, direction, width, main_x_goal, parent_z_paths = [], parent_x_paths = []):
        Path.__init__(self, x, y, z, direction, width, parent_z_paths, parent_x_paths)

        self.start_x = x
        self.main_x_goal = main_x_goal

        # A dictionary indicating the y-axis at the x-axis
        self.y_coords = {}

    # A function that checks if a sub-path will intersect a parent path.
    def check_if_intersection(self, sub_direction, goal_coord): 
        for parent_path in self.parent_x_paths:
            start_point = parent_path.start_x
            end_point = parent_path.main_x_goal
  
            if parent_path.direction == -1:
                temp = start_point
                start_point = end_point
                end_point = temp


            # Check if the current position is in between the 2 points.
            if start_point < self.x < end_point:
                
                # Check to see if the sub path's direction will go towards the parent path and cross it.
                if (sub_direction == 1 and self.z < parent_path.z and goal_coord > parent_path.z) or (sub_direction == -1 and self.z > parent_path.z and goal_coord < parent_path.z):
                    # Return True to indicate there will be an intersection.
                    return True
                
        return False


    # A method to check if there is a house 3 blocks ahead of a path's direction
    def check_for_obstruction(self):
        for i, (x_1, z_1, x_2, z_2, door_pos) in enumerate(blacklisted_house_dimensions):
            if self.door_goal != door_pos or door_pos.z != self.z or door_pos.direction == self.direction: # Ignore the house dimension blacklist if the path is generating towards the doorway

                
                # Check if the path is 3 blocks away from the house dimensions
                if (x_1 - 3 <= self.x <= x_2 + 3) and (z_1 - 3 <= self.z <= z_2 + 3):
                    return i

        return -1


    # A method that builds an alternate path route to a goal that is blocked by a house.
    def path_find(self, house_i):
        x_1, z_1, x_2, z_2, door_pos = blacklisted_house_dimensions[house_i]
        offset = int(self.width / 2)

        # Switch the points if the direction is negative
        if self.direction == -1:
            temp = x_2
            x_2 = x_1
            x_1 = temp

        # Check to see if the house of the path's goal is obstructing the path from reaching it
        if door_pos == self.door_goal:
            if DEBUGGING: mc.postToChat("x - goal house obstructed")

            if door_pos.dimension == 'z':
                z_side_goal = self.door_goal.z + (offset + 6) * self.door_goal.direction

                z_path_side = z_Path(self.x - (offset + 1) * self.direction, self.y, self.z + (offset + 1) * self.door_goal.direction, self.door_goal.direction, self.width, z_side_goal)
                z_path_side.set_door_goal(self.door_goal)
                
                self.sub_paths.append(z_path_side)

                z_path_side.build_z_path()

                x_path_up = x_Path(self.x, z_path_side.y, z_path_side.z - (offset + 1) * z_path_side.direction, self.direction, self.width, self.door_goal.x + (offset + 1) * self.direction)
                x_path_up.set_door_goal(self.door_goal)

                z_path_side.sub_paths.append(x_path_up)

                x_path_up.build_x_path()
            
            else:
                down_point = z_1 - 7
                z_path_down = z_Path(self.x - (offset + 1) * self.direction, self.y, self.z - (offset + 1), -1, self.width, down_point)
                z_path_down.set_door_goal(self.door_goal)

                self.sub_paths.append(z_path_down)

                z_path_down.build_z_path()

                right_point = x_2 + 7 * self.direction
                x_path_right = x_Path(z_path_down.x + (offset + 1) * self.direction, z_path_down.y, down_point + (offset + 1), self.direction, self.width, right_point)
                x_path_right.set_door_goal(self.door_goal)

                z_path_down.sub_paths.append(x_path_right)

                x_path_right.build_x_path()

                up_point = self.door_goal.z + (offset + 1)
                x_path_up = z_Path(right_point - (offset + 1) * self.direction, x_path_right.y, x_path_right.z + (offset + 1), 1, self.width, up_point)
                x_path_up.set_door_goal(self.door_goal)

                x_path_right.sub_paths.append(x_path_up)
                    
                x_path_up.build_z_path()
        else:
            # Check if dimension is the same as the goal
            if self.door_goal.dimension == 'x':

                # Check if goal is at the back of the house
                if z_1 - 4 <= self.door_goal.z <= z_2 + 4:
                    if DEBUGGING: mc.postToChat("x - Straight situation")
                    down_point = z_1 - 7
                    z_path_down = z_Path(self.x - (offset + 1) * self.direction, self.y, self.z - (offset + 1), -1, self.width, down_point)
                    z_path_down.set_door_goal(self.door_goal)

                    self.sub_paths.append(z_path_down)

                    z_path_down.build_z_path()

                    right_point = x_2 + 7 * self.direction
                    x_path_right = x_Path(z_path_down.x + (offset + 1) * self.direction, z_path_down.y, down_point + (offset + 1), self.direction, self.width, right_point)
                    x_path_right.set_door_goal(self.door_goal)

                    z_path_down.sub_paths.append(x_path_right)

                    x_path_right.build_x_path()

                    up_point = self.door_goal.z + (offset + 1)
                    x_path_up = z_Path(right_point - (offset + 1) * self.direction, x_path_right.y, x_path_right.z + (offset + 1), 1, self.width, up_point)
                    x_path_up.set_door_goal(self.door_goal)

                    x_path_right.sub_paths.append(x_path_up)

                    x_path_up.build_z_path()

                # Check if goal is on the left side of the house
                elif self.door_goal.z < z_1 - 4:
                    if DEBUGGING: mc.postToChat("x - Lefty")
                    down_point = self.door_goal.z - (offset + 1)
                    z_path_down = z_Path(self.x - (offset + 1), self.y, self.z - (offset + 1) * self.direction, -1, self.width, down_point)
                    z_path_down.set_door_goal(self.door_goal)
                    
                    self.sub_paths.append(z_path_down)

                    z_path_down.build_z_path()

                # Goal is on the right side of the house
                else:
                    if DEBUGGING: mc.postToChat("x - Righty")
                    up_point = self.door_goal.z + (offset + 1)
                    z_path_up = z_Path(self.x + (offset + 1), self.y, self.z - (offset + 1) * self.direction, 1, self.width, up_point)
                    z_path_up.set_door_goal(self.door_goal)

                    self.sub_paths.append(z_path_up)

                    z_path_up.build_z_path()


            else:
                # Check if goal is at the back of the house
                if (self.direction == 1 and self.door_goal.x > x_2 + 4 * self.direction) or (self.direction == -1 and self.door_goal.x < x_2 + 4 * self.direction):
                    if DEBUGGING: mc.postToChat("x - BACK")
                    down_point = z_1 - 7
                    
                    z_path_down = z_Path(self.x - (offset + 1) * self.direction, self.y, self.z - (offset + 1), -1, self.width, down_point)
                    z_path_down.set_door_goal(self.door_goal)

                    self.sub_paths.append(z_path_down)

                    z_path_down.build_z_path()

                    right_point = self.door_goal.x + (offset + 1) * self.direction
                    x_path_right = x_Path(z_path_down.x + (offset + 1) * self.direction, z_path_down.y, down_point + (offset + 1), self.direction, self.width, right_point)
                    x_path_right.set_door_goal(self.door_goal)

                    z_path_down.sub_paths.append(x_path_right)

                    x_path_right.build_x_path()

                # Check if goal is on the left side of the house
                elif self.door_goal.z < z_1 - 4:
                    if DEBUGGING: mc.postToChat("x - MID LEFT")
                    down_point = self.door_goal.z - (offset + 6)
                    z_path_down = z_Path(self.x - (offset + 1) * self.direction, self.y, self.z - (offset + 1), -1, self.width, down_point)
                    z_path_down.set_door_goal(self.door_goal)

                    self.sub_paths.append(z_path_down)

                    z_path_down.build_z_path()

                    right_point = self.door_goal.x + (offset + 1)
                    x_path_right = x_Path(z_path_down.x + (offset + 1) * self.direction, z_path_down.y, down_point + (offset + 1), self.direction, self.width, right_point)
                    x_path_right.set_door_goal(self.door_goal)

                    z_path_down.sub_paths.append(x_path_right)

                    x_path_right.build_x_path()            

                # Goal is on the right side of the house
                else:
                    if DEBUGGING: mc.postToChat("x - MID RIGHT")
                    up_point = self.door_goal.z - (offset + 2)
                    z_path_up = z_Path(self.x + (offset + 1) * -self.direction, self.y, self.z + (offset + 1), 1, self.width, up_point)
                    z_path_up.set_door_goal(self.door_goal)

                    self.sub_paths.append(z_path_up)

                    z_path_up.build_z_path()

                    right_point = self.door_goal.x + (offset + 1) * self.direction
                    x_path_right = x_Path(z_path_up.x + (offset + 1) * self.direction, z_path_up.y, up_point - (offset + 1), self.direction, self.width, right_point)
                    x_path_right.set_door_goal(self.door_goal)

                    z_path_up.sub_paths.append(x_path_right)

                    x_path_right.build_x_path()            


    # A method that builds staircases on steep terrain in the x-direction
    def build_stairs_x(self, x, y, z, direction):
        air_detected = False
        
        offset = int(self.width/2)
        blocks = mc.getBlocks(x, y, z - offset, x, y, z + offset)

        for hit_block in blocks:
            if hit_block in air_blocks:
                air_detected = True
                break


        if air_detected and x != self.main_x_goal:
            stair_orientation = stair_orientation_ids['x'][direction]
            mc.setBlocks(x, y, z - offset, x, y, z + offset, block.STAIRS_COBBLESTONE.id, stair_orientation)

            # Fill cobblestone base underneath stairs
            step_y = y - 1
            step_blocks = mc.getBlocks(x, step_y, z - offset, x, step_y, z + offset)
            base_air_detected = True

            while base_air_detected:
                base_air_detected = False

                for step_block in step_blocks:
                    if step_block in air_blocks or step_block == block.STAIRS_COBBLESTONE.id:
                        base_air_detected = True
                        break

                if base_air_detected:
                    mc.setBlocks(x, step_y, z - offset, x, step_y, z + offset, block.COBBLESTONE.id)

                    step_y = step_y - 1
                    step_blocks = mc.getBlocks(x, step_y, z - offset, x, step_y, z + offset)


            return self.build_stairs_x(x - direction, y - 1, z, direction)
        else:
            return y, x + direction

    
    # Builds a straight path in the x direction 
    def build_x_path(self):
        self.y_coords[self.x] = self.y

        if self.x == self.main_x_goal: # Base case 1: goal reached
            door_goals.find_and_remove(self.x, self.z) # Find and remove the reached goal from the list, preventing it from getting multiple paths.
            if DEBUGGING: mc.postToChat("[Paths]: Path goal in X direction reached!")

        else:
            house_i_obstructed = self.check_for_obstruction() 
            
            if house_i_obstructed != -1: # Base Case 2, path blocked by an object ahead
                self.path_find(house_i_obstructed)
            else:     
                # Continue generating path    
                direction = self.direction
                prev_y = self.y
                offset = int(self.width / 2)

                self.y, last_block = get_max_block_height(self.x, self.z - offset, self.x, self.z + offset, self.y, self.width)
                
                if last_block in liquids:
                    # build bridge
                    mc.setBlocks(self.x, self.y, self.z - offset, self.x, self.y, self.z + offset, block.WOOD_PLANKS.id)
                else:
                    mc.setBlocks(self.x, self.y, self.z - offset, self.x, self.y, self.z + offset, block.COBBLESTONE.id)

                # Get the greatest height change in the y-coordinate
                elevation = self.y - prev_y

                if elevation > 1:
                    # Build stairs uphill
                    self.build_stairs_x(self.x - direction, self.y, self.z, direction)
                elif elevation < -1:
                    # Build stairs downhill
                    self.y, self.x = self.build_stairs_x(self.x, self.y - elevation, self.z, -direction)

                branch_count = 0

                for goal in door_goals.goals[:]:
                    if self.x - offset * direction == goal.x:             
                        direction_z = determine_turn_direction(self.z, goal.z)

                        # Ensure this sub-path will not intersect a parent path that will already generate a path towards it.
                        if not self.check_if_intersection(direction_z, goal.z):

                            # Ensure the doorway will be facing the sub-path when it generates towards it.
                            if goal.dimension == 'z' and goal.direction != direction_z:
                                branch_count = branch_count + 1

                                # Create a sub path in the z direction
                                sub_path = z_Path(self.x - offset * direction, self.y, self.z + (offset + 1) * direction_z, direction_z, self.width, goal.z, self.parent_z_paths, self.parent_x_paths)
                                sub_path.parent_x_paths.append(self)
                                sub_path.set_door_goal(goal)
                                
                                self.sub_paths.append(sub_path)

                                sub_path.build_z_path()

                                # Check to make sure the sub-path did not find an alternate route to the goal
                                door_goal = self.door_goal

                                if not door_goals.find(door_goal.x, door_goal.z):
                                    return

                            elif goal.dimension =='x':
                                # Add the path to a list to potentially generate a corner pathway to the doorway after the recursion finishes in case an alternate pathway is found.
                                corner_paths.append(((self.x - offset * direction) + (offset + 4) * goal.direction, self.y, self.z + (offset + 1) * direction_z, 'z', goal, self))
                            else:
                                if DEBUGGING: mc.postToChat("back goal for x dimension added!")
                                back_paths.append((self.x - offset * direction, self.y, self.z + (offset + 1) * direction_z, 'z', goal, self))

                if branch_count == 0:
                    self.length = self.length + 1

                self.x = self.x + direction
                self.build_x_path()


    # A recursive method that spawns lamps in lamp base positions set by the path finding, if appropriate.
    def spawn_lamps(self):
        offset = int(self.width / 2)
        left_side = False

        for x in range(self.start_x + 7 * self.direction, self.x, 8 * self.direction):
            if x in self.y_coords.keys():
                y = self.y_coords[x] + 1
                z = None
                direction = None

                lamp_obstructed = False

                if left_side:
                    z = self.z + ((offset + 1) * self.direction)
                    direction = -self.direction

                else:
                    z = self.z + ((offset + 1) * -self.direction)
                    direction = self.direction

                # Ensure the glowstone block and the 2 blocks below it are air blocks
                for block in mc.getBlocks(x, y + 4, z, x, y + 4 - 3, z + direction):
                    if not block in air_blocks:
                        lamp_obstructed = True
                        break
                
                for sub_path in self.sub_paths:
                    if sub_path.x - offset <= x <= sub_path.x + offset:
                        lamp_obstructed = True
                        if DEBUGGING: mc.postToChat("lamp obstructed, not spawned.")

                if not lamp_obstructed:
                    new_lamp = decoration.Lamp(x, y, z)
                    new_lamp.build(direction, 'x')  

                left_side = not left_side

        for sub_path in self.sub_paths:
            sub_path.spawn_lamps()


    def get_path_intersections(self):
        intersections = []

        for sub_path in self.sub_paths:
            # Check to ensure the sub path is not on the very edge of the path
            if sub_path.x != self.main_x_goal - int(self.width / 2 + 1) * self.direction:
                if sub_path.x in self.y_coords.keys():
                    intersections.append((sub_path.x, self.y_coords[sub_path.x], self.z))
                
            intersections = intersections + sub_path.get_path_intersections()

        return intersections


class z_Path(Path):
    def __init__(self, x, y, z, direction, width, main_z_goal, parent_z_paths = [], parent_x_paths = []):
        Path.__init__(self, x, y, z, direction, width, parent_z_paths, parent_x_paths)

        self.start_z = z
        self.main_z_goal = main_z_goal

        # A dictionary indicating the y-axis at the z-axis
        self.y_coords = {}


    # A function that checks if a sub-path will intersect a parent path.
    def check_if_intersection(self, sub_direction, goal_coord): 
        for parent_path in self.parent_z_paths:
            start_point = parent_path.start_z
            end_point = parent_path.main_z_goal
  
            if parent_path.direction == -1:
                temp = start_point
                start_point = end_point
                end_point = temp


            # Check if the current position is in between the 2 points.
            if start_point < self.z < end_point:
                
                # Check to see if the sub path's direction will go towards the parent path and cross it.
                if (sub_direction == 1 and self.x < parent_path.x and goal_coord > parent_path.x) or (sub_direction == -1 and self.x > parent_path.x and goal_coord < parent_path.x):
                
                    # Return True to indicate there will be an intersection.
                    return True
                
        return False


    # A method that builds staircases on steep terrain in the z-direction.
    def build_stairs_z(self, x, y, z, direction):
        air_detected = False
        
        offset = int(self.width/2)
        blocks = mc.getBlocks(x - offset, y, z, x + offset, y, z)

        for hit_block in blocks:
            if hit_block in air_blocks:
                air_detected = True
                break


        if air_detected and z != self.main_z_goal:
            stair_orientation = stair_orientation_ids['z'][direction]
            mc.setBlocks(x - offset, y, z, x + offset, y, z, block.STAIRS_COBBLESTONE.id, stair_orientation)

            # Fill cobblestone base underneath stairs
            step_y = y - 1
            step_blocks = mc.getBlocks(x - offset, step_y, z, x + offset, step_y, z)
            base_air_detected = True

            while base_air_detected:
                base_air_detected = False

                for step_block in step_blocks:
                    if step_block in air_blocks or step_block == block.STAIRS_COBBLESTONE.id:
                        base_air_detected = True
                        break

                if base_air_detected:
                    mc.setBlocks(x - offset, step_y, z, x + offset, step_y, z, block.COBBLESTONE.id)

                    step_y = step_y - 1
                    step_blocks = mc.getBlocks(x - offset, step_y, z, x + offset, step_y, z)


            return self.build_stairs_z(x, y - 1, z - direction, direction)
        else:
            return y, z + direction


    # A method to check if there is a house 3 blocks ahead of a path's direction
    def check_for_obstruction(self):
        for i, (x_1, z_1, x_2, z_2, door_pos) in enumerate(blacklisted_house_dimensions):
            if self.door_goal != door_pos or door_pos.x != self.x or door_pos.direction == self.direction: # Ignore the house dimension blacklist if the path is generating towards the doorway

                # Check if the path is 3 blocks away from the house dimensions
                if (x_1 - 3 <= self.x <= x_2 + 3) and (z_1 - 3 <= self.z <= z_2 + 3):
                    return i

        return -1


    # A method that builds an alternate path route to a goal that is blocked by a house.
    def path_find(self, house_i):
        x_1, z_1, x_2, z_2, door_pos = blacklisted_house_dimensions[house_i]
        offset = int(self.width / 2)

        # Switch the points if the direction is negative
        if self.direction == -1:
            temp = z_2
            z_2 = z_1
            z_1 = temp

        # Check to see if the house of the path's goal is obstructing the path from reaching it
        if door_pos == self.door_goal:
            if DEBUGGING: mc.postToChat("z - goal house obstructed")
            
            if door_pos.dimension == 'x':
                x_side_goal = self.door_goal.x + (offset + 6) * self.door_goal.direction

                x_path_side = x_Path(self.x + (offset + 1) * self.door_goal.direction, self.y, self.z - (offset + 1) * self.direction, self.door_goal.direction, self.width, x_side_goal)
                x_path_side.set_door_goal(self.door_goal)

                self.sub_paths.append(x_path_side)

                x_path_side.build_x_path()

                z_path_up = z_Path(x_path_side.x - (offset + 1) * x_path_side.direction, x_path_side.y, self.z, self.direction, self.width, self.door_goal.z + (offset + 1) * self.direction)
                z_path_up.set_door_goal(self.door_goal)

                x_path_side.sub_paths.append(z_path_up)

                z_path_up.build_z_path()

            else:
                down_point = x_1 - 7
                x_path_down = x_Path(self.x - (offset + 1), self.y, self.z - (offset + 1) * self.direction, -1, self.width, down_point)
                x_path_down.set_door_goal(self.door_goal)

                self.sub_paths.append(x_path_down)
                
                x_path_down.build_x_path()

                right_point = z_2 + 7 * self.direction
                z_path_right = z_Path(down_point + (offset + 1), x_path_down.y, x_path_down.z + (offset + 1) * self.direction, self.direction, self.width, right_point)
                z_path_right.set_door_goal(self.door_goal)

                x_path_down.sub_paths.append(z_path_right)

                z_path_right.build_z_path()

                up_point = self.door_goal.x + (offset + 1)
                x_path_up = x_Path(z_path_right.x + (offset + 1), z_path_right.y, right_point - (offset + 1) * self.direction, 1, self.width, up_point)
                x_path_up.set_door_goal(self.door_goal)

                z_path_right.sub_paths.append(x_path_up)

                x_path_up.build_x_path()

        else:
            # Check if dimension is the same as the goal
            if self.door_goal.dimension == 'z':

                # Check if goal is at the back of the house
                if x_1 - 4 <= self.door_goal.x <= x_2 + 4:
                    if DEBUGGING: mc.postToChat("z - Straight situation")
                    down_point = x_1 - 7
                    x_path_down = x_Path(self.x - (offset + 1), self.y, self.z - (offset + 1) * self.direction, -1, self.width, down_point)
                    x_path_down.set_door_goal(self.door_goal)

                    self.sub_paths.append(x_path_down)

                    x_path_down.build_x_path()

                    right_point = z_2 + 7 * self.direction
                    z_path_right = z_Path(down_point + (offset + 1), x_path_down.y, x_path_down.z + (offset + 1) * self.direction, self.direction, self.width, right_point)
                    z_path_right.set_door_goal(self.door_goal)

                    x_path_down.sub_paths.append(z_path_right)

                    z_path_right.build_z_path()

                    up_point = self.door_goal.x + (offset + 1)
                    x_path_up = x_Path(z_path_right.x + (offset + 1), z_path_right.y, right_point - (offset + 1) * self.direction, 1, self.width, up_point)
                    x_path_up.set_door_goal(self.door_goal)

                    z_path_right.sub_paths.append(x_path_up)

                    x_path_up.build_x_path()

                # Check if goal is on the left side of the house
                elif self.door_goal.x < x_1 - 4:
                    if DEBUGGING: mc.postToChat("z - Lefty")
                    down_point = self.door_goal.x - (offset + 1)
                    x_path_down = x_Path(self.x - (offset + 1), self.y, self.z - (offset + 1) * self.direction, -1, self.width, down_point)
                    x_path_down.set_door_goal(self.door_goal)

                    self.sub_paths.append(x_path_down)

                    x_path_down.build_x_path()

                # Goal is on the right side of the house
                else:
                    if DEBUGGING: mc.postToChat("z - Righty")
                    up_point = self.door_goal.x + (offset + 1)
                    x_path_up = x_Path(self.x + (offset + 1), self.y, self.z - (offset + 1) * self.direction, 1, self.width, up_point)
                    x_path_up.set_door_goal(self.door_goal)

                    self.sub_paths.append(x_path_up)

                    x_path_up.build_x_path()


            else:
                # Check if goal is at the back of the house
                if (self.direction == 1 and self.door_goal.z > z_2 + 4 * self.direction) or (self.direction == -1 and self.door_goal.z < z_2 + 4 * self.direction):
                    if DEBUGGING: mc.postToChat("z - BACK")
                    down_point = x_1 - 7
                    x_path_down = x_Path(self.x - (offset + 1), self.y, self.z - (offset + 1) * self.direction, -1, self.width, down_point)
                    x_path_down.set_door_goal(self.door_goal)

                    self.sub_paths.append(x_path_down)

                    x_path_down.build_x_path()

                    right_point = self.door_goal.z + (offset + 1) * self.direction
                    z_path_right = z_Path(down_point + (offset + 1), x_path_down.y, x_path_down.z + (offset + 1) * self.direction, self.direction, self.width, right_point)
                    z_path_right.set_door_goal(self.door_goal)

                    x_path_down.sub_paths.append(z_path_right)

                    z_path_right.build_z_path()

                # Check if goal is on the left side of the house
                elif self.door_goal.x < x_1 - 4:
                    if DEBUGGING: mc.postToChat("z - MID LEFT")
                    down_point = self.door_goal.x + (offset + 2)
                    x_path_down = x_Path(self.x - (offset + 1), self.y, self.z - (offset + 1) * self.direction, -1, self.width, down_point)
                    x_path_down.set_door_goal(self.door_goal)

                    self.sub_paths.append(x_path_down)

                    x_path_down.build_x_path()

                    right_point = self.door_goal.z + (offset + 1)
                    z_path_right = z_Path(down_point + (offset + 1), x_path_down.y, x_path_down.z + (offset + 1) * self.direction, self.direction, self.width, right_point)
                    z_path_right.set_door_goal(self.door_goal)

                    x_path_down.sub_paths.append(z_path_right)

                    z_path_right.build_z_path()            

                # Goal is on the right side of the house
                else:
                    if DEBUGGING: mc.postToChat("z - MID RIGHT")
                    up_point = self.door_goal.x - (offset + 2)
                    x_path_up = x_Path(self.x + (offset + 1), self.y, self.z - (offset + 1) * self.direction, 1, self.width, up_point)
                    x_path_up.set_door_goal(self.door_goal)
                    x_path_up.build_x_path()

                    self.sub_paths.append(x_path_up)

                    right_point = self.door_goal.z + (offset + 1)
                    z_path_right = z_Path(up_point - (offset + 1), x_path_up.y, x_path_up.z + (offset + 1) * self.direction, self.direction, self.width, right_point)
                    z_path_right.set_door_goal(self.door_goal)

                    x_path_up.sub_paths.append(z_path_right)

                    z_path_right.build_z_path()            


    # Builds a straight path in the z direction 
    def build_z_path(self):
        self.y_coords[self.z] = self.y

        if self.z == self.main_z_goal: # Base Case 1: goal reached
            door_goals.find_and_remove(self.x, self.z) # Find and remove the reached goal from the list, preventing it from getting multiple paths.
            if DEBUGGING: mc.postToChat("[Paths]: Path goal in Z direction reached!")
        
        else:
            house_i_obstructed = self.check_for_obstruction() # Base Case 2, path blocked by an object ahead
            
            if house_i_obstructed != -1:
                self.path_find(house_i_obstructed)
            else:
                # Continue generating path
                direction = self.direction
                prev_y = self.y
                offset = int(self.width / 2)

                self.y, last_block = get_max_block_height(self.x - offset, self.z, self.x + offset, self.z, self.y, self.width)
                
                if last_block in liquids:
                    # build bridge
                    mc.setBlocks(self.x - offset, self.y, self.z, self.x + offset, self.y, self.z, block.WOOD_PLANKS.id)
                else:
                    mc.setBlocks(self.x - offset, self.y, self.z, self.x + offset, self.y, self.z, block.COBBLESTONE.id)

                
                # Get the greatest height change in the y-coordinate
                elevation = self.y - prev_y

                if elevation > 1:
                    # Build stairs uphill
                    self.build_stairs_z(self.x, self.y, self.z - direction, direction)
                elif elevation < -1:
                    # Build stairs downhill
                    self.y, self.z = self.build_stairs_z(self.x, self.y - elevation, self.z, -direction)

                branch_count = 0

                for goal in door_goals.goals[:]:
                    if self.z - direction * offset == goal.z: 
                        direction_x = determine_turn_direction(self.x, goal.x)

                        # Ensure this sub-path will not intersect a parent path that will already generate a path towards it.
                        if not self.check_if_intersection(direction_x, goal.x):
                        
                            # Ensure the doorway will be facing the sub-path when it generates towards it.
                            if goal.dimension == 'x' and goal.direction != direction_x:
                                branch_count = branch_count + 1

                                # Create a sub path in the x direction
                                sub_path = x_Path(self.x + (offset + 1) * direction_x, self.y, self.z - direction * offset, direction_x, self.width, goal.x, self.parent_z_paths, self.parent_x_paths)
                                sub_path.parent_z_paths.append(self)
                                sub_path.set_door_goal(goal)

                                self.sub_paths.append(sub_path)

                                sub_path.build_x_path()
                                
                                # Check to make sure a sub-path of the sub-path did not find an alternate route to the goal
                                door_goal = self.door_goal

                                if not door_goals.find(door_goal.x, door_goal.z):
                                    return

                            elif goal.dimension == 'z':
                                # Add the path to a list to potentially generate a corner pathway to the doorway after the recursion finishes in case an alternate pathway is found.
                                corner_paths.append((self.x + (offset + 1) * direction_x, self.y, (self.z - direction * offset) + (offset + 4) * goal.direction, 'x', goal, self))
                            else:
                                if DEBUGGING: mc.postToChat("back goal for z dimension added!")
                                # Goal is on the opposite side of the house
                                back_paths.append((self.x + (offset + 1) * direction_x, self.y, (self.z - direction * offset), 'x', goal, self))

                if branch_count == 0:
                    self.length = self.length + 1

                self.z = self.z + direction
                self.build_z_path()


    # A recursive method that spawns lamps in lamp base positions set by the path finding, if appropriate.
    def spawn_lamps(self):
        offset = int(self.width / 2)
        left_side = False

        for z in range(self.start_z + 7 * self.direction, self.z, 8 * self.direction):
            if z in self.y_coords.keys():
                y = self.y_coords[z] + 1
                x = None
                direction = None

                lamp_obstructed = False

                if left_side:
                    x = self.x + (offset + 1) * self.direction
                    direction = -self.direction

                else:
                    x = self.x + (offset + 1) * -self.direction
                    direction = self.direction

                for block in mc.getBlocks(x, y + 4, z, x + direction, y + 4 - 3, z):
                    if not block in air_blocks:
                        lamp_obstructed = True

                for sub_path in self.sub_paths:
                    #mc.setBlock(x, y + 2, sub_path.z - offset, 7)
                    #mc.setBlock(x, y + 2, sub_path.z + offset, 7)
                    if sub_path.z - offset <= z <= sub_path.z + offset:
                        lamp_obstructed = True
                        if DEBUGGING: mc.postToChat("lamp obstructed, not spawned.")

                if not lamp_obstructed:
                    new_lamp = decoration.Lamp(x, y, z)
                    new_lamp.build(direction, 'z')  

                left_side = not left_side     

        for sub_path in self.sub_paths:
            sub_path.spawn_lamps()


    def get_path_intersections(self):
        intersections = []

        for sub_path in self.sub_paths:
            # Check to ensure the sub path is not on the very edge of the path
            if sub_path.z != self.main_z_goal - int(self.width / 2 + 1) * self.direction:
                if sub_path.z in self.y_coords.keys():
                    intersections.append((self.x, self.y_coords[sub_path.z], sub_path.z))
                
            intersections = intersections + sub_path.get_path_intersections()

        return intersections

door_goals = Goals()


# A method that spawns a random central decoration at branching paths.
def spawn_central_decorations(base_path):
    from random import randint

    intersection_positions = base_path.get_path_intersections()

    chosen_intersections = []

    for intersection in intersection_positions:
        can_spawn = True
        x, y, z = intersection

        # Check to make sure the central decoration will not spawn in a house
        for blacklisted_house_dim in blacklisted_house_dimensions:
            x_1, z_1, x_2, z_2, _ = blacklisted_house_dim

            # Check x
            if (x_1 <= x - 5 <= x_2) or (x_1 <= x + 5 <= x_2):
                # Check z
                if (z_1 <= z - 5 <= z_2) or (z_1 <= z + 5 <= z_2):
                    can_spawn = False
                    break
        
        # Check to ensure the central decoration is not too close to other central decorations.
        for c_intersection in chosen_intersections:
            if abs(c_intersection[0] - x) <= 10 and abs(c_intersection[2] - z) <= 10:
                can_spawn = False
                break

        if can_spawn:
            chosen_intersections.append((x, y, z))

    # Randomly choose the starting central decoration
    next_decoration = randint(0, 1)

    for c_intersection in chosen_intersections:
        x, y, z = c_intersection
        next_decoration = next_decoration + 1

        if next_decoration == 1:
            new_fountain = decoration.Fountain(x, y, z)
            new_fountain.build()

        elif next_decoration == 2:
            new_well = decoration.Well(x, y, z)
            new_well.build()
            next_decoration = 0

# A function that returns the direction from the given coordinate to the goal coordinate, represented as positive or negative.
def determine_turn_direction(curr_coordinate, goal_coordinate):
    if curr_coordinate < goal_coordinate:
        return 1
    else:
        return -1

# A function that determines the maximum height a block can be placed that is not air.
def get_max_block_height(min_x, min_z, max_x, max_z, curr_y, width):
    blocks = mc.getBlocks(min_x, curr_y + 1, min_z, max_x, curr_y + 1, max_z)
    blocks_in_air = 0

    # Find the highest non-air block in the same dimension
    while blocks_in_air < width:
        blocks_in_air = 0

        for block in blocks:
            if block in air_blocks:
                blocks_in_air = blocks_in_air + 1

        if blocks_in_air < width:
            curr_y = curr_y + 1
            blocks = mc.getBlocks(min_x, curr_y + 1, min_z, max_x, curr_y + 1, max_z)


    # Find the first non-air block while going downwards

    block_not_in_air_found = False
    blocks = mc.getBlocks(min_x, curr_y, min_z, max_x, curr_y, max_z)

    last_non_air_block_detected = None

    while not block_not_in_air_found:
        for block in blocks:
            if block not in air_blocks:
                block_not_in_air_found = True
                last_non_air_block_detected = block
                break

        if not block_not_in_air_found:
            curr_y = curr_y - 1
            blocks = mc.getBlocks(min_x, curr_y, min_z, max_x, curr_y, max_z)
        
    return curr_y, last_non_air_block_detected # Return y to indicate the new y-coordinate. This drastically improves the efficiency of this method the next time it is called.
    

# A function that finds the lowest starting point in the z-dimension
def get_min_z_coordinate():
    smallest_goal = door_goals.goals[0]

    for goal_i in range(1, len(door_goals.goals)):
        if door_goals.goals[goal_i].z < smallest_goal.z:
            smallest_goal = door_goals.goals[goal_i]

    return smallest_goal

# A function that finds the highest starting point in the z-dimension
def get_max_z_coordinate():
    highest_goal = door_goals.goals[0]

    for goal_i in range(1, len(door_goals.goals)):
        if door_goals.goals[goal_i].z > highest_goal.z:
            highest_goal = door_goals.goals[goal_i]

    return highest_goal



# Main initalisation method that generates paths to all doorways (goals).
def generate_paths(houses, width):
    if houses != None:
        for house in houses:
            goal_x = int(house.door_coords[0])
            goal_y = int(house.door_coords[1])
            goal_z = int(house.door_coords[2])

            dimension = house.dimension
            direction = house.direction

            new_goal = Goal(goal_x, goal_y, goal_z, house.dimension, house.direction)
            door_goals.add(new_goal)

            base_pos_x = int(house.coords[0])
            base_pos_y = int(house.coords[1])
            base_pos_z = int(house.coords[2])

            if dimension == 'x': 
                x_1 = base_pos_x
                z_1 = base_pos_z
                x_2 = base_pos_x + house.x_extends
                z_2 = base_pos_z + house.z_extends 

                blacklisted_dimension = (x_1, z_1, x_2, z_2, new_goal)
                blacklisted_house_dimensions.append(blacklisted_dimension)

                #mc.setBlocks(blacklisted_dimension[0], base_pos_y + 30, blacklisted_dimension[1],
                #blacklisted_dimension[2], base_pos_y + 30, blacklisted_dimension[3],
                #block.WOOL.id)
            else:
                x_1 = base_pos_x
                z_1 = base_pos_z
                x_2 = base_pos_x + house.x_extends
                z_2 = base_pos_z + house.z_extends

                blacklisted_dimension = (x_1, z_1, x_2, z_2, new_goal)
                blacklisted_house_dimensions.append(blacklisted_dimension)

                #mc.setBlocks(blacklisted_dimension[0], base_pos_y + 30, blacklisted_dimension[1],
                #blacklisted_dimension[2], base_pos_y + 30, blacklisted_dimension[3],block.WOOL.id)

            #mc.setBlock(base_pos_x, base_pos_y + 30, base_pos_z, block.DIAMOND_BLOCK.id)

        house_count = len(houses)
    else:
        house_count = len(door_goals.goals)


    start_point = get_min_z_coordinate()
    finish_point = get_max_z_coordinate()

    # Temporarily remove the start house's blacklisted dimension so a path can be generated outwards of it.
    start_house_dimension = None

    for i in range(len(blacklisted_house_dimensions)):
        house = blacklisted_house_dimensions[i]

        if house[4].x == start_point.x and house[4].z == start_point.z:
            start_house_dimension = blacklisted_house_dimensions.pop(i)
            break

    door_goals.find_and_remove(start_point.x, start_point.z)
    if DEBUGGING: mc.postToChat("[Paths]: Generating path...")

    offset = int(width / 2)

    base_path = None

    
    # Determine suitable path structure based on start and finish point
    if start_point.dimension == 'z' and start_point.direction == -1:
        # Start position is facing away from the finish point in the z-dimension

        base_path = z_Path(start_point.x, start_point.y, start_point.z - 1, -1, width, start_point.z - (offset + 6))
        base_path.set_door_goal(finish_point)
        base_path.build_z_path()

        blacklisted_house_dimensions.append(start_house_dimension)

        # Reverse path
        base_path.direction = 1
        base_path.z = base_path.z + 4
        base_path.path_find(-1)

    elif start_point.dimension == 'x' and ((start_point.direction == 1 and finish_point.x < start_point.x) or (start_point.direction == -1 and finish_point.x > start_point.x)):
        # Start position is facing away from the finish point in the x-dimension

        base_path = x_Path(start_point.x + start_point.direction, start_point.y, start_point.z, start_point.direction, width, start_point.x + (offset + 6) * start_point.direction)
        base_path.set_door_goal(finish_point)
        base_path.build_x_path()

        blacklisted_house_dimensions.append(start_house_dimension)

        # Reverse path
        base_path.direction = -start_point.direction
        base_path.x = base_path.x + 4 * base_path.direction
        base_path.path_find(-1)

    elif finish_point.dimension != start_point.dimension: 
        if DEBUGGING: mc.postToChat("Different direction sit")
        # Start point and End point are facing different dimensions

        if start_point.dimension == 'z':
            # Start point is facing the z dimension. Therefore, the path generation will be initalised with a z-direction path

            direction = determine_turn_direction(start_point.z, finish_point.z)
            base_path = z_Path(start_point.x, start_point.y, start_point.z + 1 * direction, direction, width, finish_point.z + (offset + 1) * direction)
            base_path.set_door_goal(finish_point)

            base_path.build_z_path()
        else:
            # Start point is facing the x dimension. Therefore, the path generation will be initalised with an x-direction path

            direction = determine_turn_direction(start_point.x, finish_point.x)
            base_path = x_Path(start_point.x + 1 * direction, start_point.y, start_point.z, direction, width, finish_point.x + (offset + 1) * direction)
            base_path.set_door_goal(finish_point)

            base_path.build_x_path()

    else:
        # Start point and End point are facing the same dimension
        if start_point.dimension == 'z':

            if start_point.x == finish_point.x: 
                if DEBUGGING: mc.postToChat("Same Dimension")
                # Start point and finish point are in-line, therefore just generate a straight forward path

                direction = determine_turn_direction(start_point.z, finish_point.z)
                base_path = z_Path(start_point.x, start_point.y, start_point.z + 1 * direction, direction, width, finish_point.z)
                base_path.set_door_goal(finish_point)

                base_path.build_z_path()
            else:
                # Finish point is offset from the start point. Thus, a zig-zag path is required to connect the start to the end.
                if DEBUGGING: mc.postToChat("OFFSET")

                mid_point = (start_point.z + finish_point.z) // 2

                if DEBUGGING: mc.postToChat(f"GOING TO z = {mid_point + (offset + 1)}")

                z_direction = determine_turn_direction(start_point.z, finish_point.z)
                base_path = z_Path(start_point.x, start_point.y, start_point.z + 1 * z_direction, z_direction, width, mid_point + (offset + 1))
                base_path.set_door_goal(finish_point)

                base_path.build_z_path()

                # Check to ensure an alternate route to the finish point was not found by a sub-path
                if door_goals.find(finish_point.x, finish_point.z):
                    x_direction = determine_turn_direction(start_point.x, finish_point.x)
                    path = x_Path(start_point.x + (offset + 1) * x_direction, start_point.y, mid_point, x_direction, width, finish_point.x + (offset + 1) * x_direction)
                    path.set_door_goal(finish_point)

                    base_path.sub_paths.append(path)

                    path.build_x_path()

        # Start point and end point are both facing the x-dimension
        else:
            if start_point.z == finish_point.z: 
                if DEBUGGING: mc.postToChat("Same Dimension for x")
                # Start point and finish point are in-line, therefore just generate a straight forward path

                direction = determine_turn_direction(start_point.x, finish_point.x)

                if DEBUGGING: mc.postToChat(finish_point.x)
                base_path = x_Path(start_point.x + direction, start_point.y, start_point.z, direction, width, finish_point.x)
                base_path.set_door_goal(finish_point)

                base_path.build_x_path()
            else:
                # Finish point is offset from the start point. Thus, a zig-zag path is required to connect the start to the end.
                if DEBUGGING: mc.postToChat("OFFSET")

                mid_point = (start_point.x + finish_point.x) // 2
                if DEBUGGING: mc.postToChat(f"GOING TO x = {mid_point + (offset + 1)}")

                x_direction = determine_turn_direction(start_point.x, finish_point.x)
                base_path = x_Path(start_point.x + x_direction, start_point.y, start_point.z, x_direction, width, mid_point + (offset + 1) * x_direction)
                base_path.set_door_goal(finish_point)

                base_path.build_x_path()

                # Check to ensure an alternate route to the finish point was not found by a sub-path
                if door_goals.find(finish_point.x, finish_point.z):
                    z_direction = determine_turn_direction(start_point.z, finish_point.z)
                    path = z_Path(mid_point, start_point.y, start_point.z + (offset + 1) * z_direction, z_direction, width, finish_point.z + (offset + 1) * z_direction)
                    path.set_door_goal(finish_point)

                    base_path.sub_paths.append(path)

                    path.build_z_path()

    # Generate back paths if necessary
    for x, y, z, coordinate, goal, parent_path in back_paths:
        if DEBUGGING: mc.postToChat(f"back goal located at {goal.x}, {goal.y}, {goal.z}")

        if goal in door_goals.goals:
            if coordinate == 'x':
                if DEBUGGING: mc.postToChat("building back path to Goal in x dimension")
                direction = determine_turn_direction(x, goal.x)
                path = x_Path(x, y, z, direction, width, goal.x + (offset + 1) * direction)
                path.set_door_goal(goal)

                parent_path.sub_paths.append(path)

                path.build_x_path()
            else:
                if DEBUGGING: mc.postToChat("building back path to Goal in z dimension")
                direction = determine_turn_direction(z, goal.z)
                path = z_Path(x, y, z, direction, width, goal.z + (offset + 1) * direction)
                path.set_door_goal(goal)

                parent_path.sub_paths.append(path)

                path.build_z_path()
            door_goals.find_and_remove(x, z)
        else:
            if DEBUGGING: mc.postToChat("goal not in goals list")


    # Generate corner paths to goals that could not get a linear path to it.
    for x, y, z, coordinate, goal, parent_path in corner_paths:
        if goal in door_goals.goals:
            if coordinate == 'x':
                direction = determine_turn_direction(x, goal.x)
                path = x_Path(x, y, z, direction, width, goal.x + (offset + 1) * direction)
                path.set_door_goal(goal)

                parent_path.sub_paths.append(path)

                path.build_x_path()
            else:
                direction = determine_turn_direction(z, goal.z)
                path = z_Path(x, y, z, direction, width, goal.z + (offset + 1) * direction)
                path.set_door_goal(goal)

                parent_path.sub_paths.append(path)

                path.build_z_path()
            door_goals.find_and_remove(x, z)

    # Spawn in lamps after paths have finished generating.
    base_path.spawn_lamps()

    # Spawn decorations at path branches
    spawn_central_decorations(base_path)

    corner_paths.clear()
    back_paths.clear()

    blacklisted_house_dimensions.clear()
    
    if DEBUGGING: mc.postToChat("[Paths]: Finished generating path")



###-------------- CODE BELOW ONLY USED FOR DEBUGGING --------------###



# Temporary methods to test door facing direction
def build_z_facing_doorway(base_pos, z_direction):
    # left side
    mc.setBlocks(base_pos.x + 1, base_pos.y + 1, base_pos.z,
                 base_pos.x + 10, base_pos.y + 1, base_pos.z + 1 * z_direction, block.WOOD_PLANKS)

    # right side
    mc.setBlocks(base_pos.x - 1, base_pos.y + 1, base_pos.z,
                base_pos.x - 10, base_pos.y + 1, base_pos.z + 1 * z_direction, block.WOOD_PLANKS)

    # back block
    mc.setBlocks(base_pos.x - 10, base_pos.y + 1, base_pos.z + 1 * z_direction,
                base_pos.x + 10, base_pos.y + 1, base_pos.z + 10* z_direction, block.WOOD_PLANKS)

    x_1 = base_pos.x - 10
    z_1 = base_pos.z
    x_2 = base_pos.x + 10
    z_2 = base_pos.z + 10 * z_direction

    if z_2 < z_1:
        temp = z_2
        z_2 = z_1
        z_1 = temp
    
    blacklisted_dimension = (x_1, z_1, x_2, z_2, base_pos)
    blacklisted_house_dimensions.append(blacklisted_dimension)


def build_x_facing_doorway(base_pos, x_direction):
    # left side
    mc.setBlocks(base_pos.x, base_pos.y + 1, base_pos.z + 1,
                 base_pos.x + 1 * x_direction, base_pos.y + 1, base_pos.z + 10, block.WOOD_PLANKS)

    # right side
    mc.setBlocks(base_pos.x, base_pos.y + 1, base_pos.z- 1,
                base_pos.x + 1 * x_direction, base_pos.y + 1, base_pos.z - 10, block.WOOD_PLANKS)

    # back block
    mc.setBlocks(base_pos.x + 1 * x_direction, base_pos.y + 1, base_pos.z - 10,
                base_pos.x + 10 * x_direction, base_pos.y + 1, base_pos.z + 10, block.WOOD_PLANKS)


    x_1 = base_pos.x
    z_1 = base_pos.z - 10
    x_2 = base_pos.x + 10 * x_direction
    z_2 = base_pos.z + 10 


    if x_2 < x_1:
        temp = x_2
        x_2 = x_1
        x_1 = temp


    blacklisted_dimension = (x_1, z_1, x_2, z_2, base_pos)
    blacklisted_house_dimensions.append(blacklisted_dimension)

DISABLED = True

if not DEBUGGING and not DISABLED:
    import houses
    
    player_pos = mc.player.getTilePos()
    Village1 = houses.Village((player_pos.x, 3, player_pos.z))


    i = 0
    while i < 5:
        Village1.generate_house()
        i += 1

    generate_paths(Village1.houses, 3)

# Temporary loop for testing and debugging the path finding
while DEBUGGING: 
    blocksHit = mc.events.pollBlockHits()
    chatEvents = mc.events.pollChatPosts()

    for message in chatEvents:
        if message.message=='start':
            generate_paths(None, 3)
            door_goals.clear()

        elif message.message=='clear':
            door_goals.clear()
            if DEBUGGING: mc.postToChat("[Paths]: All goal points have been cleared")
        elif message.message =='pop':
            door_goals.goals.pop()
            if DEBUGGING: mc.postToChat("[Paths]: Removed last goal!")


    for hitBlock in blocksHit:
        goal_point = None
        player_rotation = mc.player.getRotation()

        if player_rotation > 90 - 45 and player_rotation <= 90 + 45:
            goal_point = Goal(hitBlock.pos.x, hitBlock.pos.y, hitBlock.pos.z, 'x', 1)
            build_x_facing_doorway(goal_point, -1)

        elif player_rotation > 180 - 45 and player_rotation <= 180 + 45:
            goal_point = Goal(hitBlock.pos.x, hitBlock.pos.y, hitBlock.pos.z, 'z', 1)
            build_z_facing_doorway(goal_point, -1)

        elif player_rotation > 270 - 45 and player_rotation <= 270 + 45:

            goal_point = Goal(hitBlock.pos.x, hitBlock.pos.y, hitBlock.pos.z, 'x', -1)
            build_x_facing_doorway(goal_point, 1)

        else:
            goal_point = Goal(hitBlock.pos.x, hitBlock.pos.y, hitBlock.pos.z, 'z', -1)
            build_z_facing_doorway(goal_point, 1)

        door_goals.add(goal_point)

        mc.setBlock(hitBlock.pos.x, hitBlock.pos.y, hitBlock.pos.z, block.GOLD_BLOCK.id)
        if DEBUGGING: mc.postToChat("[Paths]: Goal Added!")
        break
from mcpi.minecraft import Minecraft
import numpy as np

tree_blocks = (18, 106, 127, 161, 473) #Leaves, as well as vines, cocoa beans
log_blocks = (17, 162) #Logs

mc = Minecraft.create()

def remove_tree(x: int, y: int, z: int) -> bool:
    """
    Arguments:
        x (int): x coordinate of a log or tree block
        y (int): y coordinate of a log or tree block
        z (int): z coordinate of a log or tree block
        
    Returns:
        success (bool): Whether the function removed a tree
    """   

    block = mc.getBlock(x, y, z)
  
    #Find log from tree block
    if block in tree_blocks: 
        x, y, z = find_trunk(x, y, z)

        #If log is not found
        if y < 0:
            return False
        else:
            block = mc.getBlock(x, y, z)

    #Check if block is valid
    if block in log_blocks: 
        remove_connected_logs(x, y, z)
        #Leaves will disintegrate naturally with no nearby logs
        return True
    else:
        return False


def find_trunk(x, y, z):
    """
        Arguments:
            x (int): x coordinate of a tree block (e.g. a leaf block)
            y (int): y coordinate of a tree block (e.g. a leaf block)
            z (int): z coordinate of a tree block (e.g. a leaf block)
            
        Returns:
            x (int): x coordinate of a log block
            y (int): y coordinate of a log block
            z (int): z coordinate of a log block

        Note:
            If log is not found within reasonable range, -1 is returned as y
        """   

    trunk_found = False
    extension = 1

    while not trunk_found and extension < 10:
        diameter = extension * 2 + 1
        blocks_list = list(mc.getBlocks(x - extension, y - extension, z - extension, x + extension, y + extension, z + extension))
        blocks_matrix = np.reshape(blocks_list, (diameter, diameter, diameter))
        
        for target_y in range (0, diameter):
            for target_x in range (0, diameter):
                for target_z in range (0, diameter):
                    if blocks_matrix[target_y][target_x][target_z] in log_blocks:
                        trunk_found = True
                        break
                if trunk_found: break
            if trunk_found: break
        
        extension += 1
    
    if trunk_found:
        return target_x + x - extension + 1, target_y + y - extension + 1, target_z + z - extension + 1
    else:
        return -1, -1, -1

#Recursive algorithm to remove all logs connected to a target
def remove_connected_logs(x: int, y: int, z: int) -> None:
    """
        Arguments:
            x (int): x coordinate of a log
            y (int): y coordinate of a log
            z (int): z coordinate of a log
            
        Returns:
            None

        Note: 
            This is a recursive function
        """    

    blocks_list = list(mc.getBlocks(x - 1, y - 1, z - 1, x + 1, y + 1, z + 1))
    blocks_matrix = np.reshape(blocks_list, (3, 3, 3))

    #Find logs within 1 block cubic range of log and remove it
    #Then search for logs in within 1 block cubic range of it and repeat
    for target_y in range (0, 3):
        for target_x in range (0, 3):
            for target_z in range (0, 3):
                if blocks_matrix[target_y][target_x][target_z] in log_blocks and not (target_x + (x - 1) == x and target_y + (y - 1) == y and target_z + (z - 1) == z):
                    mc.setBlock(target_x + (x - 1), target_y + (y - 1), target_z + (z - 1), 0)
                    remove_connected_logs(target_x + (x - 1), target_y + (y - 1), target_z + (z - 1))
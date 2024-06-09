from mcpi.minecraft import Minecraft
import numpy as np

mc = Minecraft.create()

air_blocks = [0, 8, 9, 10, 11, 17, 18, 31, 32, 37, 38, 39, 40, 81, 83, 106, 127, 161, 162, 175] #Blocks to be treated as air (e.g. flowers, leaves, water, cactus)
fluid_blocks = [8, 9, 10, 11] #Fluids, including water, flowing water, lava, flowing lava
ground_blocks = [1, 2, 3, 12, 13, 80] #Blocks viewed as terrain
house_blocks = [4, 5, 44, 45, 53, 89, 98, 108, 112, 114, 126, 134, 135, 155, 156, 164] #Blocks used in houses

CHUNK_LENGTH = 16 #chunks are (vertical) square prisms

def find_ground_levels(x0: int, x1: int, z0: int, z1: int, y0 = 0, y1 = 255, ignore_house = True) -> 'tuple[int, int]':
    """
        Arguments:
            x0 (int): First x coordinate
            x1 (int): Second x coordinate
            z0 (int): First z coordinate
            z1 (int): Second z coordinate
            y0 (int, optional): First y coordinate. Defaults to 0 (min world height)
            y1 (int, optional): Second y coordinate. Defaults to 255 (max world height)
            ignore_house (bool, optional): Whether house blocks are ignored by algorithm. Defaults to True
            
        Returns:
            min_y (int): The minimum y ordinate that ground can be found at 
            max_y (int): The maximum y ordinate that ground can be found at

        Note: 
            If both y ordinates are below ground level, returns the maximum y ordinate as max_y
        """    

    global air_blocks
    global house_blocks

    ignore_blocks = air_blocks.copy()
    if ignore_house:
        ignore_blocks.extend(house_blocks)

    blocks_list = list(mc.getBlocks(x0, y0, z0, x1, y1, z1))
    x_length = abs(x0 - x1) + 1
    z_length = abs(z0 - z1) + 1
    y_length = abs(y0 - y1) + 1

    #convert list of blocks to 3D matrix
    blocks_matrix = np.reshape(blocks_list, (y_length, x_length, z_length))
   
    #find max ground level across matrix
    max_height = min(y0, y1)
    past_highest_point = False
    for layer in blocks_matrix:
        if past_highest_point:
            break
        past_highest_point = True
        max_height += 1
        for row in layer:
            if not set(row).issubset(ignore_blocks):
                past_highest_point = False
                break
    max_height -= 2

    blocks_matrix = blocks_matrix[::-1]

    #find min ground level across matrix
    min_height = max(y0, y1)
    past_lowest_point = False
    for layer in blocks_matrix:
        if past_lowest_point:
            break
        past_lowest_point = True
        min_height -= 1
        for row in layer:
            if set(row).intersection(ignore_blocks):
                past_lowest_point = False
                break
    min_height += 1
            
    if not past_lowest_point:
        min_height = -1
    if not past_highest_point:
        max_height = -1

    return min_height, max_height


def determine_village_location(chunks_to_search: int) -> 'tuple[int, int, int]':
    """
        Arguments:
            chunks_to_search (int): How many chunks should be searched for the best location
            
        Returns:
            x (int): The x coordinate of the middle of village location
            y (int): The y coordinate of the middle of village location
            z (int): The z coordinate of the middle of village location
        """    

    x, y, z = mc.player.getPos()

    #Determine min position in current chunk
    x = int(x // CHUNK_LENGTH * CHUNK_LENGTH)
    y = int(y) #elevation is trivial
    z = int(z // CHUNK_LENGTH * CHUNK_LENGTH)   

    return search_chunks_for_location(x, y, z, chunks_to_search)


def search_chunks_for_location(x: int, y: int, z: int, chunks_to_search: int) -> 'tuple[int, int, int]':
    """
    Arguments:
        x (int): The x coordinate to search out from
        y (int): The y coordinate to search out from
        z (int): The z coordinate to search out from
        chunks_to_search (int): The number of chunks to search. Rounds down to the nearest odd square 
        
    Returns:
        x (int): The x coordinate of the most suitable chunk in range
        y (int): The y coordinate input
        z (int): The z coordinate of the most suitable chunk in range

    Note: 
        The y coordinate is returned to allow the output to be treated as a full coordinate set
    """    

    MAX_WORLD_HEIGHT = 255
    MIN_WORLD_HEIGHT = 0

    #Find the variation in hight across a range of chunks
    chunk_matrix = []
    chunks_length_to_search = (int(chunks_to_search**(1/2))) // 2 * 2 + 1 #Total side length of area (odd for simplicity)
    chunks_distance_to_search = chunks_length_to_search // 2 #Distance from centre

    for target_x in range (-chunks_distance_to_search - 1, chunks_distance_to_search):
        chunk_list = []
        for target_z in range (-chunks_distance_to_search - 1, chunks_distance_to_search):

            blocks = list(mc.getBlocks(x + (target_x + 1) * CHUNK_LENGTH, MIN_WORLD_HEIGHT, z + (target_z + 1) * CHUNK_LENGTH,  x + (target_x + 1) * CHUNK_LENGTH, MAX_WORLD_HEIGHT, z + (target_z + 1) * CHUNK_LENGTH))

            sample_ground = MAX_WORLD_HEIGHT
            while blocks[sample_ground] in air_blocks and sample_ground > 0:
                sample_ground -= 1          

            #If there is water or lava, mark as invalid
            if blocks[sample_ground + 1] in fluid_blocks:
                chunk_list.append(-1)
            else:

                min_y, max_y = find_ground_levels(x + (target_x + 1) * CHUNK_LENGTH, x + (target_x + 1) * CHUNK_LENGTH + CHUNK_LENGTH, z + (target_z + 1) * CHUNK_LENGTH, z + (target_z + 1) * CHUNK_LENGTH + CHUNK_LENGTH)
                chunk_list.append(max_y - min_y)
        
        chunk_matrix.append(chunk_list)

    #Calculate how many valid neighbors every chunk has
    neighbors_matrix = calculate_chunk_neighbors(chunk_matrix, chunks_length_to_search, chunks_length_to_search)
 
    #Find chunk with most neighbors
    matrix_x, matrix_z = find_largest_in_matrix(neighbors_matrix, chunks_length_to_search, chunks_length_to_search)
    coord_x = x + (matrix_x - chunks_distance_to_search) * CHUNK_LENGTH
    coord_z = z + (matrix_z - chunks_distance_to_search) * CHUNK_LENGTH

    return coord_x, y, coord_z


def calculate_chunk_neighbors(matrix: 'list[list]', rows_count: int, cols_count: int) -> 'list[list]':
    """
    Arguments:
        matrix (list[list]): The matrix to find neighbors in
        rows_count (int): The number of rows in the matrix
        cols_count (int): The number of columns in the matrix
        
    Returns:
        x (int): The x coordinate of the most suitable chunk in range
        y (int): The y coordinate input
        z (int): The z coordinate of the most suitable chunk in range

    Note: 
        The y coordinate is returned to allow the output to be treated as a full coordinate set
    """  

    neighbors_matrix = []

    for row in range (rows_count):
        neighbors_list = []
        for col in range (cols_count):
            neighbors_list.append(0)
            
            offset = 2
            min_col = col - offset if col - offset >= 0 else 0
            max_col = col + offset if col + offset < cols_count else cols_count - 1
            min_row = row - offset if row - offset >= 0 else 0
            max_row = row + offset if row + offset < rows_count else rows_count - 1

            if -1 < matrix[row][col] < 4:
                for neighbor_row in range (min_row, max_row + 1):
                    for neighbor_col in range (min_col, max_col + 1):
                        if -1 < matrix[neighbor_row][neighbor_col] < 4:
                            neighbors_list[col] += 1 
        
        neighbors_matrix.append(neighbors_list)
    
    return neighbors_matrix


def find_largest_in_matrix(matrix: 'list[list]', rows_count: int, cols_count: int) -> 'tuple[int, int]':
    """
    Arguments:
        matrix (list[list]): The matrix to find neighbors in
        rows_count (int): The number of rows in the matrix
        cols_count (int): The number of columns in the matrix
        
    Returns:
        matrix_x (int): The row of the highest value in the matrix
        matrix_z (int): The column of the highest value in the matrix
    """ 

    matrix_x = 0
    matrix_z = 0
    for row in range (rows_count):
        for col in range (cols_count):
            if matrix[row][col] >= matrix[matrix_x][matrix_z]:
                matrix_x = row
                matrix_z = col

    print(matrix_x, matrix_z)

    return matrix_x, matrix_z
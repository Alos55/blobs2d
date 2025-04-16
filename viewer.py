import pygame

# Function to load block types from a single file
def load_block_types(file_path):
    block_types = {}
    with open(file_path, "r") as file:
        for line in file:
            # Ignore comments or empty lines
            if line.startswith('#') or not line.strip():
                continue
            # Split the line into block name, image path, and block ID
            parts = line.strip().split(',')
            block_name = parts[0].strip()
            image_path = parts[1].strip()
            block_id = int(parts[2].strip())
            block_types[block_id] = {
                'name': block_name,
                'image_path': image_path,
                'image': None
             }
    return block_types

# Function to load blocks from a map file (formatted as "x1 y1 z1 e")
def load_map(file_path):
    blocks = []
    with open(file_path, "r") as file:
        for line in file:
            # Ignore comments or empty lines
            if line.startswith('#') or not line.strip():
                continue

            # Split the line into parts based on spaces (x, y, z, e)
            parts = line.strip().split()

            # Extract x, y, and block ID from the line
            x_pos = int(parts[0][1:])  # Remove 'x' and convert to int
            y_pos = int(parts[1][1:])  # Remove 'y' and convert to int
            block_id = int(parts[2][1:])  # Remove 'z' and convert to int

            # Add the block data to the blocks list
            blocks.append({'x': x_pos, 'y': y_pos, 'id': block_id})

    return blocks

# Initialize pygame
pygame.init()

clock = pygame.time.Clock()
# Inside your main loop
clock.tick(60)  # Cap at 60 FPS
screen = pygame.display.set_mode((800, 600), pygame.RESIZABLE)
pygame.display.set_caption("blobs2d")

# Load the block types from the blocks.txt file (this contains all block definitions)
block_types = load_block_types("block/blocks.txt")

# Load the map (this file contains the block coordinates and IDs)
blocks = load_map("maps/testmap.txt")

# Movement variables
camera_x = 0
camera_y = 0

# Prepare the images for rendering
tile_size_change = False
TILESIZE = 32
run = True

# Function to load and scale block images dynamically
def load_block_images():
    for block_id, block_data in block_types.items():
        image_path = block_data['image_path']
        print(f"Loading image for block {block_id}: {image_path}")

        try:
            block_image = pygame.image.load(image_path)
            block_data['image'] = pygame.transform.scale(block_image, (TILESIZE, TILESIZE))
        except pygame.error as e:
            print(f"Error loading image for block {block_id}: {image_path}. Exception: {e}")
            block_data['image'] = pygame.Surface((TILESIZE, TILESIZE))
            block_data['image'].fill((255, 0, 0))

def save_map_to_file(filename, blocks):
    try:
        with open(filename, "w") as file:
            for block in blocks:
                line = f"x{block['x']} y{block['y']} z{block['id']} e\n"
                file.write(line)
        print("Map saved successfully.")
    except Exception as e:
        print(f"Failed to save map: {e}")


# Load the images initially
load_block_images()

# Main game loop
while run:
    screen_width, screen_height = screen.get_size()

    screen.fill((0, 0, 0))  # Clear the screen once per frame

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.MOUSEWHEEL:
            if event.y > 0:
                TILESIZE += 4  # Scroll up → zoom in
                tile_size_change = True
            elif event.y < 0:
                TILESIZE = max(4, TILESIZE - 4)  # Prevent going below size 4
                tile_size_change = True
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_x, mouse_y = pygame.mouse.get_pos()

           
                grid_x = (mouse_x + camera_x) // TILESIZE
                grid_y = (mouse_y + camera_y) // TILESIZE
                for block in blocks:
                    if block['x'] == grid_x and block['y'] == grid_y:
                        block['id'] = 3  # Change to grass or whatever ID you want
                        break
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL:
                save_map_to_file("maps/testmap.txt", blocks)


    # Only rescale block images if the tile size changed
   
        

    # Handle key events for WASD movement
    keys = pygame.key.get_pressed()  # Get the state of all keys

    if keys[pygame.K_w]:  # W key = move up
        camera_y += 1
    if keys[pygame.K_s]:  # S key = move down
        camera_y -= 1
    if keys[pygame.K_a]:  # A key = move left
        camera_x += 1
    if keys[pygame.K_d]:  # D key = move right
        camera_x -= 1

    # Draw only visible tiles
    for block in blocks:
        tile_x = (block['x'] * TILESIZE) - camera_x
        tile_y = (block['y'] * TILESIZE) - camera_y

        if -TILESIZE <= tile_x <= screen_width and -TILESIZE <= tile_y <= screen_height:
            block_image = block_types[block['id']]['image']
            screen.blit(block_image, (tile_x, tile_y))

        
    if tile_size_change:
        load_block_images()  # Reload and rescale images when tile size changes
        tile_size_change = False

    pygame.display.flip()  # Update the screen

print("Error: loop broke. You either quit or did unspeakable crimes.")

import pygame
import os
import threading
import tkinter as tk
from tkinter import messagebox

sensitivity = 2
camera_x = 0
camera_y = 0 
current_block_id =[1]
tile_size_change = False
TILESIZE = 32



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


def save_map_to_file(filename, blocks):
    try:
        with open(filename, "w") as file:
            for block in blocks:
                line = f"x{block['x']} y{block['y']} z{block['id']} e\n"
                file.write(line)
        print("Map saved successfully.")
    except Exception as e:
        print(f"Failed to save map: {e}")
def run_pygame():
    global TILESIZE, tile_size_change, camera_x, camera_y
    run = True
    pygame.init()
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
    clock = pygame.time.Clock()

    screen = pygame.display.set_mode((800, 600), pygame.RESIZABLE)
    pygame.display.set_caption("blobs2d")


    block_types = load_block_types("block/blocks.txt")


    blocks = load_map("maps/testmap.txt")





    load_block_images()


    while run:
        
        screen_width, screen_height = screen.get_size()

        screen.fill((0, 0, 0))  # Clear the screen once per frame

        if tile_size_change:
            load_block_images()  # Reload and rescale images when tile size changes
            tile_size_change = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                os._exit(0)
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
                            block['id'] = current_block_id[0]
                            break
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    save_map_to_file("maps/testmap.txt", blocks)


    # Only rescale block images if the tile size changed
   
        

    # Handle key events for WASD movement
        keys = pygame.key.get_pressed()  # Get the state of all keys

        if keys[pygame.K_w]:  # W key = move up
            camera_y += sensitivity
        if keys[pygame.K_s]:  # S key = move down
            camera_y -= sensitivity
        if keys[pygame.K_a]:  # A key = move left
            camera_x += sensitivity
        if keys[pygame.K_d]:  # D key = move right
            camera_x -= sensitivity

    # Draw only visible tiles
        for block in blocks:
            tile_x = (block['x'] * TILESIZE) - camera_x
            tile_y = (block['y'] * TILESIZE) - camera_y

            if -TILESIZE <= tile_x <= screen_width and -TILESIZE <= tile_y <= screen_height:
                block_image = block_types[block['id']]['image']
                screen.blit(block_image, (tile_x, tile_y))

        
        
        clock.tick(60)
        pygame.display.flip()  # Update the screen

def run_tk(block_types):
    def on_select(block_id):
        current_block_id[0] = block_id
        print(f"Selected block ID: {block_id}")
    def on_close():
        os._exit(0)
    root = tk.Tk()
    root.title("Block Selector")
    canvas = tk.Canvas(root)
    scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
    scroll_frame = tk.Frame(canvas)

    scroll_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    for block_id, data in block_types.items():
        name = data['name']
        btn = tk.Button(scroll_frame, text=f"{name} (ID {block_id})", width=30, command=lambda bid=block_id: on_select(bid))
        btn.pack(pady=2, padx=5)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    root.mainloop()

pygame_thread = threading.Thread(target=run_pygame, daemon=True)
pygame_thread.start()

run_tk(load_block_types("block/blocks.txt"))

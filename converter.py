from PIL import Image

# Open the irregular sprite sheet
sprite_sheet = Image.open("RunCattt.png").convert("RGBA")
width, height = sprite_sheet.size

# Step 1: Scan the image horizontally to find solid columns vs empty columns
has_content = []
for x in range(width):
    # Check if any pixel in this column is not fully transparent
    column_has_pixel = any(sprite_sheet.getpixel((x, y))[3] > 0 for y in range(height))
    has_content.append(column_has_pixel)

# Step 2: Group consecutive content columns into frame boundaries
frames_bounds = []
in_frame = False
start_x = 0

for x, active in enumerate(has_content):
    if active and not in_frame:
        start_x = x
        in_frame = True
    elif not active and in_frame:
        # We found the end of a cat; add a small 1-2 pixel padding if needed
        frames_bounds.append((start_x, x))
        in_frame = False

if in_frame:
    frames_bounds.append((start_x, width))

# Step 3: Crop frames and pad them to a uniform size so the cat doesn't shake
frames = []
max_frame_w = max(end - start for start, end in frames_bounds)

for start, end in frames_bounds:
    # Crop the raw cat
    raw_frame = sprite_sheet.crop((start, 0, end, height))
    
    # Create a uniform transparent canvas so frames align perfectly at the bottom
    unified_frame = Image.new("RGBA", (max_frame_w, height), (0, 0, 0, 0))
    
    # Center horizontally, align to the bottom edge
    paste_x = (max_frame_w - (end - start)) // 2
    unified_frame.paste(raw_frame, (paste_x, 0))
    
    frames.append(unified_frame)

# Step 4: Export the dynamic GIF
frames[0].save(
    "dynamic_jump_cat.gif",
    save_all=True,
    append_images=frames[1:],
    duration=100,  # Jump animations usually look better a bit faster!
    loop=0
)

print(f"Successfully detected and extracted {len(frames)} frames!")
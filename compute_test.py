hex_rows = [3, 4, 5, 4, 3]

# Horizontal and vertical spacing between hex centers
hex_dx = 6  # width per hex
hex_dy = 4  # height per row

# Relative positions for the 6 corners of each hex tile
corner_offsets = [
    (-1, 0),     # top
    (-0.5, 0.87),# top-right
    (0.5, 0.87), # bottom-right
    (1, 0),      # bottom
    (0.5, -0.87),# bottom-left
    (-0.5, -0.87)# top-left
]

corner_points = set()

for row_idx, num_hexes in enumerate(hex_rows):
    # Horizontal offset to center the hexes
    offset = (max(hex_rows) - num_hexes) * (hex_dx // 2)

    for col_idx in range(num_hexes):
        # Calculate center of the current hex
        x = col_idx * hex_dx + offset
        y = row_idx * hex_dy

        # Add 6 corners around this hex center
        for dy, dx in corner_offsets:
            cx = int(x + dx * hex_dx / 2)
            cy = int(y + dy * hex_dy / 2)
            corner_points.add((cy, cx))

# Get grid size
max_y = max(y for y, x in corner_points) + 1
max_x = max(x for y, x in corner_points) + 1

# Build the grid
grid = [['  ' for _ in range(max_x + 1)] for _ in range(max_y + 1)]

for y, x in corner_points:
    if 0 <= y < len(grid) and 0 <= x < len(grid[0]):
        grid[y][x] = 'o '

# Print it
for row in grid:
    print(''.join(row).rstrip())


5-3 + 1
5-3 
5-3
5-4 + 1



5 - 3 + 1 =3, 3 = 3
5 - 3 = 2, 3 + 1 = 4
5 - 3 = 2, 3 + 1 = 4
5 - 4 = 1, 4 + 1 = 5
1
0
0

array = [3,4,5,4.3]
width = max(array)
height = len(array)
rows = 2 * height + 2

board = ""      
for i in range(rows):
    if i == 0:
        spaces = 
        board = board + 

    elif i == height:


A B C D E F G H I J K
      ##  ##  ##
    ##  ##  ##  ##
    ##  ##  ##  ##
  ##  ##  ##  ##  ##
  ##  ##  ##  ##  ##
##  ##  ##  ##  ##  ##
##  ##  ##  ##  ##  ##
  ##  ##  ##  ##  ##
  ##  ##  ##  ##  ##
    ##  ##  ##  ##
    ##  ##  ##  ##
      ##  ##  ##
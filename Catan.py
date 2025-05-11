import pygame
import sys
import math
import random
from engine.game_engine import GameEngine
from enum import Enum, auto

# --- Constants ---
SCREEN_WIDTH, SCREEN_HEIGHT = 1200, 900  # Window dimensions
HEX_RADIUS = 70  # Radius of each hex tile
BOARD_ORIGIN = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)  # Center of the board
SNAP_THRESHOLD = 45  # Pixel distance threshold for snapping clicks to nodes/edges

# ---Debugging ---
SHOW_NODE_IDS = False

# --- Colors ---
COLOR_BG = (245, 222, 179)  # Background sand/beige
COLOR_LINE = (0, 0, 0)  # Outline lines
COLOR_BUTTON = (200, 200, 200)  # Button background
COLOR_BUTTON_TEXT = (0, 0, 0)  # Button text
COLOR_ACTIVE_BUTTON_BG = (255, 255, 255)  # Active button fill
COLOR_ACTIVE_BUTTON_BORDER = (255, 0, 0)  # Active button border
COLOR_PLAYABLE = (0, 200, 0)  # Playable dev card indicator
COLOR_UNPLAYABLE = (150, 150, 150)  # Unplayable dev card indicator
COLOR_CURRENT_TURN = (0, 255, 0)    # Bright green
COLOR_NOT_TURN = (150, 150, 150)    # Grey
COLOR_GHOST = (180, 180, 180)  # Light grey
# Resource-specific tile colors
RESOURCE_COLORS = {
    'wood': (34, 139, 34),
    'brick': (178, 34, 34),
    'sheep': (144, 238, 144),
    'wheat': (238, 232, 170),
    'ore': (169, 169, 169),
    'desert': (210, 180, 140)
}

# --- Preset data ---
# Generic player names
NAMES = [
    "Alex", "Jordan", "Taylor", "Morgan", "Casey",
    "Riley", "Jamie", "Cameron", "Drew", "Reese",
    "Quinn", "Avery", "Peyton", "Hayden", "Rowan",
    "Skyler", "Dakota", "Payton", "Finley", "Emerson"
]
# Development card types and labels
DEV_CARD_OPTIONS = [
    ("Knight", ("Knight", "")),
    ("Road Building", ("Road", "Building")),
    ("Year of Plenty", ("Year of", "Plenty")),
    ("Monopoly", ("Monopoly", "")),
    ("Victory Point", ("Victory", "Point"))
]

BUILD_COSTS = {
    'road': {"wood": 1, "brick": 1},
    'settle': {"wood": 1, "brick": 1, "sheep": 1, "wheat": 1},
    'upgrade': {"ore": 3, "wheat": 2},
    'buy': {"ore": 1, "sheep": 1, "wheat": 1}
}

class Resource(Enum):
    """Enum for resource types on tiles."""
    WOOD = auto()
    BRICK = auto()
    SHEEP = auto()
    WHEAT = auto()
    ORE = auto()
    DESERT = auto()

class BotPlayer:
    def __init__(self, name, strategy_module):
        self.name = name
        self.strategy = strategy_module  # imported Python module
        self.resources = {r: 0 for r in Resource}
        self.node_states = []
        self.edge_states = []
        self.dev_cards = []

    def take_turn(self, game_state):
        # Example call to script
        action = self.strategy.choose_build(game_state)
        return action

class Debug_And_Log:
    """Class to log different types"""
    def __init__(self):
        self.mode = "Debug" # Debug, Normal, Off

    def Debug_Log(self, text):
        if self.mode == "Debug":
            print(f'[Debug] {text}')

    def Game_Log(self, text):
        if self.mode == "Debug" or self.mode == "Normal":
            print(f'[Game] {text}')

    def Setup_Log(self, text):
        if self.mode == "Debug" or self.mode == "Normal":
            print(f'[Setup] {text}')

class Tile:
    """
    Represents a single hex tile on the board.
    Stores resource type, number token, and center position.
    """
    def __init__(self, resource, number, position):
        self.resource = resource  # Resource enum
        self.number = number      # Dice number (None for desert)
        self.position = position  # (x, y) center coordinates

    def draw(self, screen):
        """
        Draws the hex: fill with resource color, outline, and number.
        """
        pts = []
        # Compute six corners for flat-top hexagon
        for i in range(6):
            angle = math.radians(60 * i - 30)
            x = self.position[0] + HEX_RADIUS * math.cos(angle)
            y = self.position[1] + HEX_RADIUS * math.sin(angle)
            pts.append((x, y))
        # Draw filled polygon
        color_key = self.resource.name.lower()
        pygame.draw.polygon(screen, RESOURCE_COLORS[color_key], pts)
        # Draw outline
        pygame.draw.polygon(screen, COLOR_LINE, pts, 2)
        # Draw number token if present
        if self.number is not None:
            font = pygame.font.SysFont(None, 28)
            text = font.render(str(self.number), True, COLOR_BUTTON_TEXT)
            screen.blit(text, text.get_rect(center=self.position))

class Board:
    """
    Manages the hex grid: generates tile layout, computes
    graph nodes (for settlements) and edges (for roads).
    """
    def __init__(self):
        self.tiles = []  # List of Tile objects
        self.nodes = []  # Unique corner positions for settlements
        self.edges = []  # Midpoints between corners for roads
        self.generate_board()
        self.compute_graph()

    def generate_board(self):
        """
        Randomly shuffles resources and number tokens,
        then positions tiles in 5 rows: 3-4-5-4-3 layout.
        """
        print("[Game] Board reshuffled")
        self.tiles.clear()
        # Prepare resource and number pools
        res_pool = ([Resource.WOOD]*4 + [Resource.BRICK]*3 + [Resource.SHEEP]*4 +
                    [Resource.WHEAT]*4 + [Resource.ORE]*3 + [Resource.DESERT])
        num_pool = [2,3,3,4,4,5,5,6,6,8,8,9,9,10,10,11,11,12]
        random.shuffle(res_pool)
        random.shuffle(num_pool)
        rows = [3, 4, 5, 4, 3]
        horiz = HEX_RADIUS * math.sqrt(3)
        vert = HEX_RADIUS * 1.5
        idx = 0
        for r, count in enumerate(rows):
            y = BOARD_ORIGIN[1] + (r - 2) * vert
            for i in range(count):
                x = BOARD_ORIGIN[0] + (i - (count - 1)/2) * horiz
                res = res_pool[idx]
                num = None if res == Resource.DESERT else num_pool.pop()
                self.tiles.append(Tile(res, num, (x, y)))
                idx += 1
        print("[DEBUG] Assigned tile numbers:")
        for i, tile in enumerate(self.tiles):
            print(f"  Tile {i} at {tile.position} - {tile.resource.name}, number: {tile.number}")

    def draw(self, screen):
        """Draws all hex tiles on provided screen."""
        for tile in self.tiles:
            tile.draw(screen)

    def compute_graph(self):
        self.nodes = []
        self.edges = []
        self.node_adjacency = {}

        # Map to avoid duplicate nodes by coordinate proximity
        coord_to_index = {}

        # Helper to deduplicate and assign a unique index to each node
        def get_or_create_node(coord):
            for existing_coord, idx in coord_to_index.items():
                if math.hypot(coord[0] - existing_coord[0], coord[1] - existing_coord[1]) < 1:
                    return idx
            idx = len(self.nodes)
            self.nodes.append(coord)
            coord_to_index[coord] = idx
            return idx

        tile_corner_lists = []

        for tile in self.tiles:
            # Get all 6 corners of the hex
            corner_indices = []
            for i in range(6):
                angle = math.radians(60 * i - 30)
                x = tile.position[0] + HEX_RADIUS * math.cos(angle)
                y = tile.position[1] + HEX_RADIUS * math.sin(angle)
                idx = get_or_create_node((x, y))
                corner_indices.append(idx)
            tile_corner_lists.append(corner_indices)

            # Add edges and adjacency between corner indices
            for i in range(6):
                a = corner_indices[i]
                b = corner_indices[(i + 1) % 6]

                # Bidirectional adjacency
                self.node_adjacency.setdefault(a, set()).add(b)
                self.node_adjacency.setdefault(b, set()).add(a)

                # Add midpoint for road placement
                midpoint = (
                    (self.nodes[a][0] + self.nodes[b][0]) / 2,
                    (self.nodes[a][1] + self.nodes[b][1]) / 2
                )
                if all(math.hypot(midpoint[0] - e[0], midpoint[1] - e[1]) > 1 for e in self.edges):
                    self.edges.append(midpoint)

        # --- Sort node list (top to bottom, then left to right)
        sorted_nodes = sorted(enumerate(self.nodes), key=lambda pair: (round(pair[1][1]), round(pair[1][0])))
        old_to_new_index = {old: new for new, (old, _) in enumerate(sorted_nodes)}
        self.nodes = [coord for _, coord in sorted_nodes]

        # --- Remap adjacency
        new_adjacency = {}
        for old_idx, neighbors in self.node_adjacency.items():
            new_idx = old_to_new_index[old_idx]
            new_adjacency[new_idx] = {old_to_new_index[n] for n in neighbors}
        self.node_adjacency = new_adjacency

        # --- Remap edge positions
        new_edges = []
        for edge in self.edges:
            new_edges.append(edge)
        self.edges = new_edges

        # --- Debug output
        print("[DEBUG] Node Adjacency List:")
        for node_index, neighbors in sorted(self.node_adjacency.items()):
            print(f"[DEBUG] Node {node_index} adjacent to: {sorted(neighbors)}")

        print(f"[DEBUG] Total Nodes: {len(self.nodes)}, Total Edges: {len(self.edges)}")



class Player:
    """
    Tracks a player's resources, dev cards,
    and placement states (states arrays for nodes and edges).
    """
    def __init__(self, idx, name, color, node_count, edge_count):
        self.id = idx
        self.name = name
        self.color = color
        # Resource counts
        self.resources = {r: 0 for r in Resource}
        # Dev cards: mapping label -> list of turns bought
        self.dev_cards = {lbl: [] for lbl, _ in DEV_CARD_OPTIONS}
        # State arrays: track placement at each graph index
        self.node_states = ["empty"] * node_count  # 'empty','settlement','city'
        self.edge_states = ["empty"] * edge_count  # 'empty','road'
        # Derived stats
        self.victory_points = 0
        self.longest_road = 0

    @property
    def card_count(self):
        """Total resource cards in hand."""
        return sum(self.resources.values())

    def update_stats(self):
        """Recomputes victory points and longest road from state arrays."""
        self.victory_points = self.node_states.count("settlement") + 2*self.node_states.count("city")
        self.longest_road = self.edge_states.count("road")

class Game:
    """
    Main game controller: initializes board and players,
    handles input, updates state, and renders frames.
    """
    def __init__(self, num_players=3):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Catan")
        self.clock = pygame.time.Clock()
        # Board and graph positions
        self.board = Board()
        self.pos_nodes = sorted(self.board.nodes, key=lambda p: (p[1], p[0]))
        self.pos_edges = sorted(self.board.edges, key=lambda p: (p[1], p[0]))
        print(f"[DEBUG] Loaded {len(self.pos_nodes)} nodes and {len(self.pos_edges)} edges")
        # Player setup
        self.min_players, self.max_players = 2, 5
        self.num_players = max(self.min_players, min(num_players, self.max_players))
        self.players = []
        self.node_ownership = {}  # node_index -> player_id, 'settlement' or 'city'
        self.edge_ownership = {}  # edge_index -> player_id
        self.selected_player = 0
        self.current_turn = 0
        self.engine = GameEngine(
            players=self.players,
            tiles=self.board.tiles,
            nodes=self.pos_nodes,
            edges=self.pos_edges)
        # UI elements
        self.btn_rect = {}
        self.roll_rect = pygame.Rect(SCREEN_WIDTH-150, SCREEN_HEIGHT-60, 130, 50)
        self.play_buttons = {}
        self.build_mode = None
        self.dice_result = None
        self.ui_popup_message = None  # (text, frame_timer)
        # Whether the roll dice button is active
        self.roll_active = True
        self.show_node_ids = SHOW_NODE_IDS # Show node IDs for debugging; toggle this as needed
        # Fonts
        self.font = pygame.font.SysFont(None, 24)
        self.title_font = pygame.font.SysFont(None, 28)
        self.init_ui()
        self.setup_players()
        self.phase = 'setup'  # Track whether in initial placement or regular game
        self.setup_step = 0  # Tracks progress through setup phase (settlement and road)
        self.robber_tile_index = None  # Track robber location
        self.setup_resource_popup = None  # Tuple of (player_name, list of resources, frame_timer)
        print("[Game] Board reshuffled")
        print("[Setup] Entering setup phase")
        print(f"[Setup] {self.engine.players[self.setup_player_index()].name} to place settlement")
    
    

    def init_ui(self):
        """Define rectangles for UI buttons."""
        btns = [
            ('reshuffle',20,20,160,40), ('clear',200,20,160,40),
            ('road',380,20,120,40),    ('settle',510,20,120,40),
            ('upgrade',640,20,120,40), ('buy',770,20,120,40),
            ('dec',900,20,40,40),      ('inc',950,20,40,40)
        ]
        for n,x,y,w,h in btns:
            self.btn_rect[n] = pygame.Rect(x, y, w, h)

    def is_valid_settlement(self, player, node_index):
        print(f"[DEBUG] Checking node {node_index}, adjacent: {self.board.node_adjacency.get(node_index)}")
        print(f"[DEBUG] Existing settlements at: {list(self.engine.node_ownership.keys())}")
        # Can't place on an already occupied node
        if self.node_ownership.get(node_index):
            return False

        # Check adjacent nodes using current ownership
        for neighbor in self.board.node_adjacency.get(node_index, []):
            owner = self.node_ownership.get(neighbor)
            if owner and owner[1] in ('settlement', 'city'):
                return False

        return True

    def is_valid_road(self, player, edge_index):
        edge_pos = self.pos_edges[edge_index]

        # Check if edge is already taken
        if edge_index in self.edge_ownership:
            return False

        # Find adjacent node indices (settlements/cities)
        adjacent_node_indices = [
            i for i, node_pos in enumerate(self.pos_nodes)
            if math.hypot(edge_pos[0] - node_pos[0], edge_pos[1] - node_pos[1]) < HEX_RADIUS * 0.6
        ]

        # ✅ Check if any adjacent node is owned by the player
        for node_index in adjacent_node_indices:
            owner = self.node_ownership.get(node_index)
            if owner and owner[0] == player.id:
                return True

        # ✅ Check if any neighboring edge is owned by the player
        for i, other_edge_pos in enumerate(self.pos_edges):
            if i == edge_index:
                continue
            if math.hypot(edge_pos[0] - other_edge_pos[0], edge_pos[1] - other_edge_pos[1]) < HEX_RADIUS * 0.6:
                if self.edge_ownership.get(i, (None,))[0] == player.id:
                    return True

        return False

    def can_afford(self, player, build_type):
        for res, cost in BUILD_COSTS[build_type].items():
            if player.resources[res] < cost:
                return False
        return True

    def pay_cost(self, player, build_type):
        for res, cost in BUILD_COSTS[build_type].items():
            player.resources[res] -= cost

    def distribute_resources(self):
        popup_log = []

        for tile in self.board.tiles:
            if tile.number == self.dice_result:
                for node_index in self.get_adjacent_nodes(tile):
                    owner = self.node_ownership.get(node_index)
                    if owner:
                        player_id, structure = owner
                        amount = 2 if structure == "city" else 1
                        self.engine.players[player_id].resources[tile.resource] += amount
                        popup_log.append(f"{self.engine.players[player_id].name} +{amount} {tile.resource.name.title()}")

        if popup_log:
            self.setup_resource_popup = ("Resources: " + ", ".join(popup_log), 3 * 30)


    def handle_roll(self):
        self.dice_result = random.randint(1, 6) + random.randint(1, 6)
        if self.dice_result == 7:
            self.handle_robber()
        else:
            self.distribute_resources()

    def handle_robber(self):
        # TODO: Implement discard logic and robber placement
        print("[Robber] Rolled 7: implement discard and move robber")

    def play_card(self, lbl):
        # Existing dev card logic...
        if lbl == "Year of Plenty":
            # TODO: Let player choose 2 resources
            pass
        elif lbl == "Monopoly":
            # TODO: Take all of chosen resource from others
            pass
        elif lbl == "Road Building":
            # TODO: Place 2 free roads
            pass
        elif lbl == "Knight":
            self.handle_robber()

    def check_win(self):
        for p in self.engine.players:
            if p.victory_points >= WINNING_VICTORY_POINTS:
                print(f"[Game Over] {self.current_player().name} wins!")
                pygame.quit()
                sys.exit()

    def get_tiles_adjacent_to_node(self, node_index):
        """Return all tiles adjacent to a node (corner)."""
        node_pos = self.pos_nodes[node_index]
        adjacent_tiles = []
        for tile in self.board.tiles:
            for i in range(6):
                angle = math.radians(60 * i - 30)
                corner_x = tile.position[0] + HEX_RADIUS * math.cos(angle)
                corner_y = tile.position[1] + HEX_RADIUS * math.sin(angle)
                if math.hypot(corner_x - node_pos[0], corner_y - node_pos[1]) < 1:
                    adjacent_tiles.append(tile)
                    break
        return adjacent_tiles

    def next_turn(self):
        self.current_turn += 1
        self.handle_roll()
        self.check_win()

    def trade_with_bank(self, player, give_res, get_res):
        if player.resources[give_res] >= 4:
            player.resources[give_res] -= 4
            player.resources[get_res] += 1

    def get_adjacent_nodes(self, tile):
        """Return all node indices that are adjacent (corners) to a given tile."""
        tile_nodes = []
        for i, node in enumerate(self.pos_nodes):
            for j in range(6):
                angle = math.radians(60 * j - 30)
                corner_x = tile.position[0] + HEX_RADIUS * math.cos(angle)
                corner_y = tile.position[1] + HEX_RADIUS * math.sin(angle)
                if math.hypot(corner_x - node[0], corner_y - node[1]) < 1:
                    tile_nodes.append(i)
                    break
        return tile_nodes

    def is_active_player(self, player_id):
        return player_id == (self.current_turn % self.num_players)

    def setup_players(self):
        """Assign names, colors, and initialize state arrays for each player."""
        names = random.sample(NAMES, self.num_players)
        for i,name in enumerate(names):
            color = (random.randint(50,255), random.randint(50,255), random.randint(50,255))
            p = Player(i, name, color, len(self.pos_nodes), len(self.pos_edges))
            self.engine.players.append(p)

    def next_turn(self):
        """Advance turn counter and log."""
        self.current_turn += 1
        print(f"{self.log_prefix()}'s turn")

        if self.phase == "game":
            self.roll_active = True

    def clear_board(self):
        """Reset all placement states and ownership for a fresh start."""
        for p in self.engine.players:
            p.node_states = ["empty"] * len(self.pos_nodes)
            p.edge_states = ["empty"] * len(self.pos_edges)
            p.update_stats()

        self.node_ownership.clear()
        self.edge_ownership.clear()
        self.phase = 'setup'
        self.setup_step = 0
        self.dice_result = None
        print("[Game] Board cleared")
        print("[Setup] Entering setup phase")
        print(f"[Setup] {self.engine.players[self.setup_player_index()].name} to place settlement")

    def buy(self):
        """Buy a random development card and log purchase."""
        p = self.engine.players[self.selected_player]
        card = random.choice([lbl for lbl,_ in DEV_CARD_OPTIONS])
        p.dev_cards[card].append(self.current_turn)
        print(f"{self.log_prefix()} bought {card}")

    def play_card(self, lbl):
        """Play a bought dev card if eligible and log."""
        p = self.engine.players[self.selected_player]
        for t in p.dev_cards[lbl]:
            if t < self.current_turn:
                p.dev_cards[lbl].remove(t)
                print(f"{self.log_prefix()} played {lbl}")
                break

    def place_piece(self, pt):
        print(f"[DEBUG] Clicked at {pt}")

        if not self.pos_nodes:
            print("[DEBUG] pos_nodes is empty!")
            return

        idx = min(range(len(self.pos_nodes)), key=lambda i: math.hypot(pt[0] - self.pos_nodes[i][0], pt[1] - self.pos_nodes[i][1]))
        dist = math.hypot(pt[0] - self.pos_nodes[idx][0], pt[1] - self.pos_nodes[idx][1])
        print(f"[DEBUG] Closest node is {idx} at distance {dist}")
        print(f"[DEBUG] Selected node {idx} has neighbors: {self.board.node_adjacency.get(idx)}")

        if dist > SNAP_THRESHOLD:
            print(f"[DEBUG] Too far from node. Not placing.")
            return

        if self.phase == 'setup':
            if self.setup_step % 2 == 0:
                # Settlement placement
                player_index = self.setup_player_index()
                player = self.engine.players[player_index]
                self.selected_player = player_index

                idx = min(range(len(self.pos_nodes)), key=lambda i: math.hypot(pt[0] - self.pos_nodes[i][0], pt[1] - self.pos_nodes[i][1]))
                if self.node_ownership.get(idx):
                    print(f"[Setup] {player.name} cannot place settlement: node {idx} already occupied")
                    return
                if not self.is_valid_settlement(player, idx):
                    print(f"[Setup] {player.name} cannot place settlement: invalid location at node {idx}")
                    return
                player.node_states[idx] = "settlement"
                self.engine.node_ownership[idx] = (player.id, 'settlement')
                print(f"[Setup] {player.name} placed settlement at node {idx}")

                # If it's the player's second settlement (in reverse setup phase), give resources
                settlements_now = player.node_states.count("settlement")
                if self.setup_step >= self.num_players * 2 and settlements_now == 2:
                    tiles = self.get_tiles_adjacent_to_node(idx)
                    for tile in tiles:
                        if tile.resource != Resource.DESERT:
                            player.resources[tile.resource] += 1
                    resources_granted = [tile.resource.name.title() for tile in tiles if tile.resource != Resource.DESERT]
                    print(f"[Setup] {player.name} received starting resources: {resources_granted}")
                    self.setup_resource_popup = (player.name, resources_granted, 3*30)  # Show for ~3 seconds at 30 FPS

            
            else:
                # Road placement
                player_index = self.setup_player_index()
                player = self.engine.players[player_index]
                self.selected_player = player_index

                idx = min(range(len(self.pos_edges)), key=lambda i: math.hypot(pt[0] - self.pos_edges[i][0], pt[1] - self.pos_edges[i][1]))
                
                if not self.is_valid_road(player, idx):
                    print(f"[Setup] {player.name} cannot place road: not adjacent to own settlement or road")
                    return

                player.edge_states[idx] = "road"
                self.edge_ownership[idx] = (player.id, 'road')
                print(f"[Setup] {player.name} placed road at edge {idx}")

            self.setup_step += 1


            if self.setup_step >= self.num_players * 2 * 2:
                self.phase = 'game'
                print("[Game] Setup complete, entering main game phase")
                print(f"[Game] {self.engine.players[self.current_turn % self.num_players].name}'s turn to roll the dice")
            else:
                next_player = self.engine.players[self.setup_player_index()]
                next_action = "settlement" if self.setup_step % 2 == 0 else "road"
                print(f"[Setup] {next_player.name} to place {next_action}")
            return

        # ⬇️ MAIN GAME PHASE (normal placements)
        p = self.engine.players[self.selected_player]

        if self.build_mode == 'road':
            idx = min(range(len(self.pos_edges)), key=lambda i: math.hypot(pt[0]-self.pos_edges[i][0], pt[1]-self.pos_edges[i][1]))
            if p.edge_states[idx] == "empty":
                p.edge_states[idx] = "road"
                self.edge_ownership[idx] = (p.id, 'road')
                p.update_stats()
                print(f"{self.log_prefix()} built road at edge {idx}")

        elif self.build_mode == 'settle':
            idx = min(range(len(self.pos_nodes)), key=lambda i: math.hypot(pt[0] - self.pos_nodes[i][0], pt[1] - self.pos_nodes[i][1]))
            if self.node_ownership.get(idx):
                print(f"{self.log_prefix()} cannot build: node {idx} already occupied")
                return
            if not self.is_valid_settlement(p, idx):
                print(f"{self.log_prefix()} invalid settlement location at node {idx}")
                return
            if not self.can_afford(p, 'settle'):
                print(f"{self.log_prefix()} cannot afford a settlement")
                return
            self.pay_cost(p, 'settle')
            p.node_states[idx] = "settlement"
            self.engine.node_ownership[idx] = (p.id, 'settlement')
            p.update_stats()
            print(f"{self.log_prefix()} built settlement at node {idx}")

        elif self.build_mode == 'upgrade':
            for i,state in enumerate(p.node_states):
                if state == "settlement":
                    p.node_states[i] = "city"
                    self.node_ownership[i] = (p.id, 'city')
                    p.update_stats()
                    print(f"{self.log_prefix()} upgraded settlement to city at node {i}")
                    break

    def draw_setup_popup(self):
        if self.setup_resource_popup:
            frames_left = 0  # fallback

            # Handle both 2-element and 3-element tuple cases
            if len(self.setup_resource_popup) == 3:
                name, resources, frames_left = self.setup_resource_popup
                message = f"{name} receives: " + ", ".join(resources)
            else:
                message, frames_left = self.setup_resource_popup

            # Decrease frame timer
            if frames_left <= 0:
                self.setup_resource_popup = None
                return

            # Save updated timer
            if len(self.setup_resource_popup) == 3:
                self.setup_resource_popup = (name, resources, frames_left - 1)
            else:
                self.setup_resource_popup = (message, frames_left - 1)

            # Draw popup
            surf = self.title_font.render(message, True, (0, 0, 0))
            bg_rect = pygame.Rect(0, 0, surf.get_width() + 20, surf.get_height() + 10)
            bg_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 160)

            pygame.draw.rect(self.screen, (255, 255, 220), bg_rect)
            pygame.draw.rect(self.screen, (0, 0, 0), bg_rect, 2)
            self.screen.blit(surf, surf.get_rect(center=bg_rect.center))

    def draw_ui_popup(self):  # ✅ Insert it here
        if self.ui_popup_message:
            text, frames_left = self.ui_popup_message
            if frames_left <= 0:
                self.ui_popup_message = None
                return
            self.ui_popup_message = (text, frames_left - 1)

            surf = self.font.render(text, True, (0, 0, 0))
            bg_rect = pygame.Rect(0, 0, surf.get_width() + 20, surf.get_height() + 10)
            bg_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 190)

            pygame.draw.rect(self.screen, (255, 220, 220), bg_rect)
            pygame.draw.rect(self.screen, (150, 0, 0), bg_rect, 2)
            self.screen.blit(surf, surf.get_rect(center=bg_rect.center))

    def setup_player_index(self):
        placements_per_player = 2
        total_steps = self.num_players * placements_per_player

        if self.setup_step < total_steps:
            # First round: forward order
            return self.setup_step // placements_per_player
        else:
            # Second round: reverse order
            return self.num_players - 1 - ((self.setup_step - total_steps) // placements_per_player)


    def draw_player_stats(self):
        """Draw stats panels for all players at top of screen."""
        self.stats_rects = []
        sx, sy = 20, 80  # Starting x,y
        lh = self.font.get_height()
        bw = 220  # Panel width

        if self.phase == 'setup':
            active_id = self.setup_player_index()
        else:
            active_id = self.current_turn % self.num_players

        for i, p in enumerate(self.engine.players):
            x = sx + i*(bw + 10)
            y = sy
            rect = pygame.Rect(x-5, y-5, bw, lh*6+10)
            pygame.draw.rect(self.screen, (255,255,255), rect)

            # ✅ Now this line is inside the loop and uses `p`
            if p.id == active_id:
                pygame.draw.rect(self.screen, COLOR_CURRENT_TURN, rect, 3)
            else:
                pygame.draw.rect(self.screen, COLOR_NOT_TURN, rect, 3)

            self.stats_rects.append(rect)
            self.screen.blit(self.title_font.render(p.name, True, p.color), (x,y))
            stats = [
                f"VP: {p.victory_points}",
                f"Cards: {p.card_count}",
                f"LR: {p.longest_road}",
                f"R: {p.edge_states.count('road')}",
                f"S: {p.node_states.count('settlement')}"
            ]
            for j,t in enumerate(stats, start=1):
                self.screen.blit(self.font.render(t,True,COLOR_BUTTON_TEXT),(x+5,y+j*lh))


    def draw_selected_info(self):
        """Draw resources and dev card info for selected player with play buttons."""
        p = self.engine.players[self.selected_player]
        info_h = 100
        y0 = SCREEN_HEIGHT - info_h
        info_w = SCREEN_WIDTH - (self.roll_rect.width + 20)
        pygame.draw.rect(self.screen, (220,220,220), (0,y0,info_w,info_h))
        lh = self.font.get_height()
        y1, y2, y3 = y0+5, y0+5+lh, y0+5+2*lh
        slots = [r for r in Resource if r!=Resource.DESERT] + [lbl for lbl,_ in DEV_CARD_OPTIONS]
        spacing = info_w//(len(slots)+1)
        x = spacing
        self.play_buttons.clear()
        for s in slots:
            if isinstance(s,Resource):
                nm = s.name.title();
                surf = self.font.render(nm,True,COLOR_BUTTON_TEXT)
                self.screen.blit(surf,surf.get_rect(center=(x,(y1+y2)//2)))
                ct = p.resources[s]
                cts = self.font.render(str(ct),True,COLOR_BUTTON_TEXT)
                self.screen.blit(cts,cts.get_rect(center=(x,y3)))
            else:
                for lbl,lines in DEV_CARD_OPTIONS:
                    if lbl==s: la,lb=lines;break
                a_s=self.font.render(la,True,COLOR_BUTTON_TEXT)
                b_s=self.font.render(lb,True,COLOR_BUTTON_TEXT)
                self.screen.blit(a_s,a_s.get_rect(center=(x,y1)))
                self.screen.blit(b_s,b_s.get_rect(center=(x,y2)))
                cv=len(p.dev_cards[s])
                cvs=self.font.render(str(cv),True,COLOR_BUTTON_TEXT)
                cr=cvs.get_rect(center=(x,y3));self.screen.blit(cvs,cr)
                if s!="Victory Point":
                    btn=pygame.Rect(cr.left,y3+5,cr.width,20)
                    playable=any(t<self.current_turn for t in p.dev_cards[s])
                    clr=COLOR_PLAYABLE if playable else COLOR_UNPLAYABLE
                    pygame.draw.rect(self.screen,clr,btn,2)
                    self.play_buttons[s]=(btn,playable)
            x+=spacing

    def draw_placements(self):
        """Render roads, settlements, and cities from state arrays."""
        for p in self.engine.players:
            for i,st in enumerate(p.edge_states):
                if st=='road':
                    x,y=self.pos_edges[i]
                    pygame.draw.line(self.screen,p.color,(x-15,y),(x+15,y),4)
            for i,st in enumerate(p.node_states):
                x,y=self.pos_nodes[i]
                if st=='settlement': pygame.draw.circle(self.screen,p.color,(int(x),int(y)),10)
                elif st=='city': pygame.draw.rect(self.screen,p.color,pygame.Rect(x-10,y-10,20,20))
        # === Draw ghost previews ===
        if self.build_mode in ['road', 'settle', 'upgrade'] or self.phase == 'setup':
            if self.build_mode == 'road':
                for i, (x, y) in enumerate(self.pos_edges):
                    if i not in self.edge_ownership:
                        pygame.draw.line(self.screen, COLOR_GHOST, (x - 15, y), (x + 15, y), 4)

            elif self.build_mode == 'settle':
                # Draw black circles on all disallowed spots due to adjacency
                disallowed = set()
                for idx in self.node_ownership:
                    for neighbor in self.board.node_adjacency.get(idx, []):
                        if neighbor not in self.node_ownership:
                            disallowed.add(neighbor)

                # Draw disallowed spots in black
                for i in disallowed:
                    x, y = self.pos_nodes[i]
                    pygame.draw.circle(self.screen, (0, 0, 0), (int(x), int(y)), 10, 1)

                # Then draw allowed ghost spots
                p = self.engine.players[self.selected_player]
                for i, (x, y) in enumerate(self.pos_nodes):
                    if self.is_valid_settlement(p, i):
                        pygame.draw.circle(self.screen, COLOR_GHOST, (int(x), int(y)), 10)


            elif self.build_mode == 'upgrade':
                for i, (x, y) in enumerate(self.pos_nodes):
                    p = self.engine.players[self.selected_player]
                    if p.node_states[i] == "settlement":
                        pygame.draw.rect(self.screen, COLOR_GHOST, pygame.Rect(x - 10, y - 10, 20, 20))

        # Draw node index labels for debugging
        if self.show_node_ids:
            for i, (x, y) in enumerate(self.pos_nodes):
                label = self.font.render(str(i), True, (0, 0, 0))
                self.screen.blit(label, (x + 8, y + 8))  # Offset so it doesn't overlap the circle

    def current_player(self):
        return self.engine.players[self.current_turn % self.num_players]
    
    def get_round_and_turn(self):
        if self.phase == 'setup':
            # Use current_turn directly, count from 0
            round_num = 0
            turn_in_round = (self.current_turn % self.num_players) + 1
        else:
            round_num = (self.current_turn // self.num_players) + 1
            turn_in_round = (self.current_turn % self.num_players) + 1
        return round_num, turn_in_round
    
    def log_prefix(self):
        r, t = self.get_round_and_turn()
        player = self.engine.players[self.setup_player_index()] if self.phase == 'setup' else self.current_player()
        return f"[Round {r} - Turn {t}] Player {player.name}"
    
    def roll_dice(self):
        self.dice_result = random.randint(1, 6) + random.randint(1, 6)
        self.roll_active = False
        print(f"[Game] Dice rolled: {self.dice_result}")

        if self.phase == "game" and self.dice_result != 7:
            popup_log = []

            for tile in self.board.tiles:
                if tile.number == self.dice_result:
                    print(f"[DEBUG] Tile {tile.resource.name} matched dice roll {self.dice_result}")
                    for node_index in self.get_adjacent_nodes(tile):
                        owner = self.node_ownership.get(node_index)
                        if owner:
                            player_id, structure = owner
                            amount = 2 if structure == "city" else 1
                            self.engine.players[player_id].resources[tile.resource] += amount
                            popup_log.append(f"{self.engine.players[player_id].name} +{amount} {tile.resource.name.title()}")
                            print(f"[DEBUG] {self.engine.players[player_id].name} receives {amount} {tile.resource.name} from node {node_index}")

            if popup_log:
                self.setup_resource_popup = ("Resources: " + ", ".join(popup_log), 3 * 30)

    def run(self):
        """Main loop: handle events, update game, and render each frame."""
        running=True
        while running:
            for ev in pygame.event.get():
                if ev.type==pygame.QUIT: running=False
                elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                    pt = ev.pos
                    print(f"[DEBUG] Mouse click at {pt}")

                    # Handle UI buttons
                    clicked_ui = False
                    for name, rect in self.btn_rect.items():
                        if rect.collidepoint(pt):
                            print(f"[DEBUG] Clicked button '{name}'")
                            clicked_ui = True
                            if name == 'reshuffle':
                                self.board.generate_board()
                                self.board.compute_graph()
                                self.pos_nodes = sorted(self.board.nodes, key=lambda p: (p[1], p[0]))
                                self.pos_edges = sorted(self.board.edges, key=lambda p: (p[1], p[0]))
                                print("[Game] Board reshuffled")
                                print(f"[DEBUG] Reloaded {len(self.pos_nodes)} nodes and {len(self.pos_edges)} edges")
                            elif name == 'clear':
                                self.clear_board()
                            elif name == 'road':
                                self.build_mode = 'road'
                                print(f"{self.log_prefix()} Mode: Road")
                            elif name == 'settle':
                                self.build_mode = 'settle'
                                print(f"{self.log_prefix()} Mode: Settle")
                            elif name == 'upgrade':
                                self.build_mode = 'upgrade'
                                print(f"{self.log_prefix()} Mode: Upgrade")
                            elif name == 'buy':
                                self.buy()
                            elif name in ['dec', 'inc']:
                                self.ui_popup_message = ("Changing player count is not available mid-game.", 180)
                            break  # only break if we hit something

                    if not clicked_ui:
                        print(f"[DEBUG] not clicked_ui")
                        # Roll button
                        if self.roll_rect.collidepoint(pt):
                            print("[DEBUG] Clicked roll button")
                            if self.roll_active and self.phase != 'setup':
                                self.next_turn()
                                self.dice_result = random.randint(1, 6) + random.randint(1, 6)
                                self.engine.roll_dice()
                                print(f"{self.log_prefix()} Rolled {self.dice_result}")
                            elif (not self.roll_active) and self.phase != 'setup':
                                self.roll_active = True
                                print("[DEBUG] Skip trading and placements for now.")
                                ### TODO
                            else:
                                print("[DEBUG] Roll ignored (setup phase or inactive)")
                        
                        # Player stats panel click
                        elif any(r.collidepoint(pt) for r in self.stats_rects):
                            print("[DEBUG] Clicked player stats panel")
                            for i, r in enumerate(self.stats_rects):
                                if r.collidepoint(pt):
                                    self.selected_player = i
                                    print(f"[Game] Selected {self.engine.players[i].name}")
                                    break

                        # Play development cards
                        elif self.phase == 'main' and self.play_buttons:
                            print("[DEBUG] Check DEV cards")
                            for lbl, (btn, play) in self.play_buttons.items():
                                if btn.collidepoint(pt):
                                    print(f"[DEBUG] Clicked dev card: {lbl}")
                                    if play:
                                        self.play_card(lbl)
                                    else:
                                        print(f"{self.log_prefix()} Cannot play {lbl} yet")
                                    break

                        # Not a UI element: treat as board click
                        else:
                            print("[DEBUG] Attempting board piece placement")
                            self.place_piece(pt)

            # Render everything
            self.screen.fill(COLOR_BG)
            self.board.draw(self.screen)
            self.draw_placements()
            self.draw_player_stats()
            self.draw_selected_info()
            # Draw UI and roll button
            for name,label in [('reshuffle','Reshuffle'),('clear','Clear'),('road','Road'),('settle','Settle'),('upgrade','Upgrade'),('buy','Buy')]:
                r=self.btn_rect[name]
                bg=COLOR_ACTIVE_BUTTON_BG if self.build_mode==name else COLOR_BUTTON
                br=COLOR_ACTIVE_BUTTON_BORDER if self.build_mode==name else COLOR_LINE
                pygame.draw.rect(self.screen,bg,r); pygame.draw.rect(self.screen,br,r,2)
                txt=self.font.render(label,True,COLOR_BUTTON_TEXT)
                self.screen.blit(txt,txt.get_rect(center=r.center))
            for name,label in [('dec','-'),('inc','+')]:
                r=self.btn_rect[name]
                pygame.draw.rect(self.screen,COLOR_BUTTON,r); pygame.draw.rect(self.screen,COLOR_LINE,r,2)
                self.screen.blit(self.font.render(label,True,COLOR_BUTTON_TEXT), self.font.render(label,True,COLOR_BUTTON_TEXT).get_rect(center=r.center))
            active = self.roll_active and self.phase != 'setup'
            pygame.draw.rect(self.screen,COLOR_ACTIVE_BUTTON_BG if self.roll_active else COLOR_BUTTON,self.roll_rect)
            pygame.draw.rect(self.screen,COLOR_ACTIVE_BUTTON_BORDER if self.roll_active else COLOR_LINE,self.roll_rect,3)
            rd=self.font.render("Roll Dice",True,COLOR_BUTTON_TEXT)
            self.screen.blit(rd,rd.get_rect(center=self.roll_rect.center))
            if self.dice_result is not None:
                dr=self.font.render(f"Total: {self.dice_result}",True,COLOR_BUTTON_TEXT)
                self.screen.blit(dr,dr.get_rect(midbottom=(self.roll_rect.centerx,self.roll_rect.top-10)))
            self.draw_setup_popup()
            # Show setup phase instructions
            if self.phase == 'setup':
                next_player = self.engine.players[self.setup_player_index()]
                next_action = "settlement" if self.setup_step % 2 == 0 else "road"
                instruction = f"{next_player.name}, place your {next_action}"
                text_surface = self.font.render(instruction, True, (0, 0, 0))
                self.screen.blit(text_surface, (20, SCREEN_HEIGHT - 120))
            self.draw_setup_popup()
            pygame.display.flip()
            self.draw_ui_popup()
            self.clock.tick(30)
        pygame.quit(); sys.exit()

if __name__ == "__main__":
    Game(num_players=3).run()

import pygame
import sys
import math
import random
from enum import Enum, auto

# --- Constants ---
SCREEN_WIDTH, SCREEN_HEIGHT = 1200, 900  # Window dimensions
HEX_RADIUS = 70  # Radius of each hex tile
BOARD_ORIGIN = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)  # Center of the board
SNAP_THRESHOLD = 30  # Pixel distance threshold for snapping clicks to nodes/edges

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

    def draw(self, screen):
        """Draws all hex tiles on provided screen."""
        for tile in self.tiles:
            tile.draw(screen)

    def compute_graph(self):
        """
        Builds lists of unique corner (node) and edge midpoint positions
        used for settlement and road placement.
        """
        self.nodes.clear()
        self.edges.clear()
        for tile in self.tiles:
            # Compute 6 corner points
            corners = []
            for i in range(6):
                ang = math.radians(60 * i - 30)
                pt = (tile.position[0] + HEX_RADIUS*math.cos(ang),
                      tile.position[1] + HEX_RADIUS*math.sin(ang))
                corners.append(pt)
            # Add each corner if not duplicate
            for c in corners:
                if all(math.hypot(c[0]-n[0], c[1]-n[1]) > 1 for n in self.nodes):
                    self.nodes.append(c)
            # Add midpoints of each edge
            for i in range(6):
                a, b = corners[i], corners[(i+1)%6]
                mid = ((a[0]+b[0])/2, (a[1]+b[1])/2)
                if all(math.hypot(mid[0]-e[0], mid[1]-e[1]) > 1 for e in self.edges):
                    self.edges.append(mid)

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
        # Player setup
        self.min_players, self.max_players = 2, 5
        self.num_players = max(self.min_players, min(num_players, self.max_players))
        self.players = []
        self.node_ownership = {}  # node_index -> player_id, 'settlement' or 'city'
        self.edge_ownership = {}  # edge_index -> player_id
        self.selected_player = 0
        self.current_turn = 0
        # UI elements
        self.btn_rect = {}
        self.roll_rect = pygame.Rect(SCREEN_WIDTH-150, SCREEN_HEIGHT-60, 130, 50)
        self.play_buttons = {}
        self.build_mode = 'road'
        self.dice_result = None
        # Whether the roll dice button is active
        self.roll_active = True
        # Fonts
        self.font = pygame.font.SysFont(None, 24)
        self.title_font = pygame.font.SysFont(None, 28)
        self.init_ui()
        self.setup_players()
        self.phase = 'setup'  # Track whether in initial placement or regular game
        self.robber_tile_index = None  # Track robber location

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
        # TODO: Add logic to prevent building next to existing settlements
        # and require road connection after setup phase
        return True

    def is_valid_road(self, player, edge_index):
        # TODO: Ensure road is connected to existing player structures
        return True

    def can_afford(self, player, build_type):
        for res, cost in BUILD_COSTS[build_type].items():
            if player.resources[res] < cost:
                return False
        return True

    def pay_cost(self, player, build_type):
        for res, cost in BUILD_COSTS[build_type].items():
            player.resources[res] -= cost

    def distribute_resources(self):
        for tile in self.board.tiles:
            if tile.number == self.dice_result:
                for node_index in self.get_adjacent_nodes(tile):
                    for p in self.players:
                        if p.node_states[node_index] == "settlement":
                            p.resources[tile.resource.name.lower()] += 1
                        elif p.node_states[node_index] == "city":
                            p.resources[tile.resource.name.lower()] += 2

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
        for p in self.players:
            if p.victory_points >= WINNING_VICTORY_POINTS:
                print(f"[Game Over] {self.current_player().name} wins!")
                pygame.quit()
                sys.exit()

    def place_piece(self, pt):
        # TODO: Wrap this with can_afford + is_valid_*
        # and deduct resources with pay_cost
        pass

    def next_turn(self):
        self.current_turn += 1
        self.handle_roll()
        self.check_win()

    def trade_with_bank(self, player, give_res, get_res):
        if player.resources[give_res] >= 4:
            player.resources[give_res] -= 4
            player.resources[get_res] += 1

    def get_adjacent_nodes(self, tile):
        # TODO: Implement: return node indices adjacent to a given tile
        return []

    def is_active_player(self, player_id):
        return player_id == (self.current_turn % self.num_players)

    def setup_players(self):
        """Assign names, colors, and initialize state arrays for each player."""
        names = random.sample(NAMES, self.num_players)
        for i,name in enumerate(names):
            color = (random.randint(50,255), random.randint(50,255), random.randint(50,255))
            p = Player(i, name, color, len(self.pos_nodes), len(self.pos_edges))
            self.players.append(p)

    def next_turn(self):
        """Advance turn counter and log."""
        self.current_turn += 1
        print(f"{self.log_prefix()}'s turn")

    def clear_board(self):
        """Reset all placement states for each player."""
        for p in self.players:
            p.node_states = ["empty"]*len(self.pos_nodes)
            p.edge_states = ["empty"]*len(self.pos_edges)
            p.update_stats()
        print("[Game] Board cleared")

    def buy(self):
        """Buy a random development card and log purchase."""
        p = self.players[self.selected_player]
        card = random.choice([lbl for lbl,_ in DEV_CARD_OPTIONS])
        p.dev_cards[card].append(self.current_turn)
        print(f"{self.log_prefix()} bought {card}")

    def play_card(self, lbl):
        """Play a bought dev card if eligible and log."""
        p = self.players[self.selected_player]
        for t in p.dev_cards[lbl]:
            if t < self.current_turn:
                p.dev_cards[lbl].remove(t)
                print(f"{self.log_prefix()} played {lbl}")
                break

    def place_piece(self, pt):
        """Handle clicks to place roads, settlements, or upgrade to cities."""
        p = self.players[self.selected_player]
        if self.build_mode == 'road':
            # Find closest edge index
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
            p = self.players[self.selected_player]
            # Optional: check for minimum distance (e.g., no adjacent settlements)
            if not self.is_valid_settlement(p, idx):
                print(f"{self.log_prefix()} invalid settlement location at node {idx}")
                return
            # Check and deduct resources only if not in setup phase
            if self.phase != 'setup':
                if not self.can_afford(p, 'settle'):
                    print(f"{self.log_prefix()} cannot afford a settlement")
                    return
                self.pay_cost(p, 'settle')
            # Place the settlement
            p.node_states[idx] = "settlement"
            self.node_ownership[idx] = (p.id, 'settlement')
            p.update_stats()
            print(f"{self.log_prefix()} built settlement at node {idx}")
        elif self.build_mode == 'upgrade':
            # Upgrade first settlement found
            for i,state in enumerate(p.node_states):
                if state == "settlement":
                    p.node_states[i] = "city"
                    self.node_ownership[i] = (p.id, 'city')
                    p.update_stats()
                    print(f"{self.log_prefix()} upgraded settlement to city at node {i}")
                    break

    def draw_player_stats(self):
        """Draw stats panels for all players at top of screen."""
        self.stats_rects = []
        sx, sy = 20, 80  # Starting x,y
        lh = self.font.get_height()
        bw = 220  # Panel width
        for i,p in enumerate(self.players):
            x = sx + i*(bw + 10)
            y = sy
            rect = pygame.Rect(x-5, y-5, bw, lh*6+10)
            pygame.draw.rect(self.screen, (255,255,255), rect)

            if self.is_active_player(p.id):
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
        p = self.players[self.selected_player]
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
        for p in self.players:
            for i,st in enumerate(p.edge_states):
                if st=='road':
                    x,y=self.pos_edges[i]
                    pygame.draw.line(self.screen,p.color,(x-15,y),(x+15,y),4)
            for i,st in enumerate(p.node_states):
                x,y=self.pos_nodes[i]
                if st=='settlement': pygame.draw.circle(self.screen,p.color,(int(x),int(y)),10)
                elif st=='city': pygame.draw.rect(self.screen,p.color,pygame.Rect(x-10,y-10,20,20))

    def current_player(self):
        return self.players[self.current_turn % self.num_players]
    
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
        return f"[Round {r} - Turn {t}] Player {self.current_player().name}"

    def run(self):
        """Main loop: handle events, update game, and render each frame."""
        running=True
        while running:
            for ev in pygame.event.get():
                if ev.type==pygame.QUIT: running=False
                elif ev.type==pygame.MOUSEBUTTONDOWN and ev.button==1:
                    pt=ev.pos
                    # UI buttons
                    if self.btn_rect['reshuffle'].collidepoint(pt):
                        self.board.generate_board(); self.board.compute_graph(); print("[Game] Board reshuffled")
                    elif self.btn_rect['clear'].collidepoint(pt): self.clear_board()
                    elif self.btn_rect['road'].collidepoint(pt): 
                        self.build_mode='road'
                        print(f"{self.log_prefix()} Mode: Road")
                    elif self.btn_rect['settle'].collidepoint(pt): 
                        self.build_mode='settle'
                        print(f"{self.log_prefix()} Mode: Settle")
                    elif self.btn_rect['upgrade'].collidepoint(pt): 
                        self.build_mode='upgrade'
                        print(f"{self.log_prefix()} Mode: Upgrade")
                    elif self.btn_rect['buy'].collidepoint(pt): self.buy()
                    elif self.btn_rect['dec'].collidepoint(pt) and self.num_players>self.min_players:
                        self.num_players-=1; self.setup_players(); print(f"[Game] Players: {self.num_players}")
                    elif self.btn_rect['inc'].collidepoint(pt) and self.num_players<self.max_players:
                        self.num_players+=1; self.setup_players(); print(f"[Game] Players: {self.num_players}")
                    elif self.roll_rect.collidepoint(pt) and self.roll_active:
                        self.next_turn()
                        self.dice_result=random.randint(1,6)+random.randint(1,6)
                        print(f"{self.log_prefix()} Rolled {self.dice_result}")
                    elif any(r.collidepoint(pt) for r in self.stats_rects):
                        for i,r in enumerate(self.stats_rects):
                            if r.collidepoint(pt): self.selected_player=i; print(f"[Game] Selected {self.players[i].name}"); break
                    elif self.play_buttons:
                        for lbl,(btn,play) in self.play_buttons.items():
                            if btn.collidepoint(pt):
                                if play: self.play_card(lbl)
                                else: 
                                    print(f"{self.log_prefix()} Cannot play {lbl} yet")
                                break
                    else:
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
            pygame.draw.rect(self.screen,COLOR_ACTIVE_BUTTON_BG if self.roll_active else COLOR_BUTTON,self.roll_rect)
            pygame.draw.rect(self.screen,COLOR_ACTIVE_BUTTON_BORDER if self.roll_active else COLOR_LINE,self.roll_rect,3)
            rd=self.font.render("Roll Dice",True,COLOR_BUTTON_TEXT)
            self.screen.blit(rd,rd.get_rect(center=self.roll_rect.center))
            if self.dice_result is not None:
                dr=self.font.render(f"Total: {self.dice_result}",True,COLOR_BUTTON_TEXT)
                self.screen.blit(dr,dr.get_rect(midbottom=(self.roll_rect.centerx,self.roll_rect.top-10)))
            pygame.display.flip(); self.clock.tick(30)
        pygame.quit(); sys.exit()

if __name__ == "__main__":
    Game(num_players=3).run()

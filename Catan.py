import pygame
import sys
import math
import random
from enum import Enum, auto

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 1200, 900
HEX_RADIUS = 70
BOARD_ORIGIN = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
SNAP_THRESHOLD = 30  # pixel distance for snapping

# Colors
COLOR_BG = (245, 222, 179)
COLOR_LINE = (0, 0, 0)
COLOR_BUTTON = (200, 200, 200)
COLOR_BUTTON_TEXT = (0, 0, 0)
COLOR_ACTIVE_BUTTON_BG = (255, 255, 255)
COLOR_ACTIVE_BUTTON_BORDER = (255, 0, 0)
COLOR_PLAYABLE = (0, 200, 0)
COLOR_UNPLAYABLE = (150, 150, 150)

RESOURCE_COLORS = {
    'wood': (34, 139, 34),
    'brick': (178, 34, 34),
    'sheep': (144, 238, 144),
    'wheat': (238, 232, 170),
    'ore': (169, 169, 169),
    'desert': (210, 180, 140)
}

# Generic names for players
NAMES = [
    "Alex", "Jordan", "Taylor", "Morgan", "Casey",
    "Riley", "Jamie", "Cameron", "Drew", "Reese",
    "Quinn", "Avery", "Peyton", "Hayden", "Rowan",
    "Skyler", "Dakota", "Payton", "Finley", "Emerson"
]

# Development card options
DEV_CARD_OPTIONS = [
    ("Knight", ("Knight", "")),
    ("Road Building", ("Road", "Building")),
    ("Year of Plenty", ("Year of", "Plenty")),
    ("Monopoly", ("Monopoly", "")),
    ("Victory Point", ("Victory", "Point"))
]

class Resource(Enum):
    WOOD = auto()
    BRICK = auto()
    SHEEP = auto()
    WHEAT = auto()
    ORE = auto()
    DESERT = auto()

class Tile:
    def __init__(self, res, number, pos):
        self.resource = res
        self.number = number
        self.position = pos

    def draw(self, screen):
        pts = []
        for i in range(6):
            ang = math.radians(60 * i - 30)
            pts.append((
                self.position[0] + HEX_RADIUS * math.cos(ang),
                self.position[1] + HEX_RADIUS * math.sin(ang)
            ))
        pygame.draw.polygon(screen, RESOURCE_COLORS[self.resource.name.lower()], pts)
        pygame.draw.polygon(screen, COLOR_LINE, pts, 2)
        if self.number is not None:
            font = pygame.font.SysFont(None, 28)
            text = font.render(str(self.number), True, COLOR_BUTTON_TEXT)
            screen.blit(text, text.get_rect(center=self.position))

class Board:
    def __init__(self):
        self.tiles = []
        self.nodes = []
        self.edges = []
        self.generate_board()
        self.compute_graph()

    def generate_board(self):
        print("[Game] Board reshuffled")
        self.tiles.clear()
        res_pool = ([Resource.WOOD] * 4 + [Resource.BRICK] * 3 +
                    [Resource.SHEEP] * 4 + [Resource.WHEAT] * 4 +
                    [Resource.ORE] * 3 + [Resource.DESERT])
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
        for tile in self.tiles:
            tile.draw(screen)

    def compute_graph(self):
        self.nodes.clear()
        self.edges.clear()
        for tile in self.tiles:
            corners = []
            for i in range(6):
                ang = math.radians(60 * i - 30)
                corners.append((
                    tile.position[0] + HEX_RADIUS * math.cos(ang),
                    tile.position[1] + HEX_RADIUS * math.sin(ang)
                ))
            for c in corners:
                if all(math.hypot(c[0]-n[0], c[1]-n[1]) > 1 for n in self.nodes):
                    self.nodes.append(c)
            for i in range(6):
                a, b = corners[i], corners[(i+1)%6]
                mid = ((a[0]+b[0])/2, (a[1]+b[1])/2)
                if all(math.hypot(mid[0]-e[0], mid[1]-e[1]) > 1 for e in self.edges):
                    self.edges.append(mid)

class Player:
    def __init__(self, idx, name, color):
        self.id = idx
        self.name = name
        self.color = color
        self.resources = {r: 0 for r in Resource}
        self.dev_cards = {lbl: [] for lbl, _ in DEV_CARD_OPTIONS}
        self.roads = []
        self.settlements = []
        self.cities = []
        self.longest_road = 0
        self.victory_points = 0

    @property
    def card_count(self):
        return sum(self.resources.values())

    def update_stats(self):
        self.victory_points = len(self.settlements) + 2 * len(self.cities)
        self.longest_road = len(self.roads)

class Game:
    def __init__(self, num_players=3):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Catan")
        self.clock = pygame.time.Clock()
        self.board = Board()
        self.min_players, self.max_players = 2, 5
        self.num_players = max(self.min_players, min(num_players, self.max_players))
        self.players = []
        self.selected_player = 0
        self.stats_rects = []
        self.current_turn = 0
        self.setup_players()
        self.font = pygame.font.SysFont(None, 24)
        self.title_font = pygame.font.SysFont(None, 28)
        btns = [
            ('reshuffle', 20, 20, 160, 40),
            ('clear', 200, 20, 160, 40),
            ('road', 380, 20, 120, 40),
            ('settle', 510, 20, 120, 40),
            ('upgrade', 640, 20, 120, 40),
            ('buy', 770, 20, 120, 40),
            ('dec', 900, 20, 40, 40),
            ('inc', 950, 20, 40, 40)
        ]
        self.btn_rect = {name: pygame.Rect(x, y, w, h) for name, x, y, w, h in btns}
        self.roll_rect = pygame.Rect(SCREEN_WIDTH-150, SCREEN_HEIGHT-60, 130, 50)
        self.roll_active = True
        self.dice_result = None
        self.build_mode = 'road'
        # Initialize play buttons dict
        self.play_buttons = {}

    def setup_players(self):
        names = random.sample(NAMES, self.num_players)
        self.players = [Player(i, n, (random.randint(50,255), random.randint(50,255), random.randint(50,255))) for i, n in enumerate(names)]

    def next_turn(self):
        self.current_turn += 1
        print(f"[Turn {self.current_turn}] Starting turn")

    def clear_board(self):
        print("[Game] Board cleared")
        for p in self.players:
            p.roads.clear()
            p.settlements.clear()
            p.cities.clear()
            p.update_stats()

    def buy(self):
        p = self.players[self.selected_player]
        card = random.choice([lbl for lbl, _ in DEV_CARD_OPTIONS])
        p.dev_cards[card].append(self.current_turn)
        print(f"[Turn {self.current_turn}] Player {p.name} bought {card}")

    def play_card(self, lbl):
        p = self.players[self.selected_player]
        turns = p.dev_cards[lbl]
        for t in turns:
            if t < self.current_turn:
                turns.remove(t)
                print(f"[Turn {self.current_turn}] Player {p.name} played {lbl}")
                break

    def place_piece(self, pt):
        p = self.players[self.selected_player]
        if self.build_mode == 'road':
            cand = min(self.board.edges, key=lambda e: math.hypot(pt[0]-e[0], pt[1]-e[1]))
            dist = math.hypot(pt[0]-cand[0], pt[1]-cand[1])
            if dist < SNAP_THRESHOLD and cand not in p.roads and (
               not(p.roads or p.settlements or p.cities) or any(
                   math.hypot(cand[0]-e[0], cand[1]-e[1]) < SNAP_THRESHOLD for e in p.roads + p.settlements + p.cities)):
                p.roads.append(cand)
                p.update_stats()
                print(f"[Turn {self.current_turn}] Player {p.name} built Road at {cand}")
            else:
                print(f"[Turn {self.current_turn}] Road placement invalid")
        elif self.build_mode == 'settle':
            cand = min(self.board.nodes, key=lambda n: math.hypot(pt[0]-n[0], pt[1]-n[1]))
            dist = math.hypot(pt[0]-cand[0], pt[1]-cand[1])
            if dist < SNAP_THRESHOLD and cand not in p.settlements and cand not in p.cities:
                p.settlements.append(cand)
                p.update_stats()
                print(f"[Turn {self.current_turn}] Player {p.name} built Settlement at {cand}")
            else:
                print(f"[Turn {self.current_turn}] Settlement placement invalid")
        elif self.build_mode == 'upgrade':
            if p.settlements:
                cand = p.settlements.pop()
                p.cities.append(cand)
                p.update_stats()
                print(f"[Turn {self.current_turn}] Player {p.name} upgraded to City at {cand}")
            else:
                print(f"[Turn {self.current_turn}] No settlement to upgrade")

    def roll_dice(self):
        self.next_turn()
        self.dice_result = random.randint(1,6) + random.randint(1,6)
        print(f"[Turn {self.current_turn}] Rolled dice: {self.dice_result}")

    def draw_player_stats(self):
        self.stats_rects.clear()
        sx, sy = 20, 80
        lh = self.font.get_height()
        bw = 220
        for i, p in enumerate(self.players):
            x = sx + i*(bw+10)
            y = sy
            rect = pygame.Rect(x-5, y-5, bw, lh*6+10)
            pygame.draw.rect(self.screen, (255,255,255), rect)
            pygame.draw.rect(self.screen, p.color, rect, 3)
            self.stats_rects.append(rect)
            self.screen.blit(self.title_font.render(p.name, True, p.color), (x, y))
            stats = [f"VP: {p.victory_points}", f"Cards: {p.card_count}", f"LR: {p.longest_road}", f"R: {len(p.roads)}", f"C: {len(p.cities)}"]
            for j, t in enumerate(stats, start=1):
                self.screen.blit(self.font.render(t, True, COLOR_BUTTON_TEXT), (x+5, y+j*lh))

    def draw_selected_info(self):
        # Display selected player's resource and dev card info, with play buttons for all except Victory Point
        if self.selected_player is None:
            return
        p = self.players[self.selected_player]
        info_height = 100
        y0 = SCREEN_HEIGHT - info_height
        info_width = SCREEN_WIDTH - (self.roll_rect.width + 20)
        pygame.draw.rect(self.screen, (220, 220, 220), (0, y0, info_width, info_height))

        lh = self.font.get_height()
        y1, y2, y3 = y0 + 5, y0 + 5 + lh, y0 + 5 + 2 * lh

        # Prepare slots: resources then all dev cards including Victory Point
        slots = [r for r in Resource if r != Resource.DESERT] + [lbl for lbl, _ in DEV_CARD_OPTIONS]
        spacing = info_width // (len(slots) + 1)
        x = spacing
        # Reset play_buttons
        self.play_buttons.clear()

        for s in slots:
            if isinstance(s, Resource):
                # Resource name and count
                name_str = s.name.title()
                name_surf = self.font.render(name_str, True, COLOR_BUTTON_TEXT)
                name_rect = name_surf.get_rect(center=(x, (y1 + y2) // 2))
                self.screen.blit(name_surf, name_rect)
                cnt = p.resources[s]
                cnt_surf = self.font.render(str(cnt), True, COLOR_BUTTON_TEXT)
                cnt_rect = cnt_surf.get_rect(center=(x, y3))
                self.screen.blit(cnt_surf, cnt_rect)
            else:
                # Dev card lines
                for lbl, lines in DEV_CARD_OPTIONS:
                    if lbl == s:
                        line_a, line_b = lines
                        break
                a_surf = self.font.render(line_a, True, COLOR_BUTTON_TEXT)
                b_surf = self.font.render(line_b, True, COLOR_BUTTON_TEXT)
                a_rect = a_surf.get_rect(center=(x, y1))
                b_rect = b_surf.get_rect(center=(x, y2))
                self.screen.blit(a_surf, a_rect)
                self.screen.blit(b_surf, b_rect)
                # Count
                cnt = len(p.dev_cards[s])
                cnt_surf = self.font.render(str(cnt), True, COLOR_BUTTON_TEXT)
                cnt_rect = cnt_surf.get_rect(center=(x, y3))
                self.screen.blit(cnt_surf, cnt_rect)
                # Only show play button for non-Victory cards
                if s != "Victory Point":
                    btn_rect = pygame.Rect(cnt_rect.left, y3 + 5, cnt_rect.width, 20)
                    playable = any(turn < self.current_turn for turn in p.dev_cards[s])
                    color = COLOR_PLAYABLE if playable else COLOR_UNPLAYABLE
                    pygame.draw.rect(self.screen, color, btn_rect, 2)
                    self.play_buttons[s] = (btn_rect, playable)
            x += spacing

    def draw_placements(self):
        for p in self.players:
            for e in p.roads: pygame.draw.line(self.screen,p.color,(e[0]-15,e[1]),(e[0]+15,e[1]),4)
            for n in p.settlements: pygame.draw.circle(self.screen,p.color,n,10)
            for n in p.cities: pygame.draw.rect(self.screen,p.color,pygame.Rect(n[0]-10,n[1]-10,20,20))

    def run(self):
        running=True
        while running:
            for ev in pygame.event.get():
                if ev.type==pygame.QUIT:
                    running=False
                elif ev.type==pygame.MOUSEBUTTONDOWN and ev.button==1:
                    pt=ev.pos
                    if self.btn_rect['reshuffle'].collidepoint(pt):
                        self.board.generate_board();self.board.compute_graph()
                    elif self.btn_rect['clear'].collidepoint(pt):
                        self.clear_board()
                    elif self.btn_rect['road'].collidepoint(pt):
                        self.build_mode='road';print(f"[Turn {self.current_turn}] Mode: Road")
                    elif self.btn_rect['settle'].collidepoint(pt):
                        self.build_mode='settle';print(f"[Turn {self.current_turn}] Mode: Settle")
                    elif self.btn_rect['upgrade'].collidepoint(pt):
                        self.build_mode='upgrade';print(f"[Turn {self.current_turn}] Mode: Upgrade")
                    elif self.btn_rect['buy'].collidepoint(pt):
                        self.buy()
                    elif self.btn_rect['dec'].collidepoint(pt) and self.num_players>self.min_players:
                        self.num_players-=1;self.setup_players();print(f"[Game] Players: {self.num_players}")
                    elif self.btn_rect['inc'].collidepoint(pt) and self.num_players<self.max_players:
                        self.num_players+=1;self.setup_players();print(f"[Game] Players: {self.num_players}")
                    elif self.roll_rect.collidepoint(pt) and self.roll_active:
                        self.roll_dice()
                    elif any(r.collidepoint(pt) for r in self.stats_rects):
                        for i,r in enumerate(self.stats_rects):
                            if r.collidepoint(pt):
                                self.selected_player=i;print(f"[Game] Selected {self.players[i].name}")
                                break
                    elif self.play_buttons:
                        for lbl,(btn,play) in self.play_buttons.items():
                            if btn.collidepoint(pt):
                                if play: self.play_card(lbl)
                                else: print(f"[Turn {self.current_turn}] Cannot play {lbl} yet")
                                break
                    else:
                        self.place_piece(pt)
            # DRAW FRAME
            self.screen.fill(COLOR_BG)
            self.board.draw(self.screen)
            self.draw_placements()
            for name,label in [('reshuffle','Reshuffle'),('clear','Clear'),('road','Road'),('settle','Settle'),('upgrade','Upgrade'),('buy','Buy')]:
                r=self.btn_rect[name]
                bg=COLOR_ACTIVE_BUTTON_BG if name==self.build_mode else COLOR_BUTTON
                br=COLOR_ACTIVE_BUTTON_BORDER if name==self.build_mode else COLOR_LINE
                pygame.draw.rect(self.screen,bg,r);pygame.draw.rect(self.screen,br,r,2)
                txt=self.font.render(label,True,COLOR_BUTTON_TEXT)
                self.screen.blit(txt,txt.get_rect(center=r.center))
            for name,label in [('dec','-'),('inc','+')]:
                r=self.btn_rect[name]
                pygame.draw.rect(self.screen,COLOR_BUTTON,r);pygame.draw.rect(self.screen,COLOR_LINE,r,2)
                txt=self.font.render(label,True,COLOR_BUTTON_TEXT)
                self.screen.blit(txt,txt.get_rect(center=r.center))
            self.draw_player_stats()
            self.draw_selected_info()
            if self.roll_active:
                pygame.draw.rect(self.screen,COLOR_ACTIVE_BUTTON_BG,self.roll_rect)
                pygame.draw.rect(self.screen,COLOR_ACTIVE_BUTTON_BORDER,self.roll_rect,3)
            else:
                pygame.draw.rect(self.screen,COLOR_BUTTON,self.roll_rect)
                        # Roll button label
            rd = self.font.render("Roll Dice", True, COLOR_BUTTON_TEXT)
            self.screen.blit(rd, rd.get_rect(center=self.roll_rect.center))
            # Dice result display
            if self.dice_result is not None:
                dr = self.font.render(f"Total: {self.dice_result}", True, COLOR_BUTTON_TEXT)
                self.screen.blit(dr, dr.get_rect(midbottom=(self.roll_rect.centerx, self.roll_rect.top-10)))

            # Update display and tick
            pygame.display.flip()
            self.clock.tick(30)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    Game(num_players=3).run()


# CATAN_AI
CATAN made by chatgpt for battle offs

# Catan Python Game (Pygame)

A simplified version of the board game *Catan* implemented using Python and Pygame.

---

## ✅ New Features Added 12/05/25

### 🧙 Knight Development Card Support
- **Knight card now playable** from the dev card bar.
- Playing a Knight:
  - Triggers robber mode.
  - Lets player select a tile to move the robber.
  - Steals a card from adjacent players.
- Fixed bug where `play_card()` was overwritten and didn’t execute effects.
- Updated click detection to allow Knight use during `self.phase == 'game'` (was incorrectly checking for `'main'`).

### 🦹 Robber Placement & Stealing Logic
- **Robber mode fully implemented**:
  - Triggered by rolling a 7 or playing a Knight.
  - Prompts player to click a tile to move the robber.
  - Robber is drawn as a black circle on the selected tile.
- **Card stealing**:
  - Automatically steals a random resource from an adjacent player.
  - If multiple valid victims, prompts player to choose by clicking their stat panel.
- **Click routing fixes**:
  - Robber tile placement is now prioritized and cannot be blocked by dev card or stat panel clicks.
  - Prevents crashes from invalid `robber_tile_index`.

### 👤 Player Selection Display
- Bottom-left HUD now shows:
  - `Viewing: <PlayerName>` indicating which player’s stats/resources you are looking at.
- Updates dynamically when a player stat panel is clicked.

### 🛠️ Input Handling Fixes (Robber Flow)
- **Click priority order updated**:
  - Robber tile click → victim click → dev card click → roll → stats → board.
  - Ensures clicks are routed correctly during robber phase.
- Added `return`/`break` control flow to prevent fallthrough into piece placement during robber interaction.

---

## ✅ New Features Added 11/05/25

### 🌊 Harbour System Introduced
- **Harbours Implemented**:
  - Added a `Harbour` class to represent trading ports.
  - Ports are attached to **pairs of coastal nodes** and positioned **outside the board edge**, pointing inward.
  - Rendered with a blue circle and two connection lines back to nodes.
- **Random Harbour Placement**:
  - `harbour_node_pairs` is now randomized with `random.shuffle()`.
  - Ensures harbours are distributed differently each game.
- **Resource & 3:1 Port Types**:
  - Nine harbour types supported (e.g. "2:1 wood", "3:1", etc.).
  - Types are shuffled alongside node pairs.

### 📈 Debugging & Visual Enhancements
- **Node ID Labels Toggle**:
  - `SHOW_NODE_IDS = True` enables labels for each node index.
  - Helps visualize harbour connections and debug placements.
- **Harbour-to-Node Debug Output**:
  - Console shows which nodes each harbour connects to, with distances.

### 🧱 UI/UX Improvements
- **Player Stats Realignment**:
  - Player stat panels now stack **vertically on the left** instead of top horizontal.
  - Prevents overlap with top-edge harbours or tiles.
- **Dock Placement Visuals**:
  - Harbours now draw correctly:
    - **Dock circle is pushed outside** the board.
    - **Lines connect back** to coastal nodes.
    - Text labels display the trade type.

### 🔁 Board Architecture Improvements
- **Tile-to-Node Graph Rewritten**:
  - `compute_graph()` now:
    - Deduplicates node coordinates precisely.
    - Tracks node adjacency (for valid placement checking).
    - Remaps all node indices to maintain consistent ordering.
- **Graph-Aware Harbour Placement**:
  - Harbours snap to existing graph nodes instead of arbitrary positions.
  - Eliminates tile-center-based approximation.

---

## 🐞 Fixes & Refactors

- ❌ Fixed: Harbour `draw()` previously attempted to use `self.nodes` (which it didn’t own).
- ✅ Now draws harbour lines inside `Board.draw()` using known node coordinates.
- 🧹 Refactored `Board.__init__()` to ensure `compute_graph()` runs **before** `generate_harbours()`, fixing missing node issues.
- ✅ Cleaned up constructor argument mismatch for `Harbour` class (now accepts `node_indices`).
- 🧪 Improved debug logging structure with centralized `Debug_And_Log` class (early stub added for future use).

---

## 🛠️ In Progress / To Do

- [ ] Use **auto-detected coastal nodes** for harbour placement instead of hardcoding node indices.
- [ ] Integrate harbour ownership rules (e.g. trade eligibility if player has a settlement on connected node).
- [ ] Add hover or tooltip UI to explain harbour trade rates during gameplay.


---

## ✅ New Features Added 9/05/25

### 🏗️ Setup Phase Overhaul
- **Setup Phase Introduced**:
  - Players take turns placing settlements and roads in a 1 → N → 1 snake order.
  - Tracked using `self.phase = 'setup'` and `self.setup_step = 0`.
  - Ends automatically and transitions to main gameplay after 2 settlements + 2 roads per player.
- **Turn Indicator in Setup**:
  - Setup now highlights the correct player’s panel (green) during placement.
  - Instructional text displayed at the bottom: `"Player X, place your settlement/road"`.

### 🧪 Debugging & Placement Fixes
- **Debug Logging**:
  - Added click logging: `"[DEBUG] Clicked at (x, y)"`.
  - Logs closest node and distance for click validation.
  - Logs placement events: `"Player X placed settlement at node Y"`.
- **Improved Proximity Handling**:
  - Set `SNAP_THRESHOLD = 100` to allow more forgiving placement clicks.
  - Prevents placement if too far from node or edge.

### 🛠️ Input Handling Fixes
- **UI Interaction Fixes**:
  - Replaced faulty `for...break` button logic with `clicked_ui` flag for accurate event routing.
  - Ensures `self.place_piece(pt)` is called when no UI button was clicked.
- **Dev Card UI Bug Fixed**:
  - Dev card buttons no longer intercept all clicks during setup.
  - `self.play_buttons` is only checked in main phase (`self.phase == 'main'`).

### 🔁 Board Sync Improvements
- **Board Reset Now Resyncs Graph**:
  - Clicking "Reshuffle" now resets `self.pos_nodes` and `self.pos_edges` to match new board layout.

---

## ✅ New Features Added 7/05/25

### 🎮 Gameplay Mechanics
- **Turn & Round Tracking**: Logs are now formatted as `Round X - Turn Y`, with a special `Round 0` for the setup phase.
- **Player Turn Indicator**: Active player's stat panel is highlighted in green; others are shown in grey.
- **Ownership Tracking**:
  - `node_ownership`: Stores who owns each node (settlement or city).
  - `edge_ownership`: Stores who owns each edge (road).
- **Settlement Placement Rules**:
  - Checks for node occupancy before placing.
  - Differentiates setup vs normal phase (resource cost deduction only in normal play).
  - Logs action with round and player details.

### 🛠️ Build Mode UI/UX
- **Neutral Starting Mode**: Game begins with no build mode selected to avoid ghost preview clutter.
- **Ghost Previews**:
  - Roads: Grey lines shown only in `'road'` mode where no road exists.
  - Settlements: Grey circles shown only in `'settle'` mode at unclaimed nodes.
  - Upgrades: Grey squares shown in `'upgrade'` mode on the player’s own settlements.

### 🧠 Helper Functions
- `get_round_and_turn()`: Computes round number and player turn within round.
- `log_prefix()`: Standardizes log messages to include round, turn, and player.
- `current_player()`: Returns the player whose turn it currently is.

---

## 🔜 Planned Features
- Legal placement enforcement (e.g., no adjacent settlements).
- Robber logic on rolling a 7.
- Resource distribution based on tile numbers.
- Full development card effects (Monopoly, Year of Plenty, Knight, etc.).
- Enforced road connectivity.
- Win condition (e.g., 10 victory points).

---

## 💡 How to Play

1. Run the script:

   ```bash
   python Catan.py

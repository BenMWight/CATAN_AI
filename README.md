# CATAN_AI
CATAN made by chatgpt for battle offs

# Catan Python Game (Pygame)

A simplified version of the board game *Catan* implemented using Python and Pygame.

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

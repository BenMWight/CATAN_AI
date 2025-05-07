# CATAN_AI
CATAN made by chatgpt for battle offs

# Catan Python Game (Pygame)

A simplified version of the board game *Catan* implemented using Python and Pygame.

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

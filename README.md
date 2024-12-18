# Battleship Game

## Game Modes
- **Multiplayer**: Two players play against each other.
- **Singleplayer**: One player competes against the computer.

## Game Board
- The grid is a 10x10 board.
- **Vertical columns** are marked by letters (A-J).
- **Horizontal rows** are marked by numbers (1-10).

### Board Layout:
```
A
B
C
D
E
F
G
H
I
J
   1   2   3   4   5   6   7   8   9   10
```

## Ship Sizes
- **Submarine**: Size 2
- **Cruiser**: Size 3
- **Battleship**: Size 4
- **Destroyer**: Size 4
- **Air Carrier**: Size 5

## Game Setup
### Multiplayer
1. Two players take turns to place their ships on the 10x10 grid.
2. **Player 1** places their 5 ships first.
3. **Player 2** then places their 5 ships.

### Singleplayer
1. The player places their 5 ships on the 10x10 grid.
2. The computer places its 5 ships randomly (ships cannot overlap).

## Game Description
1. The game begins once both players (or the computer) have placed all their ships.
2. **Player 1** starts by choosing a grid location to attack with a bomb.
3. If Player 1 hits an opponent's ship:
   - They get a streak and can take another turn.
4. If Player 1 misses:
   - It becomes Player 2’s turn (or the computer's turn in singleplayer).
5. When all the cells of a ship are hit, the ship sinks.
6. The first player to sink all of their opponent’s ships wins the game.

### Example Gameplay
- **You**: "Bomb on D-4"
- **Opponent**: "D-4 Hit on Destroyer"
- **You**: "Bomb on F-1"
- **Opponent**: "F-1 Miss"

## Rules
### General Rules
1. Players cannot target their own ships.
2. Players cannot change ship positions after the game starts.
3. Players must announce when their ship is hit and identify the ship name.
4. Players must not look at each other’s screens while placing ships.

### Ship Placement Rules
1. Ships must be placed either horizontally or vertically (not diagonally).
2. Ships cannot overlap with each other, cross the grid boundaries, or overlap row/column markers.
3. Once placed, ship positions cannot be changed.

### Winning Conditions
- A player wins by sinking all five of their opponent’s ships.

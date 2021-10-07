# Block-The-Pig-Bot

Simulates [Block the Pig](https://www.coolmathgames.com/0-block-the-pig), a hex grid maze-like game. In the original game, the player is allowed two free moves to block in the grid, where each subsequent block the pig can move. The game ends once the pig reaches an edge, or the player completely restricts the pig from reaching an edge.
![gameComparison](https://user-images.githubusercontent.com/70815649/136258625-01b810d5-04cb-4a54-83ad-7d86588e78b2.PNG)_Real game v.s. Simulation_


The core part of this project, however, is the Bot that plays against the pig. The bot can simulate the games, either visually or silently, to choose the next "best" block that will ensure a win.

To achieve all of this, the project features:
* HexMap Creation(Including Graphs and Algorithms), through an incredibly useful [reference](https://www.redblobgames.com/grids/hexagons/).
* Image Recognition and Manipulation, reading in the webgame data and converting it into useful information.
* A Bot using Monte-Carlo Tree Search, playing through multiple games to determine the next "best" block that achieves an absolute win.
* 32 different games for testing and debugging (all read from webgame).

## Performance
Currently, the bot is able to simulate 32 different games in ~20 seconds. Although this is acceptable, I believe that the simulation can be done much faster by optimizing floodfill, pig's path-finding, and **game state copying**. Moreover, heavy bottle-necks sometimes occur at the beginning stages of the game (where bot has 2 free moves) because of the sheer computation size.

The bot can reach upwards of 22 rounds using its current algorithms and logic. Accuracy could be improved by simulating pig's mobility options after forcing moves (where bot must block an immediate edge to prevent pig win), however this would come at a HEAVY cost of run time. Run time optimizations must be done before this is possible.

## Algorithms
In the webgame, the pig takes a somewhat predictable path: the shortest path towards an edge. **However, it will not necessarily take the most OPTIMAL path**. If the pig were presented two paths, one that lead to 1 possible win and another leading to 3, the probability between the two would be 50/50. This means that at every point where the pig has multiple mobility options, player must choose subsequent blocks that lead to an absolute victory. 

To shorten this calculation, the Bot uses Monte-Carlo Tree Search through selection, expansion, simulation, and backup. In selection, Bot tests a potential block and scores the game state with a heuristic function. If there is potential in the block (score is above certain threshold), the Bot moves onto expansion and simulation. It runs through the pig's mobility options, repeating back from selection->simulation until...
1. Absolute win is achieved
2. Possible loss occurs

at which point Bot terminates branch and backs up into previous game state. I believe the back up process is the bottle-neck right now, as it uses python's deepcopy at two different points to save and load previous game states.

## Program In Action


## What's Next
_Not in any particular importance or order to be done_
1. Fixing the FloodFill implementation
2. Optimizing and cleaning up Pig's path finding
3. Optimizing the simulation speed of the different games (by improving game state copying)
4. Optimize performance bottle-necks at "free block" stage of the game
5. Splitting the functions and classes into multiple files
6. **CLEANING UP CODE IN THE BOT FUNCTIONS AND CLASSES**
7. Improving the initial image capture (5 seconds to capture webgame and convert to data)
8. Have program recognize pig's position in webgame
9. Debugging memory leak when running visually
10. Have simulation more accurately mimic real game

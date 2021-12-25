# Block-The-Pig-Bot

Simulates [Block the Pig](https://www.coolmathgames.com/0-block-the-pig), a hex grid maze-like game. In the original game, the player is allowed two free moves to block in the grid, where each subsequent block results in a pig move. The game ends once the pig reaches an edge, or the player completely restricts the pig from reaching an edge.
![gameComparison](https://user-images.githubusercontent.com/70815649/136258625-01b810d5-04cb-4a54-83ad-7d86588e78b2.PNG)_Real game v.s. Simulation_


The core part of this project, however, is the Bot that plays against the pig. The bot can simulate the games, either visually or silently, to choose the next "best" block that will ensure a win.

To achieve all of this, the project features:
* HexMap Creation(Including Graphs and Algorithms), through an incredibly useful [reference](https://www.redblobgames.com/grids/hexagons/).
* Image Recognition and Manipulation, reading in the webgame data and converting it into useful information.
* A Bot using Monte-Carlo Tree Search, playing through multiple games to determine the next "best" block that achieves an absolute win.
* 34 different games for testing and debugging (all read from webgame).

## Performance
Currently, the bot is able to simulate 34 different games in ~2 seconds. This time is a massive improvement over the previous simulation speed (20 seconds) and came as a result of improving the game state copying. Still, heavy bottle-necks sometimes occur at the beginning stages of the game (where bot has 2 free moves) because of the computation depth, preventing the program from running under a second.

Due to the optimizations in simulation speed, accuracy has improved as well. More pig mobility options can be excercised in various positions while maintaining a efficient runtime, allowing the bot to achieve "perfect" games where no pig move leads to a victory. As a result, the round limit should theoretically be unbounded; however, two errors are preventing this from occurring: dynamic computer vision/automation and inaccurate block detection.

## Algorithms
In the webgame, the pig takes a somewhat predictable path: the shortest path towards an edge. **However, it will not necessarily take the most OPTIMAL path**. If the pig were presented two paths, one that lead to 1 possible win and another leading to 3, the probability between the two would be 50/50. This means that at every point where the pig has multiple mobility options, player must choose subsequent blocks that lead to an absolute victory. 

To shorten this calculation, the Bot uses Monte-Carlo Tree Search through selection, expansion, simulation, and backup. In selection, Bot tests a potential block and scores the game state with a heuristic function. If there is potential in the block (score is above certain threshold), the Bot moves onto expansion and simulation. It runs through the pig's mobility options, repeating back from selection->simulation until...
1. Absolute win is achieved
2. Possible loss occurs

at which point Bot terminates branch and backs up into previous game state. Right now, the two things preventing the bot from winning every grame are the faulty block detection and input automation. There is just one, one singular block that is often read incorrectly when acquiring webgame data. Moreover, the bot is still not programmed to automate the game, only made to simulate games for the user. Thus, if any deviations in the actual game occurred, the moves made would still be correct but with differing orders.

## Program In Action


## What's Next
_Not in any particular importance or order to be done_
1. ~~Improving the FloodFill implementation and its corresponding data structure~~
2. ~~Optimizing and cleaning up Pig's path finding~~
3. ~~Optimizing the simulation speed of the different games (by improving game state copying)~~
4. Optimize performance bottle-necks at "free block" stage of the game
5. ~~Splitting the functions and classes into multiple files~~
6. **CLEANING UP CODE IN THE BOT FUNCTIONS AND CLASSES**
7. ~~Improving the initial image capture (5 seconds to capture webgame and convert to data)~~
8. ~~Have program recognize pig's position in webgame~~
9. ~~Debugging memory leak when running visually~~
10. ~~Have simulation more accurately mimic real game~~
11. Fix the incorrect block detection for the one tile
12. Implement bot automation so bot can play webgame without user input

######(Dec 2021 Update)
As of December, performance has improved from 4 seconds to 2 seconds as a result of optimizing floodFill and optimalPath function implementations. 

floodFill function only returns blocks from paths that lead to best win and second best win instead of all tiles in some vicinity. After some testing, I realized that there were blocks that would be completely detrimental to bot, allowing the pig a free move. These blocks were considered in each branching game state and delved into, costing a lot of computation time.

The optimalPath function, meanwhile, suffered from a bad initial implementation. I had used a depth first search algorithm to have the pig find the best path, but upon further thought using another bfs would be the best. This was because ALL the edges lead to a win, so it would have been better to expand level by level.

# AppleGame
Macro to solve Applegame automatically. https://www.gamesaien.com/game/fruit_box_a/.

## How to use
### GUI
> GUI mode. Distinctive Scan, Search, Run supported.

```sh
python main.py -g
```

### CLI
```
python main.py <args>
```
### Search arguments (must-have)
- `-i`: Iterative Search
- `-n`: N-Iterative Search
- `-r`: Recursive Iterative Search
- `-h`: Heuristic Iiterative Search
- `-e`: Exhaustive Search

### Dev mode
Dev mode can be configured with argument `--dev`
- `--v`: Verbose Mode(Not Implemented yet)
- `--e`: Execute(If dev mode is activated and Execute is not configured, then it will just search and not run)
- `--s <iteration>`: Summarize Searching Algorithms
  - Summary mode makes excel file in current directory, which summarizes multiple runs with every searching algorithm.

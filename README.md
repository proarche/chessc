# chessc
A basic tool to check how well chess moves correlate to engine suggestions.

## Requirements
### This script requires the `chess` library, you can install it with:
```pip install chess```
### also requires chess engines to analyse the positions, you can add them on the code on `chessc.py`:
original code:
```
STOCKFISH_PATH = "./engines/stockfish_15_linux_x64/stockfish_15_x64"
KOMODO_PATH = "./engines/komodo-13_201fd6/Linux/komodo-13.02-linux"
ENGINE_PATHS = [STOCKFISH_PATH, KOMODO_PATH]
```
for example to add an engine to the former code you should add it like so:
```
STOCKFISH_PATH = "./engines/stockfish_15_linux_x64/stockfish_15_x64"
KOMODO_PATH = "./engines/komodo-13_201fd6/Linux/komodo-13.02-linux"
# add the new path on this variable
TOGAII_PATH = "./engines/TogaII/togaii-4.0.1-x86-64-core2"
# and add it at the end of this list
ENGINE_PATHS = [STOCKFISH_PATH, KOMODO_PATH, TOGAII_PATH]
```
you should do this for every engine that you want to add.

## Basic usage:
```
python chessc.py --help
usage: chessc.py [-h] (-t ANALYSIS_TIME | -d DEPTH) [-pv PRINCIPAL_VARIATIONS] -pgn
                 PGN_FILES [-x] [-v]

Analyse PGN files with chess engines to show correlation between human player and
engines.

options:
  -h, --help            show this help message and exit
  -t ANALYSIS_TIME, --analysis-time ANALYSIS_TIME
                        Analysis time (in seconds) per move [mutually exclusive with
                        --depth]
  -d DEPTH, --depth DEPTH
                        Depth of analysis per move in ply [mutually exclusive with
                        --analysis-time]
  -pv PRINCIPAL_VARIATIONS, --principal-variations PRINCIPAL_VARIATIONS
                        Number of principal variations (PV) per engine [this can make
                        the correlation very high if greater than 1]
  -pgn PGN_FILES, --pgn-files PGN_FILES
                        Folder with *.pgn files or a single pgn file to analyse
  -x, --verbose         Show verbose info about the analysis when multipv(--principal-
                        variations) mode is selected
  -v, --version         show program's version number and exit
  ```
### Analyse all the PGN files inside the `pgn/` folder and stop analysing each position after the depth of 20 ply has been reached:
```
python chessc.py --depth=20 --pgn-files=pgn/
```
### this are equivalent:
```
python chessc.py --depth 20 -pgn pgn/
```
```
python chessc.py -d 20 -pgn pgn/
```
### also you can stop the engine by passing the analysis time in seconds:
```
python chessc.py --analysis-time 10 --pgn-files pgn/niemann_cornette_2020.pgn
```
or using short arguments:
```
python chessc.py -t 10 -pgn pgn/niemann_cornette_2020.pgn
```
please note that the analysis in seconds can give different results each time, for more stable
results use the `depth` argument.

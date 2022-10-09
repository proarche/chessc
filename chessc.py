import sys
from pathlib import Path
import chess
import chess.engine
import chess.pgn
import chess.polyglot
import argparse

# should use at least two engines
STOCKFISH_PATH = "./engines/stockfish_15_linux_x64/stockfish_15_x64"
KOMODO_PATH = "./engines/komodo-13_201fd6/Linux/komodo-13.02-linux"
# this engines should be passed via command line arguments
ENGINE_PATHS = [STOCKFISH_PATH, KOMODO_PATH]

BOOK_PATH = "./books/komodo.bin"
prog_name = "Chess Correlation Tester"
version = "0.0.1"


def main(moves_per_engine, thinking_time, depth, pgn):
    book = chess.polyglot.open_reader(BOOK_PATH)

    engines = []
    for engine_path in ENGINE_PATHS:
        engines.append(chess.engine.SimpleEngine.popen_uci(engine_path))

    if Path(pgn).is_dir():
        analyze_folder(engines, moves_per_engine, thinking_time, depth, book, pgn)
    else:
        analyze_file(engines, moves_per_engine, thinking_time, depth, book, pgn)

    for engine in engines:
        engine.quit()


def analyze_folder(engines, moves_per_engine, thinking_time, depth, book, pgn_dir):
    for pgn_path in Path(pgn_dir).glob("*.pgn"):
        analyze_file(engines, moves_per_engine, thinking_time, depth, book, pgn_path)


def analyze_file(engines, moves_per_engine, thinking_time, depth, book, pgn_path):
    pgn = open(pgn_path)
    print(
        "Analysing:",
        repr(str(pgn_path)),
        "with",
        ", ".join(repr(str(ep)) for ep in ENGINE_PATHS),
    )
    # run the correlation and print the results
    calculate_correlation(engines, moves_per_engine, thinking_time, depth, book, pgn)

    print("Analysis finished:", repr(str(pgn_path)))


def calculate_correlation(engines, moves_per_engine, thinking_time, depth, book, pgn):
    # the direction of the analysis, forward by default
    direction_forwards = not args.backwards
    # number of games inside PGN file
    game_number = 0

    while True:
        # read the game from PGN and advances the queue
        game = chess.pgn.read_game(pgn)
        if game is None:  # no more games in PGN, it's the end of the file
            break  # exit the loop

        # game = chess.pgn.read_game(pgn)

        # if the analysis direction is forwards
        if direction_forwards:
            # set the board to the start of the game
            board = game.board()
        else:  # if the analysis direction is backwards
            # set the board to the end of the game
            board = game.end().board()

        # name of the player playing with white pieces
        name_player_white = game.headers.get("White")
        # name of the player playing with black pieces
        name_player_black = game.headers.get("Black")

        best_white = []
        best_black = []

        # number of total half-moves(ply) in game
        total_ply = len(list(game.mainline_moves()))

        # if the analysis direction is forwards
        if direction_forwards:
            # moves in forward direction
            mainline_moves = game.mainline_moves()
        else:  # if the analysis direction is backwards
            # moves in backwards direction
            mainline_moves = reversed(game.mainline_moves())

        # iterate over the moves on the mainline variation
        for move in mainline_moves:

            # if a position matches with the opening book, don't analyse it
            if book.get(board) != None:
                if direction_forwards:  # if the analysis direction is forwards
                    # make the move and take the board to the next position
                    board.push(move)
                else:  # if the analysis direction is backwards
                    # take the board to the previous position
                    board.pop()
                continue

            # if the analysis direction is backwards
            if args.backwards:
                # take the board to the previous position
                board.pop()

            # if the analysis direction is forwards
            if direction_forwards:
                # the percent of the analysis according the current half-move(ply) forward
                percent = str(str(round(board.ply() * 100 / total_ply)) + "%")
            else:  # if the analysis direction is backwards
                # the percent of the analysis according the current half-move(ply) backward
                percent = str(str(100 - round(board.ply() * 100 / total_ply)) + "%")

            # a list where the best moves of the engines will be added
            engine_moves = []
            # traverse all the engines and analyse the game with each of them
            for engine in engines:
                # the user passed arguments to analyse by time, so the limit is this time
                if thinking_time != None:
                    analysis = engine.analyse(
                        board,
                        chess.engine.Limit(time=thinking_time),
                        multipv=moves_per_engine,
                    )
                else:
                    # the user passed arguments to analyse by depth, so when the engine reaches this depth it stops
                    analysis = engine.analyse(
                        board,
                        chess.engine.Limit(depth=depth),
                        multipv=moves_per_engine,
                    )
                # status show on terminal for a single pv
                if moves_per_engine == 1:
                    print_status(
                        percent
                        + "|#"  # move number
                        + str(board.fullmove_number)
                        + "|"  # analysis score (centipawns and color)
                        + str(analysis[0]["score"])
                        + "|BM: "  # best move of the engine
                        + str(analysis[0]["pv"][0])
                        + "|Engine: "  # engine name
                        + engine.protocol.id["name"]
                    )
                # status show on terminal for various pv and verbose
                elif moves_per_engine >= 2 and args.verbose == True:
                    for pv in range(0, len(analysis)):
                        print_status_multipv(
                            percent
                            + "|#"  # move number
                            + str(board.fullmove_number)
                            + "|PV#: "  # principal variation number
                            + str(analysis[pv]["multipv"])
                            + "|"  # analysis score (centipawns and color)
                            + str(analysis[pv]["score"])
                            + "|BM: "  # best move of the engine for this PV
                            + str(analysis[pv]["pv"][0])
                            + "|Engine: "  # engine name
                            + engine.protocol.id["name"]
                        )
                # various pv and not verbose, just show percent
                else:
                    print_status(percent)

                # add engine top choice(and the top choice for each principal variation) to list
                for line in analysis:
                    engine_moves.append(line["pv"][0])

            # fill the lists with the result of the comparison
            # True if the move is top choice by the engines, False otherwise
            if board.turn == chess.WHITE:
                best_white.append(move in engine_moves)
            else:
                best_black.append(move in engine_moves)

            # if the analysis direction is forwards
            if direction_forwards:
                # set the board to the next position
                board.push(move)

        # counter for games inside a PGN
        game_number += 1
        print(
            "\nAnalysis of game",
            game_number,
            "| Date:",
            game.headers.get("Date") + "-" + game.headers.get("Time"),
            "| Opening:",
            game.headers.get("Opening"),
        )
        print(
            "Player with whites:",
            name_player_white,
            "|",
            str(round(100 * (sum(best_white) / len(best_white)), 2)) + "%",
        )
        print(
            "Player with blacks:",
            name_player_black,
            "|",
            str(round(100 * (sum(best_black) / len(best_black)), 2)) + "%",
            "\n" + "-" * 80,  # separator between game analysis, 80 chars wide
        )

    # return (
    #     # returns the percent of moves by the human that were top choices of the engines
    #     round(100 * (sum(best_white) / len(best_white)), 2),
    #     name_player_white,  # the name of the player with white pieces
    #     round(100 * (sum(best_black) / len(best_black)), 2),
    #     name_player_black,  # the name of the player with black pieces
    # )


# print the status of the analysis on one line
def print_status(message):
    sys.stdout.write("\r\x1b[K" + message)
    sys.stdout.flush()


# print the status of the analysis for each principal variation on several lines
def print_status_multipv(message):
    sys.stdout.write("\n" + message)
    sys.stdout.flush()


# parse the command line arguments
parser = argparse.ArgumentParser(
    description="Analyse PGN files with chess engines to show correlation between human player and engines."
)
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument(
    "-t",
    "--analysis-time",
    action="store",
    type=int,
    help="Analysis time (in seconds) per move [mutually exclusive with --depth]",
)
group.add_argument(
    "-d",
    "--depth",
    action="store",
    type=int,
    help="Depth of analysis per move in ply [mutually exclusive with --analysis-time]",
)
parser.add_argument(
    "-b",
    "--backwards",
    action="store_true",
    default=False,
    help="Sets the direction of the analysis to backwards, from last move back to first [forward by default]",
)
parser.add_argument(
    "-pv",
    "--principal-variations",
    action="store",
    default=1,
    type=int,
    help="Number of principal variations (PV) per engine [this can make the correlation very high if greater than 1]",
)
parser.add_argument(
    "-pgn",
    "--pgn-files",
    action="store",
    required=True,
    type=str,
    help="Folder with *.pgn files or a single pgn file to analyse",
)
parser.add_argument(
    "-v",
    "--verbose",
    action="store_true",
    default=False,
    help="Show verbose info about the analysis when multipv(--principal-variations) mode is selected",
)
parser.add_argument(
    "-V", "--version", action="version", version="{} v{}".format(prog_name, version)
)
args = parser.parse_args()

# call to the main function with the args entered
main(
    args.principal_variations,
    args.analysis_time,
    args.depth,
    args.pgn_files,
)

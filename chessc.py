import sys
from pathlib import Path
import chess
import chess.engine
import chess.pgn
import chess.polyglot

STOCKFISH_PATH = "./engines/stockfish_15_linux_x64/stockfish_15_x64"
KOMODO_PATH    = "./engines/komodo-13_201fd6/Linux/komodo-13.02-linux"
BOOK_PATH      = "./books/komodo.bin"
ENGINE_PATHS   = [STOCKFISH_PATH, KOMODO_PATH]

def main(moves_per_engine, thinking_time, pgn):
    book = chess.polyglot.open_reader(BOOK_PATH)

    engines = []
    for engine_path in ENGINE_PATHS:
        engines.append(chess.engine.SimpleEngine.popen_uci(engine_path))
  
    if (Path(pgn).is_dir()):
        analyze_folder(engines, moves_per_engine, thinking_time, book, pgn)
    else:
        analyze_file(engines, moves_per_engine, thinking_time, book, pgn)
    
    for engine in engines:
        engine.quit()

def analyze_folder(engines, moves_per_engine, thinking_time, book, pgn_dir):
    for pgn_path in Path(pgn_dir).glob("*.pgn"):    
        analyze_file(engines, moves_per_engine, thinking_time, book, pgn_path)

def analyze_file(engines, moves_per_engine, thinking_time, book, pgn_path):
    pgn = open(pgn_path)
    (white, black) = calculate_correlation(engines, moves_per_engine, thinking_time, book, pgn)

    print(pgn_path)      
    print("White: " + str(white) + "%")
    print("Black: " + str(black) + "%")

def calculate_correlation(engines, moves_per_engine, thinking_time, book, pgn):
    game  = chess.pgn.read_game(pgn)
    board = game.board()

    best_white  = []
    best_black  = []

    for move in game.mainline_moves():
        if(book.get(board) != None):
            board.push(move)
            continue
    
        engine_moves = [] 
        for engine in engines:
            analysis = engine.analyse(board, chess.engine.Limit(time=thinking_time), multipv=moves_per_engine)
            
            for line in analysis:
              engine_moves.append(line['pv'][0])

        if (board.turn == chess.WHITE):
            best_white.append(move in engine_moves)
        else:
            best_black.append(move in engine_moves)

        board.push(move)

    return (round(100*(sum(best_white)/len(best_white)), 2), round(100*(sum(best_black)/len(best_black)), 2))


if (len(sys.argv) == 4):
    main(int(sys.argv[1]), float(sys.argv[2]), sys.argv[3])
else:
    print("Wrong number of arguments")
    print("Usage: " + sys.argv[0] + " [number of calculated moves per engine] [analysis time (in seconds) per move] [pgn folder/pgn file]")

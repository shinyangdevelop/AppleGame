import sys

from search import n_iterative_solver, iterative_solver, r_iteration_solver, h_iteration_solver, exhaustive_solver
from core import scan, solve, restart_game
from gui import run as run_gui
import time

def main(is_gui):
    if is_gui:
        run_gui()
    else:
        cli()
    print("This is the new main.py file.")
    return 0

def cli():

    initial_grid, x_reps, y_reps, pos_dict = scan()

    DEV = False

    if '--dev' in sys.argv:
        DEV = True
        verbose = '--v' in sys.argv
        execute = '--e' in sys.argv
        summary = '--s' in sys.argv
        iteration = int(sys.argv[sys.argv.index('--s')+1])
    
    if DEV and summary:
        import openpyxl
        result = openpyxl.Workbook()
        output = result.active
        output.append(['E', 'H', 'R', 'N', 'I'])
        for _ in range(iteration):
            print(_)
            e = exhaustive_solver(initial_grid, 100000)[0]
            h = h_iteration_solver(initial_grid, 5, 10)[0]
            r = r_iteration_solver(initial_grid, 10000)[0]
            n = n_iterative_solver(initial_grid, 10000)[0]
            i = iterative_solver(initial_grid, 10000)[0]        
            print(e, h, r, n, i)
            if e*h*r*n*i == 0:
                print("t")
                restart_game()
                initial_grid, x_reps, y_reps, pos_dict = scan()    
                continue
            restart_game()
            output.append([e, h, r, n, i])
            initial_grid, x_reps, y_reps, pos_dict = scan()

        result.save(f"./result_{time.time()}.xlsx")

    
    if '--exhaustive' in sys.argv or '-e' in sys.argv:
        search_func = exhaustive_solver
        argument = {'initial_grid': initial_grid, 'max_calls' : 100000}
    elif '--h-iteration' in sys.argv or '-h' in sys.argv:
        search_func = h_iteration_solver
        argument = {'initial_grid': initial_grid, 'branches': 6, 'n_iteration': 6}
    elif '--r-iteration' in sys.argv or '-r' in sys.argv:
        search_func = r_iteration_solver
        argument = {'initial_grid': initial_grid, 'max_iteration': 10000}
    elif '--n-iteration' in sys.argv or '-n' in sys.argv:
        search_func = n_iterative_solver
        argument = {'initial_grid': initial_grid, 'guess_limit': 10000}
    elif '--iterative' in sys.argv or '-i' in sys.argv:
        search_func = iterative_solver
        argument = {'initial_grid': initial_grid, 'guess_limit': 10000}
    else:
        print("No search method specified. Use -e, -h, -r, -n, or -i.")
        return

    max_score, move_sequence = search_func(**argument)
    print(f"Max Score: {max_score}")
    print("Move Sequence:")
    for move in move_sequence:
        print(move)
    if not DEV or execute:
        solve(move_sequence, pos_dict, initial_grid, difficulty=10)
    else:
        print(max_score)

if __name__ == "__main__":
    main('-g' in sys.argv)
import os
import time
from IPython.display import clear_output
import numpy as np

def tic_tac_toe():
	playing = True
	while playing:
		_tic_tac_toe_game()
		playing = input('Play again? (Y/N): ').lower() == 'y'

def _tic_tac_toe_game():
	board, icons, moves = _setup()
	clear_output(wait=True)
	_clear_console()
	current_player = np.random.choice(['user', 'opponent'])
	playing = True
	while playing:
		current_player = 'user' if current_player=='opponent' else 'opponent'
		_print_board(board)
		if current_player == 'opponent':
			print('AI is making its move')
			time.sleep(np.random.uniform(1, 3))
		if current_player == 'user':
			print('Make your move!')
		board = moves[current_player](board, icon=icons[current_player])
		winner = _win_on_board(board)
		board_full = _full_board(board)
		playing = not (winner or board_full)
		clear_output(wait=True)
		_clear_console()
	_print_board(board)
	if board_full and not winner:
		print("It's a tie!")
		return
	if current_player == 'user':
		print('Congrats! You won!')
	if current_player == 'opponent':
		print('Better luck next time!')

def _setup():
	markers = ['X', 'O', '@', '#', '$', '%', '&', '*']
	user_icon = _user_input(markers, 'marker', str)
	markers.remove(user_icon)
	opponent_icon = 'X' if 'X' in markers else 'O'
	board = _create_board()
	return board, {'user': user_icon, 'opponent': opponent_icon}, {'user': _user_move, 'opponent': _opponent_move}

def _create_board(size=3):
	board = [[' ']*size]*size
	return np.array(board)

def _print_board(board):
	for row in board:
		print('| '+' | '.join(row)+' |')

def _opponent_move(board, icon='O'):
	cell_index = _random_sample_empty_cell_index(board)
	board[*cell_index] = icon
	return board

def _user_move(board, icon='X'):
	empty_cells = _empty_cell_indices(board)
	available = np.unique(empty_cells[:, 0])
	row_indx = _user_input(available, 'row', int)
	available = np.unique(empty_cells[empty_cells[:, 0]==row_indx][:, 1])
	col_indx = _user_input(available, 'col', int)
	board[row_indx, col_indx] = icon
	return board

def _user_input(available, row_or_col, converter):
	while True:
		indx = input(f'Choose {row_or_col} for your move from available {available}: ')
		try:
			indx = converter(indx)
		except Exception:
			print(f'User input {indx} not valid. Please try again')
			continue
		if indx in available:
			return indx
		print(f'User input {indx} not in the available choices {available}. Please try again')

def _empty_cell_indices(board):
	mask = board==' '
	empty_cells = np.argwhere(mask)
	return empty_cells

def _random_sample_empty_cell_index(board):
	empty_cells = _empty_cell_indices(board)
	if empty_cells.size==0:
		return empty_cells
	random_indx = np.random.choice(np.arange(len(empty_cells)), size=1)
	return empty_cells[random_indx][0]

def _win_on_board(board):
	rows = [_win_check(row) for row in board]
	cols = [_win_check(col) for col in board.T]
	diags = [_win_check(np.diagonal(board)), _win_check(np.diagonal(np.fliplr(board)))]
	return any(rows+cols+diags)

def _win_check(row_col_or_diag):
	return len(np.unique(row_col_or_diag))==1 and row_col_or_diag[0]!=' '

def _full_board(board):
	empty_cells = _empty_cell_indices(board)
	return empty_cells.size==0

def _clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')


if __name__=='__main__':
	tic_tac_toe()
from copy import deepcopy

import numpy as np

from HamiltonianCycle import Maze
from config import Direction
from util import PriorityQueueWithFunction, cyclic


class State:
	def __init__(self, board, g, heu_function, path):
		self.board = board
		self.h = heu_function(self)
		self.g = g
		self.f = self.h + self.g
		self.path = path

	def is_goal(self):
		return self.board.snake[0] == self.board.fruit_location

	def _is_legal_move(self, i, j):
		board_size = self.board.board_size
		i = cyclic(i, board_size)
		j = cyclic(j, board_size)
		return \
			0 <= i < board_size and 0 <= j < board_size \
			and (i, j) not in self.board.obstacles and (i, j) not in self.board.snake

	def get_legal_action(self):
		legal_actions = {Direction.LEFT, Direction.RIGHT, Direction.UP, Direction.DOWN}
		i, j = self.board.snake[0]
		if not self._is_legal_move(i - 1, j):
			legal_actions.remove(Direction.UP)
		if not self._is_legal_move(i + 1, j):
			legal_actions.remove(Direction.DOWN)
		if not self._is_legal_move(i, j - 1):
			legal_actions.remove(Direction.LEFT)
		if not self._is_legal_move(i, j + 1):
			legal_actions.remove(Direction.RIGHT)

		return list(legal_actions)

	def __eq__(self, other):
		return other.board == self.board

	def __hash__(self) -> int:
		return hash(self.board)


class Agent:

	def next_move(self, board):
		raise Exception('Method not implemented!')

	def reward(self, move, reward, after_hit=True):
		pass

	def update_current_state(self, board):
		pass

	def update_new_state(self, board):
		pass

	def update_fruit_location(self, new_location):
		pass


class AStarAgent(Agent):
	def __init__(self, heuristics):
		self.heuristic_function = heuristics
		self.moves = []

	def next_move(self, board):
		if not self.moves:
			self.moves = self.search(board)
			if not self.moves:
				return None
		return self.moves.pop()

	def search(self, init_board):
		fringe = PriorityQueueWithFunction(lambda state: state.f)

		init_state = State(init_board, 0, self.heuristic_function, [])
		fringe.push(init_state)

		visited = []

		while not fringe.isEmpty():
			# print(f'Open: {len(fringe)}, Close: {len(visited)}')
			item: State = fringe.pop()
			if item in visited:
				continue
			visited.append(item)
			if item.is_goal():
				return item.path

			for move in item.get_legal_action():
				new_board = deepcopy(item.board)
				new_board.next_move = move
				new_board.step()
				new_state = State(new_board, item.g + 1, self.heuristic_function, [move] + item.path)
				fringe.push(new_state)
		return []


class HamiltonianAgent(Agent):
	def __init__(self, board_size):
		self.maze: Maze = Maze(board_size)
		self.maze.generate()
		self.path = []

	def next_move(self, board):
		y, x = board.snake[0]
		tail_y, tail_x = board.snake[~0]
		fruit_y, fruit_x = board.fruit_location

		head_pos = self.maze.get_path_number(x, y)
		tail_pos = self.maze.get_path_number(tail_x, tail_y)
		fruit_pos = self.maze.get_path_number(fruit_x, fruit_y)

		distance_to_fruit = self.maze.path_distance(head_pos, fruit_pos)
		distance_to_tail = self.maze.path_distance(head_pos, tail_pos)

		cutting_amount_available = distance_to_tail - 5
		empty_squares = self.maze.arena_size - len(board.snake) - 3

		if empty_squares < self.maze.arena_size / 4:
			cutting_amount_available = 0
		elif distance_to_fruit < distance_to_tail:
			cutting_amount_available -= 1
			if (distance_to_tail - distance_to_fruit) * 4 > empty_squares:
				cutting_amount_available -= 10
		cutting_amount_desired = distance_to_fruit
		if cutting_amount_desired < cutting_amount_available:
			cutting_amount_available = cutting_amount_desired
		if cutting_amount_available < 0:
			cutting_amount_available = 0

		state: State = State(board, 0, lambda s: 0, None)
		legal_moves = state.get_legal_action()
		can_go_right = Direction.RIGHT in legal_moves and x < board.board_size - 1
		can_go_left = Direction.LEFT in legal_moves and x > 0
		can_go_down = Direction.DOWN in legal_moves and y < board.board_size - 1
		can_go_up = Direction.UP in legal_moves and y > 0

		best_dir = None
		best_dist = -1

		if can_go_right:
			dist = self.maze.path_distance(head_pos, self.maze.get_path_number(x + 1, y))
			if cutting_amount_available >= dist > best_dist:
				best_dir = Direction.RIGHT
				best_dist = dist
		if can_go_left:
			dist = self.maze.path_distance(head_pos, self.maze.get_path_number(x - 1, y))
			if cutting_amount_available >= dist > best_dist:
				best_dir = Direction.LEFT
				best_dist = dist
		if can_go_up:
			dist = self.maze.path_distance(head_pos, self.maze.get_path_number(x, y - 1))
			if cutting_amount_available >= dist > best_dist:
				best_dir = Direction.UP
				best_dist = dist
		if can_go_down:
			dist = self.maze.path_distance(head_pos, self.maze.get_path_number(x, y + 1))
			if cutting_amount_available >= dist > best_dist:
				best_dir = Direction.DOWN
				best_dist = dist

		if best_dist >= 0:
			return best_dir
		if can_go_up:
			return Direction.UP
		elif can_go_left:
			return Direction.LEFT
		elif can_go_down:
			return Direction.DOWN
		else:
			return Direction.RIGHT


class ImprovedHamAgent(Agent):
	def __init__(self, board_size):
		self.maze = Maze(board_size)
		self.maze.generate()
		self.moves = []

	def next_move(self, board):
		if not self.moves:
			self.moves = self.search(board)
			if not self.moves:
				return None
		return self.moves.pop()

	def search(self, init_board):
		fringe = PriorityQueueWithFunction(lambda state: state.f)
		init_state = State(init_board, 0, self.heu_func, [])
		fringe.push(init_state)

		visited = []

		while not fringe.isEmpty():
			item: State = fringe.pop()
			if item in visited:
				continue
			visited.append(item)
			if item.is_goal():
				return item.path

			for move in item.get_legal_action():
				if not self.legal(move, item):
					continue
				new_board = deepcopy(item.board)
				new_board.next_move = move
				new_board.step()
				new_state = State(new_board, item.g + 1, self.heu_func, [move] + item.path)
				fringe.push(new_state)
		return []

	def legal(self, action: Direction, state):
		row, col = state.board.snake[0]
		if action == Direction.UP:
			row -= 1
		elif action == Direction.DOWN:
			row += 1
		elif action == Direction.LEFT:
			col -= 1
		elif action == Direction.RIGHT:
			col += 1
		row = cyclic(row, state.board.board_size)
		col = cyclic(col, state.board.board_size)
		# if row < 0 or row >= state.board.board_size or col < 0 or col >= state.board.board_size:
		# 	return False
		tail_y, tail_x = state.board.snake[~0]
		tail_pos = self.maze.get_path_number(tail_x, tail_y)
		normalized_snake = np.asarray(
			list(map(lambda part: self.maze.get_path_number(part[1], part[0]), state.board.snake)))
		normalized_snake = (normalized_snake - tail_pos + self.maze.arena_size) % self.maze.arena_size
		pos = self.maze.get_path_number(col, row)
		normalized_pos = (pos - tail_pos + self.maze.arena_size) % self.maze.arena_size
		if normalized_pos < normalized_snake[0]:
			return False
		return True

	def heu_func(self, state):
		head_y, head_x = state.board.snake[0]
		fruit_y, fruit_x = state.board.fruit_location

		head_pos = self.maze.get_path_number(head_x, head_y)
		fruit_pos = self.maze.get_path_number(fruit_x, fruit_y)

		return self.maze.path_distance(head_pos, fruit_pos)

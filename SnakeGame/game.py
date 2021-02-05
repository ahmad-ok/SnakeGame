from optparse import OptionParser

import pygame

import DisplayEngine
import config
from agent import *
from heuristics import *
from qLearning import *


class Game:
	def __init__(self, board_size, obstacle_chance, agent=None, display_class=DisplayEngine.SilentDisplayEngine,
	             board_file=None):
		self.board = Board(board_size, obstacle_chance, board_file)
		self.agent = agent
		self.state = None
		self.display = display_class(self.board.move)
		self.clock = pygame.time.Clock()

	def run(self):

		self.state = config.GameState.RUNNING
		self.board.spawn_snake(2, 2, 1)
		self.board.spawn_fruit()
		while self.state != config.GameState.GAME_OVER:
			if self.state == config.GameState.PAUSED:
				continue

			self.agent.update_current_state(self.board)

			move = self.agent.next_move(self.board)
			if not move:
				break

			self.board.next_move = move
			self.board.step()

			self.agent.update_new_state(self.board)

			if self.board.snake[0] in self.board.obstacles or self.board.snake[0] in self.board.snake[1:]:
				self.state = config.GameState.GAME_OVER
				self.agent.reward(move, -100)

			elif self.board.snake[0] == self.board.fruit_location:
				if len(self.board.snake) > pow(self.board.board_size, 2) - 1:
					self.state = config.GameState.GAME_OVER
					self.agent.reward(move, 50)
				else:
					self.board.eat_fruit()
					self.agent.reward(move, 30)

			else:
				self.agent.reward(move, 0, after_hit=False)

			self.display.render(self)
			self.clock.tick(config.FRAME_RATE)
		self.board.end_game()


class Board:
	def __init__(self, board_size, obstacle_chance, board_file=None):
		self.board_size = board_size
		self.next_move = config.Direction.LEFT
		self.snake = []
		self.obstacles = set()
		self.fruit_location = ()
		if board_file:
			self.load_from_file(board_file)
		else:
			# generate a new board
			self.generate_obstacles(board_size, obstacle_chance, self.load_obstacles('ob.txt'))

	def move(self, direction):
		self.next_move = direction

	@staticmethod
	def load_obstacles(filename):
		"""
		Loads and returns obstacles from file
		file format:
			* Each line represents one obstacle
			* x and y are separated by "," and segments are separated  by "_"
		"""
		with open(f'data/obstacles/{filename}') as file:
			return [[[int(c) for c in b.split(',')] for b in a.split('_')] for a in file.readlines()]

	def load_from_file(self, file_name):
		with open(f'data/boards/{file_name}') as file:
			_board = [line.split(',') for line in file.readlines()]
			if not _board:
				return
			for i in range(len(_board)):
				for j in range(len(_board[0])):
					if _board[i][j] == 'x':
						self.obstacles.add((i, j))

	def save_to_file(self, file_name):
		with open(f'data/boards/{file_name}', 'w') as file:
			_board = [['_'] * self.board_size for _ in range(self.board_size)]
			for i in range(self.board_size):
				for j in range(self.board_size):
					if (i, j) in self.obstacles:
						_board[i][j] = 'x'
			file.write('\n'.join([','.join(line) for line in _board]))

	def generate_obstacles(self, board_size, obstacle_chance, obstacles):
		"""
		Generate obstacle from list of obstacles randomly placed throughout the board
		:param board_size:
		:param obstacle_chance: number of tiles count as obstacle
		:param obstacles: list of obstacles
		:return: board with randomly generated obstacles
		"""
		all_obstacles = []
		for i in range(int(board_size / 4) + 1):
			for j in range(int(board_size / 4) + 1):
				if random.random() > obstacle_chance:
					continue
				cell_i = 4 * i
				cell_j = 4 * j
				curr_i = random.randint(1, 2)
				curr_j = random.randint(1, 2)
				ob = random.choice(obstacles)
				ob = [(row + curr_j + cell_j, col + curr_i + cell_i) for row, col in ob]
				ob = [(row, col) for row, col in ob if row < board_size and col < board_size]
				all_obstacles += ob
		self.obstacles = all_obstacles[:]

	def spawn_snake(self, row, col, length):
		"""
		Spawns a snake where the head's coordinates are (row, col) and with body length of `length` (including the head)
		"""
		head = (row, col)
		self.snake = [head]
		if head in self.obstacles:
			self.obstacles.remove(head)
		for i in range(1, length):
			part = (row, col + i)
			if part in self.obstacles:
				self.obstacles.remove(part)
			self.snake.append(part)

	def step(self):
		head_i, head_j = self.snake[0]
		direction = self.next_move
		if direction == config.Direction.LEFT:
			head_j -= 1
		elif direction == config.Direction.RIGHT:
			head_j += 1
		elif direction == config.Direction.UP:
			head_i -= 1
		elif direction == config.Direction.DOWN:
			head_i += 1

		head_i = (head_i + self.board_size) % self.board_size
		head_j = (head_j + self.board_size) % self.board_size

		if (head_i, head_j) != self.fruit_location:
			self.snake.pop()

		self.snake.insert(0, (head_i, head_j))

	def spawn_fruit(self):
		"""
		add fruit to random location on the board
		"""
		i = random.randint(0, config.BOARD_SIZE - 1)
		j = random.randint(0, config.BOARD_SIZE - 1)

		while (i, j) in self.obstacles or (i, j) in self.snake:
			i = random.randint(0, config.BOARD_SIZE - 1)
			j = random.randint(0, config.BOARD_SIZE - 1)
		self.fruit_location = (i, j)

	def eat_fruit(self):
		self.spawn_fruit()

	def end_game(self):
		# board.save_to_file('b.txt')
		print(f'Game Ended, Score: {len(self.snake)}')

	def __repr__(self):
		s = ''
		for i in range(self.board_size):
			for j in range(self.board_size):
				if (i, j) in self.obstacles:
					s += 'x '
				elif self.snake and (i, j) == self.snake[0]:
					s += '@ '
				elif self.snake and (i, j) in self.snake:
					s += 'O '
				elif self.fruit_location == (i, j):
					s += '$ '
				else:
					s += '_ '
			s += '\n'
		return s

	def __eq__(self, other):
		return isinstance(other, Board) and other.snake[0] == self.snake[0]


def validate_percentage_cb(option, opt_str, value, parser: OptionParser):
	if value < 0 or value > 1:
		print('[ERROR] Percentage values should be between 0 and 1. Defaulting to 0')
		setattr(parser.values, option.dest, 0)
	else:
		setattr(parser.values, option.dest, value)


def main():
	usage_str = """
	USAGE:      python3 game.py <options>
	"""
	parser = OptionParser(usage_str)

	parser.add_option(
		'-s', '--size', dest='board_size',
		help='The size of the board.With Hamiltonian cycle agent it must be even number',
		default=config.BOARD_SIZE, type=int
	)
	parser.add_option(
		'-o', '--obstacle-chance', help='Chance to spawn obstacles in the board',
		default=0.0, type=float, metavar='[0-1]',
		action='callback', callback=validate_percentage_cb
	)

	parser.add_option('-n', '--num-of-games', help='Number of games to play', default=1, type=int)
	parser.add_option('-f', '--frame-rate', help='Limit frame rate of the game', default=config.FRAME_RATE, type=int)

	agents = ['astar', 'Q', 'hamiltonian', 'hamiltonian-astar']
	heus = ['manhattan', 'cyclic-manhattan', 'compact', 'wighted-compact']
	parser.add_option(
		'--agent', choices=agents, help=f'The agent to drive the snake',
		default=agents[0], type='choice', metavar=agents
	)
	parser.add_option('--heu', choices=heus, help=f'The heuristic for the A* agent', default=heus[0], metavar=heus)
	parser.add_option('--alpha', help='Alpha value for Q learning agent', default=0.9, type=float)
	parser.add_option('--gamma', help='Gamma value for Q learning agent', default=0.85, type=float)
	parser.add_option('--random-rate', help='Random rate value for Q learning agent', default=0.05, type=float)

	displays = ['GUI', 'CLI', 'Silent']
	parser.add_option(
		'--display', metavar=displays, choices=displays, default='GUI',
		help='Display type for the game'
	)

	args, _ = parser.parse_args()

	config.FRAME_RATE = args.frame_rate
	config.BLOCK_SIZE = config.GUI_WIDTH / args.board_size

	display = get_display(args.display)
	heu = get_heu(args.heu)
	agent = get_agent(
		args.agent,
		size=args.board_size, heu=heu, alpha=args.alpha, gamma=args.gamma, rand=args.random_rate
	)

	game = Game(args.board_size, args.obstacle_chance, agent, display)

	scores = []
	for _ in range(args.num_of_games):
		game.run()
		scores.append(len(game.board.snake))

	avg = sum(scores) / args.num_of_games
	avg_coverage = avg / (args.board_size * args.board_size)
	print(f'Finished with average score of {avg}, average board coverage: {avg_coverage * 100: 0.2f}%')


def get_heu(name: str):
	name = name.lower()
	if name == 'manhattan':
		return manhattan_distance
	elif name == 'cyclic-manhattan':
		return cyclic_manhattan_distance
	elif name == 'compact':
		return compact_heuristics
	elif name == 'weighted-compact':
		return weighed_compact_heuristics


def get_agent(name: str, **kwargs):
	name = name.lower()
	if name == 'astar':
		return AStarAgent(kwargs['heu'])
	elif name == 'q':
		print('hi')
		alpha = kwargs['alpha']
		gamma = kwargs['gamma']
		rand = kwargs['rand']
		agent = QLearningAgent(alpha, gamma, rand)
		agent.read_qtable('50kLearn')
		return agent
	elif name == 'hamiltonian':
		board_size = kwargs['size']
		return HamiltonianAgent(board_size)
	elif name == 'hamiltonian-astar':
		board_size = kwargs['size']
		return ImprovedHamAgent(board_size)


def get_display(name: str):
	if name == 'GUI':
		return DisplayEngine.GUIDisplayEngine
	elif name == 'CLI':
		return DisplayEngine.CliDisplayEngine
	elif name == 'Silent':
		return DisplayEngine.SilentDisplayEngine


if __name__ == '__main__':
	main()

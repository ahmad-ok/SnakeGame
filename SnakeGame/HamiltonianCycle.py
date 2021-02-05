import numpy as np

from config import Direction


class Node:
	def __init__(self):
		self.visited = False
		self.can_go_right = False
		self.can_go_down = False


class Maze:
	def __init__(self, board_size):
		self.board_size = board_size
		self.arena_size = board_size * board_size
		self.nodes = [Node() for _ in range(self.arena_size // 4)]
		self.tour_to_number = np.zeros(self.arena_size, dtype=int)

	def reset(self):
		self.tour_to_number = np.zeros(self.arena_size, dtype=int)
		self.generate()

	def get_path_number(self, x, y):
		return self.tour_to_number[(x + self.board_size * y) % self.arena_size]

	def get_next_dir(self, x, y):
		"""
		(x, y) is the snake's head
		"""
		pos = self.get_path_number(x, y)
		if pos + 1 == self.arena_size:
			pos = -1
		if x > 0 and self.get_path_number(x - 1, y) == pos + 1:
			return Direction.LEFT
		elif y > 0 and self.get_path_number(x, y - 1) == pos + 1:
			return Direction.UP
		elif x <= self.board_size - 1 and self.get_path_number(x + 1, y) == pos + 1:
			return Direction.RIGHT
		elif y <= self.board_size and self.get_path_number(x, y + 1) == pos + 1:
			return Direction.DOWN

	def path_distance(self, coord_a, coord_b):
		if coord_a < coord_b:
			return coord_b - coord_a - 1
		return coord_b - coord_a - 1 + self.arena_size

	def mark_visited(self, x, y):
		self.nodes[x + y * self.board_size // 2].visited = True

	def mark_can_go_right(self, x, y):
		self.nodes[x + y * self.board_size // 2].can_go_right = True

	def mark_can_go_down(self, x, y):
		self.nodes[x + y * self.board_size // 2].can_go_down = True

	def is_visited(self, x, y):
		return self.nodes[x + y * self.board_size // 2].visited

	def can_go_right(self, x, y):
		return self.nodes[x + y * self.board_size // 2].can_go_right

	def can_go_down(self, x, y):
		return self.nodes[x + y * self.board_size // 2].can_go_down

	def can_go_left(self, x, y):
		if x == 0:
			return False
		return self.can_go_right(x - 1, y)

	def can_go_up(self, x, y):
		if y == 0:
			return False
		return self.can_go_down(x, y - 1)

	def generate(self):
		self.generate_r(-1, -1, 0, 0)
		self.generate_tour_number()

	def generate_r(self, from_x, from_y, x, y):
		if x < 0 or y < 0 or x >= self.board_size / 2 or y >= self.board_size / 2:
			return
		if self.is_visited(x, y):
			return
		self.mark_visited(x, y)

		if from_x != -1:
			if from_x < x:
				self.mark_can_go_right(from_x, from_y)
			elif from_x > x:
				self.mark_can_go_right(x, y)
			elif from_y < y:
				self.mark_can_go_down(from_x, from_y)
			elif from_y > y:
				self.mark_can_go_down(x, y)

		for i in range(2):
			r = np.random.randint(0, 4)
			if r == 0:
				self.generate_r(x, y, x - 1, y)
			elif r == 1:
				self.generate_r(x, y, x + 1, y)
			elif r == 2:
				self.generate_r(x, y, x, y - 1)
			elif r == 3:
				self.generate_r(x, y, x, y + 1)

		self.generate_r(x, y, x - 1, y)
		self.generate_r(x, y, x + 1, y)
		self.generate_r(x, y, x, y + 1)
		self.generate_r(x, y, x, y - 1)

	def _find_next_dir(self, x, y, snake_dir: Direction):
		if snake_dir == Direction.RIGHT:
			if self.can_go_up(x, y):
				return Direction.UP
			elif self.can_go_right(x, y):
				return Direction.RIGHT
			elif self.can_go_down(x, y):
				return Direction.DOWN
			else:
				return Direction.LEFT
		elif snake_dir == Direction.DOWN:
			if self.can_go_right(x, y):
				return Direction.RIGHT
			elif self.can_go_down(x, y):
				return Direction.DOWN
			elif self.can_go_left(x, y):
				return Direction.LEFT
			else:
				return Direction.UP
		elif snake_dir == Direction.LEFT:
			if self.can_go_down(x, y):
				return Direction.DOWN
			elif self.can_go_left(x, y):
				return Direction.LEFT
			elif self.can_go_up(x, y):
				return Direction.UP
			else:
				return Direction.RIGHT
		elif snake_dir == Direction.UP:
			if self.can_go_left(x, y):
				return Direction.LEFT
			elif self.can_go_up(x, y):
				return Direction.UP
			elif self.can_go_right(x, y):
				return Direction.RIGHT
			else:
				return Direction.DOWN
		return None

	def set_tour_number(self, x, y, tour_number):
		if self.get_path_number(x, y) != 0:
			print(self.get_path_number(x, y), 'trying to set to', tour_number)
			return
		self.tour_to_number[x + y * self.board_size] = tour_number

	def generate_tour_number(self):
		start_x, start_y = 0, 0
		x, y = start_x, start_y

		start_dir = Direction.UP if self.can_go_down(x, y) else Direction.LEFT
		snake_dir = start_dir
		tour_num = 0
		while tour_num != self.arena_size:
			next_dir = self._find_next_dir(x, y, snake_dir)
			if snake_dir == Direction.RIGHT:
				self.set_tour_number(x * 2, y * 2, tour_num)
				tour_num += 1
				if next_dir in [snake_dir, Direction.DOWN, Direction.LEFT]:
					self.set_tour_number(x * 2 + 1, y * 2, tour_num)
					tour_num += 1
				if next_dir in [Direction.DOWN, Direction.LEFT]:
					self.set_tour_number(x * 2 + 1, y * 2 + 1, tour_num)
					tour_num += 1
				if next_dir == Direction.LEFT:
					self.set_tour_number(x * 2, y * 2 + 1, tour_num)
					tour_num += 1
			elif snake_dir == Direction.DOWN:
				self.set_tour_number(x * 2 + 1, y * 2, tour_num)
				tour_num += 1
				if next_dir in [snake_dir, Direction.LEFT, Direction.UP]:
					self.set_tour_number(x * 2 + 1, y * 2 + 1, tour_num)
					tour_num += 1
				if next_dir in [Direction.LEFT, Direction.UP]:
					self.set_tour_number(x * 2, y * 2 + 1, tour_num)
					tour_num += 1
				if next_dir == Direction.UP:
					self.set_tour_number(x * 2, y * 2, tour_num)
					tour_num += 1
			elif snake_dir == Direction.LEFT:
				self.set_tour_number(x * 2 + 1, y * 2 + 1, tour_num)
				tour_num += 1
				if next_dir in [snake_dir, Direction.RIGHT, Direction.UP]:
					self.set_tour_number(x * 2, y * 2 + 1, tour_num)
					tour_num += 1
				if next_dir in [Direction.RIGHT, Direction.UP]:
					self.set_tour_number(x * 2, y * 2, tour_num)
					tour_num += 1
				if next_dir == Direction.RIGHT:
					self.set_tour_number(x * 2 + 1, y * 2, tour_num)
					tour_num += 1
			elif snake_dir == Direction.UP:
				self.set_tour_number(x * 2, y * 2 + 1, tour_num)
				tour_num += 1
				if next_dir in [snake_dir, Direction.RIGHT, Direction.DOWN]:
					self.set_tour_number(x * 2, y * 2, tour_num)
					tour_num += 1
				if next_dir in [Direction.RIGHT, Direction.DOWN]:
					self.set_tour_number(x * 2 + 1, y * 2, tour_num)
					tour_num += 1
				if next_dir == Direction.DOWN:
					self.set_tour_number(x * 2 + 1, y * 2 + 1, tour_num)
					tour_num += 1

			snake_dir = next_dir

			if next_dir == Direction.RIGHT:
				x += 1
			elif next_dir == Direction.LEFT:
				x -= 1
			elif next_dir == Direction.DOWN:
				y += 1
			elif next_dir == Direction.UP:
				y -= 1

	def write_tour_to_file(self):
		with open('tour.txt', 'w+') as file:
			for y in range(self.board_size):
				for x in range(self.board_size):
					file.write(f'{self.get_path_number(x, y):4d}')
				file.write('\n')


if __name__ == '__main__':
	maze = Maze(16)
	maze.generate()

	maze.write_tour_to_file()

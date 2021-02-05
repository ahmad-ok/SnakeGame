import random
from agent import Agent
from config import Direction
from util import cyclic, Counter
import util


class QLearningAgent(Agent):

    def __init__(self, alpha, gamma, random_rate):
        self.alpha = alpha  # learning rate
        self.gamma = gamma  # discount factor
        self.random_rate = random_rate
        # self.actions_space = [Direction.LEFT, Direction.RIGHT, Direction.UP, Direction.DOWN]
        self.actions_space = [0, 1, 2, 3]

        self.values = Counter()  # Q(s, a)

        self.current_state = 0
        self.new_state = 0
        self.fruit_relative_position_before = []
        self.fruit_relative_position_after = []

        self.fruit_position = 0
        self.current_fruit_position = 0

        self.counter = 0

    def update_fruit_location(self, new_location):
        self.fruit_position = new_location

    def reward(self, move, reward, after_hit=True):
        if after_hit:
            self.update(self.current_state, self.find_action(move), self.new_state, reward)

        else:

            # if self.fruit_relative_position_after[0] <= self.fruit_relative_position_after[0] and \
            #         self.fruit_relative_position_after[1] <= self.fruit_relative_position_before[1]:
            #     self.update(self.current_state, self.find_action(move), self.new_state, 1)

            # if sum(self.fruit_relative_position_after) <= sum(self.fruit_relative_position_before):
            #     self.update(self.current_state, self.find_action(move), self.new_state, 2)
            # else:
            self.update(self.current_state, self.find_action(move), self.new_state, -10)

    def update_current_state(self, board):

        self.current_state = self.get_current_state(board)
        self.current_fruit_position = board.fruit_location
        self.counter += 1

        fruit_x = board.fruit_location[0]
        fruit_y = board.fruit_location[1]
        snake_x_before = board.snake[0][0]
        snake_y_before = board.snake[0][1]

        fruit_relative_x_before = abs(fruit_x - snake_x_before)
        fruit_relative_y_before = abs(fruit_y - snake_y_before)

        self.fruit_relative_position_before = [fruit_relative_x_before, fruit_relative_y_before]

    def update_new_state(self, board):

        self.new_state = self.get_current_state(board)
        fruit_x = board.fruit_location[0]
        fruit_y = board.fruit_location[1]
        snake_x_before = board.snake[0][0]
        snake_y_before = board.snake[0][1]

        fruit_relative_x_after = abs(fruit_x - snake_x_before)
        fruit_relative_y_after = abs(fruit_y - snake_y_before)

        self.fruit_relative_position_after = [fruit_relative_x_after, fruit_relative_y_after]

    def get_current_state_(self, board):
        """
        DIDNT USE... Check the 3 blocks around the head of the snake and relative positions of fruit and tail to head
        :param board:
        :return:
        """
        # 3 places around head
        snake = board.snake
        snake_x = snake[0][0]
        snake_y = snake[0][1]
        fruit_position = board.fruit_location
        board_size = board.board_size
        fruit_x = fruit_position[0]
        fruit_y = fruit_position[1]

        direction = board.next_move

        left = right = up = 0
        # print(cyclic(5, board_size))

        if direction == Direction.LEFT:
            left = (cyclic(snake_x + 1, board_size), snake_y)
            up = (snake_x, cyclic(snake_y - 1, board_size))
            right = (cyclic(snake_x - 1, board_size), snake_y)

        elif direction == Direction.RIGHT:
            left = (cyclic(snake_x - 1, board_size), snake_y)
            up = (snake_x, cyclic(snake_y + 1, board_size))
            right = (cyclic(snake_x + 1, board_size), snake_y)

        elif direction == Direction.UP:
            left = (snake_x, cyclic(snake_y - 1, board_size))
            up = (cyclic(snake_x - 1, board_size), snake_y)
            right = (snake_x, cyclic(snake_y + 1, board_size))

        elif direction == Direction.DOWN:
            left = (snake_x, cyclic(snake_y + 1, board_size))
            up = (cyclic(snake_x + 1, board_size), snake_y)
            right = (snake_x, cyclic(snake_y - 1, board_size))

        if left in snake or left in board.obstacles:
            state_name = '1'
        elif left == fruit_position:
            state_name = '2'
        else:
            state_name = '0'

        if up in snake or up in board.obstacles:
            state_name += '1'
        elif up == fruit_position:
            state_name += '2'
        else:
            state_name += '0'

        if right in snake or right in board.obstacles:
            state_name += '1'
        elif right == fruit_position:
            state_name += '2'
        else:
            state_name += '0'

        state_name += str(abs(fruit_x - snake_x)) + str(abs(fruit_y - snake_y))

        state_name += str(abs(snake[len(snake) - 1][0] - snake_x)) + str(abs(snake[len(snake) - 1][1] - snake_y))

        return state_name

    def get_current_state(self, board):

        snake = board.snake
        snake_x = snake[0][0]
        snake_y = snake[0][1]
        fruit_position = board.fruit_location
        board_size = board.board_size

        fruit_x = fruit_position[0]
        fruit_y = fruit_position[1]

        left = 1 if (snake_x, cyclic(snake_y - 1, board_size)) in snake or \
                    (snake_x, cyclic(snake_y - 1, board_size)) in board.obstacles else 0
        right = 1 if (snake_x, cyclic(snake_y + 1, board_size)) in snake or \
                     (snake_x, cyclic(snake_y + 1, board_size)) in board.obstacles else 0
        up = 1 if (cyclic(snake_x - 1, board_size), snake_y) in snake or \
                  (cyclic(snake_x - 1, board_size), snake_y) in board.obstacles else 0
        down = 1 if (cyclic(snake_x + 1, board_size), snake_y) in snake or \
                    (cyclic(snake_x + 1, board_size), snake_y) in board.obstacles else 0

        left = 2 if (snake_x, cyclic(snake_y - 1, board_size)) == fruit_position else left
        right = 2 if (snake_x, cyclic(snake_y + 1, board_size)) == fruit_position else right
        up = 2 if (cyclic(snake_x - 1, board_size), snake_y) == fruit_position else up
        down = 2 if (cyclic(snake_x + 1, board_size), snake_y) == fruit_position else down

        state_name = str(left) + str(up) + str(right) + str(down)

        fruit_relative_x = fruit_x - snake_x
        fruit_relative_y = fruit_y - snake_y

        if fruit_relative_x < 0 and fruit_relative_y < 0:
            state_name += '10000000'

        elif fruit_relative_x < 0 and fruit_relative_y == 0:
            state_name += '01000000'

        elif fruit_relative_x < 0 and fruit_relative_y > 0:
            state_name += '00100000'

        elif fruit_relative_x == 0 and fruit_relative_y > 0:
            state_name += '00010000'

        elif fruit_relative_x > 0 and fruit_relative_y > 0:
            state_name += '00001000'

        elif fruit_relative_x > 0 and fruit_relative_y == 0:
            state_name += '00000100'

        elif fruit_relative_x > 0 and fruit_relative_y < 0:
            state_name += '00000010'

        elif fruit_relative_x == 0 and fruit_relative_y < 0:
            state_name += '00000001'

        return state_name

    def next_move(self, board):
        current_state = self.get_current_state(board)

        action = self.getAction(current_state)

        while True:
            if action == 0 and board.next_move != Direction.RIGHT:
                return Direction.LEFT
            elif action == 1 and board.next_move != Direction.LEFT:
                return Direction.RIGHT
            elif action == 2 and board.next_move != Direction.DOWN:
                return Direction.UP
            elif action == 3 and board.next_move != Direction.UP:
                return Direction.DOWN

            action = self.getAction(current_state)

    def find_action(self, action):
        if action == Direction.LEFT:
            return 0
        elif action == Direction.RIGHT:
            return 1
        elif action == Direction.UP:
            return 2
        else:
            return 3

    def getLegalActions(self, state):
        """
          Get the actions available for a given
          state. This is what you should use to
          obtain legal actions for a state
        """
        return self.actions_space

    def update(self, state, action, nextState, reward):
        """
            The parent class calls this to observe a
            state = action => nextState and reward transition.
            You should do your Q-Value update here

            NOTE: You should never call this function,
            it will be called on your behalf
        """
        self.values[(state, action)] += self.alpha * (
                reward + self.gamma * self.getValue(nextState) - self.values[(state, action)])

    def getQValue(self, state, action):
        """
        Returns Q(state,action)
        Should return 0.0 if we never seen
        a state or (state,action) tuple
        """
        return self.values[(state, action)]

    def getValue(self, state):
        """
            Returns max_action Q(state,action)
            where the max is over legal actions.  Note that if
            there are no legal actions, which is the case at the
            terminal state, you should return a value of 0.0.
        """
        actions = self.getLegalActions(state)
        if not actions:
            return 0
        return max([self.getQValue(state, a) for a in actions])

    def getPolicy(self, state):
        """
            Compute the best action to take in a state.  Note that if there
            are no legal actions, which is the case at the terminal state,
            you should return None.
        """
        val = self.getValue(state)
        actions = [a for a in self.getLegalActions(state) if self.getQValue(state, a) == val]
        if not actions:
            return None
        return random.choice(actions)

    def getAction(self, state):
        """
            Compute the action to take in the current state.  With
            probability self.epsilon, we should take a random action and
            take the best policy action otherwise.  Note that if there are
            no legal actions, which is the case at the terminal state, you
            should choose None as the action.

            HINT: You might want to use util.flipCoin(prob)
            HINT: To pick randomly from a list, use random.choice(list)
        """
        # Pick Action
        legal_actions = self.getLegalActions(state)
        action = None
        if self.counter > 1000 and self.fruit_position == self.current_fruit_position:
            # print(str(self.counter) + ' random................................................')
            action = random.choice(legal_actions)
            self.counter = 0

        if util.flipCoin(self.random_rate):
            if legal_actions:
                action = random.choice(legal_actions)
        else:
            action = self.getPolicy(state)
        return action

    def write_qtable(self, path='qtable.txt'):
        f = open(path, 'w')
        for k, v in self.values.items():
            f.write(str(k[0]) + ':' + str(k[1]) + ':' + str(v) + '\n')
        f.close()

    def read_qtable(self, path='qtable.txt'):
        f = open(path, 'r')
        line = f.readline()
        while line:
            # print(line)
            line = line.strip('\n')
            line = line.split(':')
            # print(line)
            self.values[(line[0], float(line[1]))] = float(line[2])
            line = f.readline()
        # print(self.values)

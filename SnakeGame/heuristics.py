import util
from agent import State


def manhattan_distance(state: State):
    head = state.board.snake[0]
    fruit = state.board.fruit_location
    return util.manhattanDistance(head, fruit)


def cyclic_manhattan_distance(state: State):
    board_size = state.board.board_size
    head = state.board.snake[0]
    fruit = state.board.fruit_location
    return util.cyclic_manhattan_distance(head, fruit, board_size)


def compact_heuristics(state: State):
    manhattan = manhattan_distance(state)
    squareness = util.squareness(state.board.snake)
    compactness = util.compactness(state.board.snake)
    connectivity = util.connectivity(state.board)
    dead_end = util.dead_end(state.board)

    return manhattan + squareness + compactness + connectivity + dead_end


def weighed_compact_heuristics(state: State):
    manhattan = manhattan_distance(state)
    squareness = util.squareness(state.board.snake)
    compactness = util.compactness(state.board.snake)
    connectivity = util.connectivity(state.board)
    dead_end = util.dead_end(state.board)

    return manhattan + 3 * squareness + 3 * compactness + 2 * connectivity + 2 * dead_end

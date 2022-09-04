import copy
import sys

INFINITY = sys.maxsize
AVAILABLE_CORDINATES = [0, 3, 6, 11, 13, 15, 22, 23, 24, 30, 31, 32, 34, 35, 36, 42, 43, 44, 51, 53, 55, 60, 63, 66]
PLAYER = None
OPPOSITE_PLAYER = None


def main():
    player = input().strip()
    move = input().strip()

    board = []
    for i in range(0, 7):
        board.append(input().strip())

    print(nextMove(player, move, board))


def nextMove(player, move, board_string):
    PLAYER = player
    if player == "W":
        OPPOSITE_PLAYER = "B"
    else:
        OPPOSITE_PLAYER = "W"
    board = convert(board_string)
    tree = Tree()
    node = TreeNode(board)
    tree.root = node
    if move == "INIT":
        createChildrenFirstPhase(tree.root, 3, player)
        best_node = minimax(tree.root, 3, -INFINITY, +INFINITY, True, True, 1)
        cordinates = findDifference(board, best_node.position, 1)
        return cordinates
    elif move == "MILL":
        best_board = pickOponentsPiece(tree.root, player)
        cordinates = findDifference(board, best_board, 2)
        return cordinates
    elif move == "MOVE":
        createChildrenSecondPhase(tree.root, 3, player)
        best_node = minimax(tree.root, 3, -INFINITY, +INFINITY, True, True, 1)
        cordinates = findDifference(board, best_node.position, 3)
        return cordinates


def convert(board_string):
    board = HashMap()
    for i in range(0, len(board_string)):
        for j in range(0, len(board_string[i])):
            if board_string[i][j] == "W" or board_string[i][j] == "B":
                key = i * 10 + j
                board[key] = board_string[i][j]
    return board


def findDifference(old_board, new_board, phase):
    if phase == 1:
        cordinates = None
        for figure in new_board:
            if figure < 10:
                cordinates = " ".join(list("0" + str(figure)))
            else:
                cordinates = " ".join(list(str(figure)))
        return cordinates

    elif phase == 2:
        cordinates = None
        for figure in old_board:
            if figure not in new_board:
                if figure < 10:
                    cordinates = " ".join(list("0"+str(figure)))
                else:
                    cordinates = " ".join(list(str(figure)))
        return cordinates

    elif phase == 3:
        from_cordinates = None
        for figure in old_board:
            if figure not in new_board:
                if figure < 10:
                    from_cordinates = " ".join(list("0" + str(figure)))
                else:
                    from_cordinates = " ".join(list(str(figure)))
        to_cordinates = None
        for figure in new_board:
            if figure not in old_board:
                if figure < 10:
                    to_cordinates = " ".join(list("0" + str(figure)))
                else:
                    to_cordinates = " ".join(list(str(figure)))
        return from_cordinates + " " + to_cordinates


def minimax(node, depth, alpha, beta, maximizing_player, is_top_node, phase):# https://www.youtube.com/watch?v=l-hh51ncgDI izvor koda + modifikovano
    #ako je dubina 0 ili je cvor list, vrati evaluaciju
    if depth == 0 or node.is_leaf():
        return evaluate(node, phase)

    if maximizing_player:
        max_eval = -INFINITY
        best_node = None
        for child in node.children:
            evaluation = minimax(child, depth-1, alpha, beta, False, False, phase)
            max_eval = max(max_eval, evaluation)
            if max_eval == evaluation and alpha != max_eval:
                best_node = child
            alpha = max(alpha, evaluation)
            if beta <= alpha:
                break
        if is_top_node:
            return best_node
        return max_eval

    else:
        min_eval = +INFINITY
        for child in node.children:
            evaluation = minimax(child, depth-1, alpha, beta, True, False, phase)
            min_eval = min(min_eval, evaluation)
            beta = min(beta, evaluation)
            if beta <= alpha:
                break
        return min_eval


def findNeighbours(cordinates):
    neighbours = []
    if cordinates == 0:
        neighbours += [3, 30]
    if cordinates == 6:
        neighbours += [3, 36]
    if cordinates == 60:
        neighbours += [30, 63]
    if cordinates == 66:
        neighbours += [63, 36]
    if cordinates == 11:
        neighbours += [31, 13]
    if cordinates == 15:
        neighbours += [13, 35]
    if cordinates == 55:
        neighbours += [35, 53]
    if cordinates == 51:
        neighbours += [31, 53]
    if cordinates == 22:
        neighbours += [23, 32]
    if cordinates == 24:
        neighbours += [23, 34]
    if cordinates == 44:
        neighbours += [43, 34]
    if cordinates == 42:
        neighbours += [32, 43]
    if cordinates == 3:
        neighbours += [0, 13, 6]
    if cordinates == 23:
        neighbours += [22, 24, 13]
    if cordinates == 30:
        neighbours += [0, 60, 31]
    if cordinates == 32:
        neighbours += [22, 31, 42]
    if cordinates == 63:
        neighbours += [60, 66, 53]
    if cordinates == 43:
        neighbours += [42, 44, 53]
    if cordinates == 34:
        neighbours += [24, 44, 35]
    if cordinates == 36:
        neighbours += [35, 6, 66]
    if cordinates == 13:
        neighbours += [11, 15, 3, 23]
    if cordinates == 31:
        neighbours += [11, 30, 32, 51]
    if cordinates == 53:
        neighbours += [51, 55, 43, 63]
    if cordinates == 35:
        neighbours += [34, 15, 55, 36]
    return neighbours


def movableFigures(state, player):
    board = state.position
    player_pieces = playerPieces(board, player)
    blocked_pieces = blockedPieces(state, player)
    return [piece for piece in player_pieces if piece not in blocked_pieces]


def createChildrenFirstPhase(node, depth, player):
    board = node.position
    if depth == 0:
        return
    next_player = None
    if player == "W":
        next_player = "B"
    else:
        next_player = "W"
    available_cordinates = [cordinate for cordinate in AVAILABLE_CORDINATES if cordinate not in board]
    for cordinate in available_cordinates:
        new_board = copy.deepcopy(board)
        child = TreeNode(new_board)
        node.add_child(child)
        new_board[cordinate] = player
        if millCreated(child.parent.position, new_board, player):
            child.position = pickOponentsPiece(child, player)
        createChildrenFirstPhase(child, depth - 1, next_player)


def createChildrenSecondPhase(node, depth, player):
    board = node.position
    if depth == 0:
        return
    next_player = None
    if player == "W":
        next_player = "B"
    else:
        next_player = "W"
    movable_figures = movableFigures(node, player)
    free_cordinates = [piece for piece in AVAILABLE_CORDINATES if piece not in board]
    player_pieces = playerPieces(board, player)
    #ako je igrac na vise od 3 figure (druga faza)
    if len(player_pieces) > 3:
        #prodji kroz sve kordinate koje se mogu pomeriti
        for from_cordinates in movable_figures:
            new_board = copy.deepcopy(board)
            del new_board[from_cordinates]
            neighbour_cordinates = findNeighbours(from_cordinates)
            for to_cordinates in neighbour_cordinates:
                if to_cordinates not in new_board:
                    new_board2 = copy.deepcopy(new_board)
                    child = TreeNode(new_board2)
                    node.add_child(child)
                    new_board2[to_cordinates] = player
                    if millCreated(child.parent.position, new_board2, player):
                        pickOponentsPiece(child, player)
                    createChildrenSecondPhase(child, depth - 1, next_player)
    #ako igrac ima 3 figure (treca faza)
    elif len(player_pieces) == 3:
        for from_cordinates in movable_figures:
            new_board = copy.deepcopy(board)
            del new_board[from_cordinates]
            for to_cordinates in free_cordinates:
                if to_cordinates not in new_board:
                    new_board2 = copy.deepcopy(new_board)
                    child = TreeNode(new_board2)
                    node.add_child(child)
                    new_board2[to_cordinates] = player
                    if millCreated(child.parent.position, new_board2, player):
                        pickOponentsPiece(child, player)
                    createChildrenSecondPhase(child, depth - 1, next_player)
    #ako igrac ima manje od 3 figure onda se ne grana vise odnosno taj cvor je list (game over)
    else:
        return


def pickOponentsPiece(current_state, player):
    board = current_state.position
    oposite_player = None
    if player == "W":
        oposite_player = "B"
    else:
        oposite_player = "W"

    #racunar pronalazi protivnikove figure koje nisu u millu
    player_pieces = playerPieces(board, oposite_player)
    player_mill_pieces = mills(board, oposite_player)
    non_mill_pieces = [piece for piece in player_pieces if piece not in player_mill_pieces]
    #ako postoje figure koje nisu u millu
    if len(non_mill_pieces) > 0:
        evaluation_list = []
        board_list = []
        for piece in non_mill_pieces:
            new_board = copy.deepcopy(board)
            del new_board[piece]
            new_state = TreeNode(new_board)
            new_state.parent = current_state
            evaluation_list.append(evaluateTaken(new_state, player))
            board_list.append(new_board)
        #nadji maksimalnu evaluaciju i stavi tu tabelu kao trenutnu
        best_move_index = evaluation_list.index(max(evaluation_list))
        board = board_list[best_move_index]
        return board
    #ako su sve u millu
    else:
        evaluation_list = []
        board_list = []
        for piece in player_pieces:
            new_board = copy.deepcopy(board)
            del new_board[piece]
            new_state = TreeNode(new_board)
            new_state.parent = current_state
            evaluation_list.append(evaluateTaken(new_state, player))
            board_list.append(new_board)
        # nadji maksimalnu evaluaciju i stavi tu tabelu kao trenutnu
        best_move_index = evaluation_list.index(max(evaluation_list))
        board = board_list[best_move_index]
        return board


def blockedPieces(current_state, player):
    #vraca listu blokiranih figura odredjenog igraca
    board = current_state.position
    blocked_list = []
    #blokirane sa dve strane
    if board[0] == player and 3 in board and 30 in board:
        blocked_list.append(0)
    if board[6] == player and 3 in board and 36 in board:
        blocked_list.append(6)
    if board[60] == player and 30 in board and 63 in board:
        blocked_list.append(60)
    if board[66] == player and 63 in board and 36 in board:
        blocked_list.append(66)
    if board[11] == player and 31 in board and 13 in board:
        blocked_list.append(11)
    if board[51] == player and 31 in board and 53 in board:
        blocked_list.append(51)
    if board[55] == player and 53 in board and 35 in board:
        blocked_list.append(55)
    if board[15] == player and 13 in board and 35 in board:
        blocked_list.append(15)
    if board[22] == player and 32 in board and 23 in board:
        blocked_list.append(22)
    if board[42] == player and 32 in board and 43 in board:
        blocked_list.append(42)
    if board[44] == player and 43 in board and 34 in board:
        blocked_list.append(44)
    if board[24] == player and 23 in board and 34 in board:
        blocked_list.append(24)
    #blokirane sa tri strane
    if board[3] == player and 0 in board and 6 in board and 13 in board:
        blocked_list.append(3)
    if board[23] == player and 13 in board and 22 in board and 24 in board:
        blocked_list.append(23)
    if board[30] == player and 31 in board and 0 in board and 60 in board:
        blocked_list.append(30)
    if board[32] == player and 31 in board and 22 in board and 42 in board:
        blocked_list.append(32)
    if board[63] == player and 53 in board and 60 in board and 66 in board:
        blocked_list.append(63)
    if board[43] == player and 53 in board and 42 in board and 44 in board:
        blocked_list.append(43)
    if board[36] == player and 35 in board and 6 in board and 66 in board:
        blocked_list.append(36)
    if board[34] == player and 35 in board and 24 in board and 44 in board:
        blocked_list.append(34)
    #blokiranje sa cetiri strane
    if board[13] == player and 3 in board and 11 in board and 15 in board and 23 in board:
        blocked_list.append(13)
    if board[31] == player and 11 in board and 30 in board and 51 in board and 32 in board:
        blocked_list.append(31)
    if board[53] == player and 51 in board and 43 in board and 55 in board and 63 in board:
        blocked_list.append(53)
    if board[35] == player and 34 in board and 36 in board and 15 in board and 55 in board:
        blocked_list.append(35)

    return blocked_list


def threePieces(two_pieces_list):
    no_duplicates_list = list(dict.fromkeys(two_pieces_list))
    three_pieces = 0
    for piece in no_duplicates_list:
        count = two_pieces_list.count(piece)
        if count == 2:
            three_pieces += 1
        if count == 3:
            three_pieces += 2
    return three_pieces


def millCreated(last_board, new_board, player):
    mill_list = mills(last_board, player)
    new_mill_list = mills(new_board, player)
    if len(new_mill_list) > len(mill_list):
        return True
    elif len(new_mill_list) > 0 and len(new_mill_list) == len(mill_list) and mill_list != new_mill_list:
        return True
    else:
        return False


def playerPieces(board, player):
    cordinate_list = []
    for cordinates in board:
        if board[cordinates] == player:
            cordinate_list.append(cordinates)
    return cordinate_list


def mills(board, player):
    mill_cordinates = []
    pieces_list = playerPieces(board, player)

    #proveravamo da li postoje formirane mice horizontalno
    if 0 in pieces_list and 3 in pieces_list and 6 in pieces_list:
        mill_cordinates += [0, 3, 6]
    if 11 in pieces_list and 13 in pieces_list and 15 in pieces_list:
        mill_cordinates += [11, 13, 15]
    if 22 in pieces_list and 23 in pieces_list and 24 in pieces_list:
        mill_cordinates += [22, 23, 24]
    if 30 in pieces_list and 31 in pieces_list and 32 in pieces_list:
        mill_cordinates += [30, 31, 32]
    if 34 in pieces_list and 35 in pieces_list and 36 in pieces_list:
        mill_cordinates += [34, 35, 36]
    if 42 in pieces_list and 43 in pieces_list and 44 in pieces_list:
        mill_cordinates += [42, 43, 44]
    if 51 in pieces_list and 53 in pieces_list and 55 in pieces_list:
        mill_cordinates += [51, 53, 55]
    if 60 in pieces_list and 63 in pieces_list and 66 in pieces_list:
        mill_cordinates += [60, 63, 66]
    #vertikalno
    if 0 in pieces_list and 30 in pieces_list and 60 in pieces_list:
        mill_cordinates += [0, 30, 60]
    if 11 in pieces_list and 31 in pieces_list and 51 in pieces_list:
        mill_cordinates += [11, 31, 51]
    if 22 in pieces_list and 32 in pieces_list and 42 in pieces_list:
        mill_cordinates += [22, 32, 42]
    if 3 in pieces_list and 13 in pieces_list and 23 in pieces_list:
        mill_cordinates += [3, 13, 23]
    if 43 in pieces_list and 53 in pieces_list and 63 in pieces_list:
        mill_cordinates += [43, 53, 63]
    if 24 in pieces_list and 34 in pieces_list and 44 in pieces_list:
        mill_cordinates += [24, 34, 44]
    if 15 in pieces_list and 35 in pieces_list and 55 in pieces_list:
        mill_cordinates += [15, 35, 55]
    if 6 in pieces_list and 36 in pieces_list and 66 in pieces_list:
        mill_cordinates += [6, 36, 66]

    return mill_cordinates


def doubleMills(mill_list):
    no_duplicates = list(dict.fromkeys(mill_list))
    doubles = 0
    for piece in no_duplicates:
        count = mill_list.count(piece)
        if count == 2:
            doubles += 1
    return doubles


def twoPieces(board, player):
    two_piece_cordinates = []
    pieces_list = playerPieces(board, player)
    #horizontalno proveravanje dve figure pored druge
    if 0 in pieces_list and 3 in pieces_list and 6 not in pieces_list:
        two_piece_cordinates += [0, 3]
    if 3 in pieces_list and 6 in pieces_list and 0 not in pieces_list:
        two_piece_cordinates += [3, 6]
    if 11 in pieces_list and 13 in pieces_list and 15 not in pieces_list:
        two_piece_cordinates += [11, 13]
    if 13 in pieces_list and 15 in pieces_list and 11 not in pieces_list:
        two_piece_cordinates += [13, 15]
    if 22 in pieces_list and 23 in pieces_list and 24 not in pieces_list:
        two_piece_cordinates += [22, 23]
    if 23 in pieces_list and 24 in pieces_list and 22 not in pieces_list:
        two_piece_cordinates += [23, 24]
    if 30 in pieces_list and 31 in pieces_list and 32 not in pieces_list:
        two_piece_cordinates += [30, 31]
    if 31 in pieces_list and 32 in pieces_list and 30 not in pieces_list:
        two_piece_cordinates += [31, 32]
    if 34 in pieces_list and 35 in pieces_list and 36 not in pieces_list:
        two_piece_cordinates += [34, 35]
    if 35 in pieces_list and 36 in pieces_list and 34 not in pieces_list:
        two_piece_cordinates += [35, 36]
    if 42 in pieces_list and 43 in pieces_list and 44 not in pieces_list:
        two_piece_cordinates += [42, 43]
    if 43 in pieces_list and 44 in pieces_list and 42 not in pieces_list:
        two_piece_cordinates += [43, 44]
    if 51 in pieces_list and 53 in pieces_list and 55 not in pieces_list:
        two_piece_cordinates += [51, 53]
    if 53 in pieces_list and 55 in pieces_list and 51 not in pieces_list:
        two_piece_cordinates += [53, 55]
    if 60 in pieces_list and 63 in pieces_list and 66 not in pieces_list:
        two_piece_cordinates += [60, 63]
    if 63 in pieces_list and 66 in pieces_list and 60 not in pieces_list:
        two_piece_cordinates += [63, 66]
    #vertikalno
    if 0 in pieces_list and 30 in pieces_list and 60 not in pieces_list:
        two_piece_cordinates += [0, 30]
    if 30 in pieces_list and 60 in pieces_list and 0 not in pieces_list:
        two_piece_cordinates += [30, 60]
    if 11 in pieces_list and 31 in pieces_list and 51 not in pieces_list:
        two_piece_cordinates += [11, 31]
    if 31 in pieces_list and 51 in pieces_list and 11 not in pieces_list:
        two_piece_cordinates += [31, 51]
    if 22 in pieces_list and 32 in pieces_list and 42 not in pieces_list:
        two_piece_cordinates += [22, 32]
    if 32 in pieces_list and 42 in pieces_list and 22 not in pieces_list:
        two_piece_cordinates += [32, 42]
    if 3 in pieces_list and 13 in pieces_list and 23 not in pieces_list:
        two_piece_cordinates += [3, 13]
    if 13 in pieces_list and 23 in pieces_list and 3 not in pieces_list:
        two_piece_cordinates += [13, 23]
    if 43 in pieces_list and 53 in pieces_list and 63 not in pieces_list:
        two_piece_cordinates += [43, 53]
    if 53 in pieces_list and 63 in pieces_list and 43 not in pieces_list:
        two_piece_cordinates += [53, 63]
    if 24 in pieces_list and 34 in pieces_list and 44 not in pieces_list:
        two_piece_cordinates += [24, 34]
    if 34 in pieces_list and 44 in pieces_list and 24 not in pieces_list:
        two_piece_cordinates += [34, 44]
    if 15 in pieces_list and 35 in pieces_list and 55 not in pieces_list:
        two_piece_cordinates += [15, 35]
    if 35 in pieces_list and 55 in pieces_list and 15 not in pieces_list:
        two_piece_cordinates += [35, 55]
    if 6 in pieces_list and 36 in pieces_list and 66 not in pieces_list:
        two_piece_cordinates += [6, 36]
    if 36 in pieces_list and 66 in pieces_list and 6 not in pieces_list:
        two_piece_cordinates += [36, 66]
    return two_piece_cordinates


def evaluate(current_node, phase):
    board = current_node.position
    closed_mill = 0
    if millCreated(current_node.parent.position, current_node.position, PLAYER):
        closed_mill = 1
    elif millCreated(current_node.parent.position, current_node.position, OPPOSITE_PLAYER):
        closed_mill = -1
    mills_player = mills(board, PLAYER)
    mills_op_player = mills(board, OPPOSITE_PLAYER)
    number_of_mills = len(mills_player) - len(mills_op_player)
    number_of_blocked = len(blockedPieces(current_node, OPPOSITE_PLAYER)) - len(blockedPieces(current_node, PLAYER))
    number_of_pieces = len(playerPieces(board, PLAYER)) - len(playerPieces(board, OPPOSITE_PLAYER))

    two_pieces_player = twoPieces(board, PLAYER)
    two_pieces_op_player = twoPieces(board, OPPOSITE_PLAYER)
    number_of_two_pieces = len(two_pieces_player) - len(two_pieces_op_player)

    three_pieces_player = threePieces(two_pieces_player)
    three_pieces_op_player = threePieces(two_pieces_op_player)
    number_of_three_pieces = three_pieces_player - three_pieces_op_player

    double_mills_player = doubleMills(mills_player)
    double_mills_op_player = doubleMills(mills_op_player)
    number_of_double_mills = double_mills_player - double_mills_op_player
    if phase == 1:
        return 100 * closed_mill + 70 * number_of_mills + 20 * number_of_blocked + 75 * number_of_pieces + 40 * number_of_two_pieces + 70 * number_of_three_pieces
    elif phase == 2:
        return 150 * closed_mill + 80 * number_of_mills + 68 * number_of_blocked + 84 * number_of_pieces + 90 * number_of_double_mills
    elif phase == 3:
        return 400 * closed_mill + 120 * number_of_two_pieces + 100 * number_of_three_pieces


def evaluateTaken(current_node, player):
    opposite_player = None
    if player == "W":
        opposite_player = "B"
    else:
        opposite_player = "W"
    board = current_node.position
    closed_mill = 0
    if millCreated(current_node.parent.position, current_node.position, player):
        closed_mill = 1
    elif millCreated(current_node.parent.position, current_node.position, opposite_player):
        closed_mill = -1
    mills_player = mills(board, player)
    mills_opposite_player = mills(board, opposite_player)
    number_of_mills = len(mills_player) - len(mills_opposite_player)
    number_of_blocked = len(blockedPieces(current_node, opposite_player)) - len(blockedPieces(current_node, player))
    number_of_pieces = len(playerPieces(board, player)) - len(playerPieces(board, opposite_player))

    two_pieces_player = twoPieces(board, player)
    two_pieces_opposite_player = twoPieces(board, opposite_player)
    number_of_two_pieces = len(two_pieces_player) - len(two_pieces_opposite_player)

    three_pieces_player = threePieces(two_pieces_player)
    three_pieces_opposite_player = threePieces(two_pieces_opposite_player)
    number_of_three_pieces = three_pieces_player - three_pieces_opposite_player

    double_mills_player = doubleMills(mills_player)
    double_mills_opposite_player = doubleMills(mills_opposite_player)
    number_of_double_mills = double_mills_player - double_mills_opposite_player
    return 1000 * closed_mill + 70 * number_of_mills + 10 * number_of_blocked + 50 * number_of_pieces + 20 * number_of_two_pieces + 70 * number_of_three_pieces


class TreeNode(object):
    __slots__ = 'parent', 'children', 'position'

    def __init__(self, position):
        self.parent = None
        self.children = []
        self.position = position

    def is_root(self):
        return self.parent is None

    def is_leaf(self):
        return len(self.children) == 0

    def add_child(self, node):
        node.parent = self
        self.children.append(node)


class Tree(object):
    def __init__(self):
        self.root = None

    def is_empty(self):
        return self.root is None

    def depth(self, node):
        if node.is_root():
            return 0
        else:
            return 1 + self.depth(node.parent)

    def _height(self, node):
        if node.is_leaf():
            return 0
        else:
            return 1 + max(self._height(child) for child in node.children)

    def height(self):
        return self._height(self.root)


class HashMap:
    def __init__(self):
        self.size = 7
        self.map = [None] * self.size

    def _get_hash(self, key):
        if key > 66 or key % 10 > 6:
            raise IndexError("bad key!!!")
        return key // 10

    def __setitem__(self, key, value):
        key_hash = self._get_hash(key)
        key_value = [key, value]

        if self.map[key_hash] is None:
            self.map[key_hash] = list([key_value])
            return True
        else:
            for pair in self.map[key_hash]:
                if pair[0] == key:
                    pair[1] = value
                    return True
            self.map[key_hash].append(key_value)
            return True

    def __getitem__(self, key):
        key_hash = self._get_hash(key)
        if self.map[key_hash] is not None:
            for pair in self.map[key_hash]:
                if pair[0] == key:
                    return pair[1]
        return None

    def __delitem__(self, key):
        key_hash = self._get_hash(key)
        if self.map[key_hash] is None:
            return False
        for i in range(0, len(self.map[key_hash])):
            if self.map[key_hash][i][0] == key:
                self.map[key_hash].pop(i)
                if len(self.map[key_hash]) == 0:
                    self.map[key_hash] = None
                return True
        return False

    def keys(self):
        key_list = []
        for bucket in self.map:
            if bucket is not None:
                for pair in bucket:
                    key_list.append(pair[0])
        return key_list

    def values(self):
        values = []
        for bucket in self.map:
            if bucket is not None:
                for pair in bucket:
                    values.append(pair[1])
        return values

    def __len__(self):
        return len(self.keys())

    def __contains__(self, key):
        if key in self.keys():
            return True
        return False

    def __iter__(self):
        for bucket in self.map:
            if bucket is not None:
                for item in bucket:
                    yield item[0]




if __name__ == '__main__':
    main()
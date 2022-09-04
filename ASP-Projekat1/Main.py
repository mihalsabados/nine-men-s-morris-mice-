import copy
import sys

from HashMap import HashMap
from Tree import Tree, TreeNode

MAP= "   0123456\n"\
       "0: 0--0--0\n" \
       "1: |0-0-0|\n" \
       "2: ||000||\n" \
       "3: 000■000\n" \
       "4: ||000||\n" \
       "5: |0-0-0|\n" \
       "6: 0--0--0"
BOARD_MATRIX = [list(i) for i in MAP.split("\n")]
INFINITY = sys.maxsize
AVAILABLE_CORDINATES = [0, 3, 6, 11, 13, 15, 22, 23, 24, 30, 31, 32, 34, 35, 36, 42, 43, 44, 51, 53, 55, 60, 63, 66]
PHASE = 1

HUMAN = None
AI = None


def main():
    global HUMAN
    global AI
    global PHASE
    print("---------MICE---------")
    HUMAN = input("Izaberi (W(white) ili B(black)):")
    while HUMAN != "W" and HUMAN != "B":
        print("Loše slovo, morate uneti W ili B")
        HUMAN = input("Izaberi (W(white) ili B(black)):")
    if HUMAN == "W":
        AI = "B"
    else:
        AI = "W"
    #pravljenje karte, u koju se stavlja samo polja koja su zauzeta
    board = HashMap()
    #stablo
    tree = Tree()
    current_state = TreeNode(board)
    tree.root = current_state
    player = HUMAN
    #prva faza
    available_figures = 9
    while True:
        tree.root.children = []
        if available_figures == 0:         #ukoliko je sve figure postavio, predji na drugu fazu
            break
        #ispis tabele
        drawBoard(board)
        player = HUMAN
        #unos kordinate
        while True:
            set_cordinates = None
            try:
                set_cordinates = int(input("postavi figuru na (redkolona)(00,03,23):"))
            except:
                print("Loš unos!")
            if set_cordinates not in AVAILABLE_CORDINATES:
                print("Kordinata koju ste uneli ne postoji!")
            elif set_cordinates in board:
                print("Polje je već zauzeto!")
            else:
                board[set_cordinates] = HUMAN
                break
        # ispis tabele
        drawBoard(board)

        #ako je covek napravio micu onda bira da uzme protivnicku figuru
        if available_figures <= 7 and millCreated(tree.root.parent.position, tree.root.position, player):
            pickOponentsPieceHuman(tree.root)
            # ispis tabele
            drawBoard(board)

        print("AI potez:")
        player = AI
        #AI na potezu, kreira drvo a zatim bira najbolju putanju
        createChildrenFirstPhase(tree.root, 3, player, available_figures)
        next_move = minimax(tree.root, 3, -INFINITY, +INFINITY, True, True, PHASE)
        tree.root = next_move
        board = tree.root.position

        #smanji broj figura koje trebaju da se dodaju
        available_figures -= 1



    #druga faza
    while True:
        human_pieces = len(playerPieces(board, HUMAN))
        ai_pieces = len(playerPieces(board, AI))
        tree.root.children = []
        player = HUMAN
        movable_figures_HUMAN = movableFigures(tree.root, HUMAN)
        movable_figures_AI = movableFigures(tree.root, AI)
        free_cordinates = [piece for piece in AVAILABLE_CORDINATES if piece not in board]

        if human_pieces < 3 or (len(movable_figures_HUMAN) == 0 and human_pieces > 3):
            print("Igra je gotova, IZGUBILI STE..")
            break
        if ai_pieces < 3 or (len(movable_figures_AI) == 0 and ai_pieces > 3):
            print("Igra je gotova, POBEDILI STE.")
            break
        if ai_pieces == 3 and human_pieces == 3:
            print("Igra je gotova, NEREŠENO.")
            break
        #ispis tabele
        drawBoard(board)

        # unos kordinate koju igrac premesta
        while True:
            from_cordinates = None
            try:
                from_cordinates = int(input("izaberi figuru koju premeštaš (redkolona)(00,03,23):"))
            except:
                print("Loš unos!")
            if from_cordinates not in movable_figures_HUMAN:
                print("Kordinata koju ste uneli ne postoji ili je blokirana!")
            else:
                #trazimo sve susedne figure(na koje mogu da se pomere) kordinate
                neighbour_pieces = findNeighbours(from_cordinates)
                #unos kordinate na koju se figura pomera
                while True:
                    to_cordinates = None
                    try:
                        to_cordinates = int(input("izaberi na koju poziciju premeštaš (redkolona)(00,03,23):"))
                    except:
                        print("Loš unos!")
                    if human_pieces > 3:
                        PHASE = 2
                        #proveravamo da li su uneta slobodna komsijska pojla
                        if to_cordinates not in neighbour_pieces or to_cordinates not in free_cordinates:
                            print("Pogrešno polje!")
                        elif to_cordinates in neighbour_pieces and to_cordinates in free_cordinates:
                            del board[from_cordinates]
                            board[to_cordinates] = player
                            break
                    elif human_pieces == 3:
                        PHASE = 3
                        # proveravamo da li su uneta slobodna polja
                        if to_cordinates not in free_cordinates:
                            print("Pogrešno polje!")
                        else:
                            del board[from_cordinates]
                            board[to_cordinates] = player
                            break
                break
        # ispis tabele
        drawBoard(board)
        if millCreated(tree.root.parent.position, tree.root.position, player):
            pickOponentsPieceHuman(tree.root)
            # ispis tabele
            drawBoard(board)

        ai_pieces = len(playerPieces(board, AI))
        if ai_pieces < 3 or (len(movable_figures_AI) == 0 and ai_pieces > 3):
            print("Igra je gotova, POBEDILI STE.")
            break

        player = AI
        # AI na potezu, kreira drvo a zatim bira najbolju putanju
        createChildrenSecondPhase(tree.root, 3, player)
        next_move = minimax(tree.root, 3, -INFINITY, +INFINITY, True, True, PHASE)
        tree.root = next_move
        board = tree.root.position


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


def drawBoard(board):
    for i in range(len(BOARD_MATRIX)):
        for j in range(len(BOARD_MATRIX[i])):
            key = (i-1) * 10 + (j - 3)
            if key in board:
                print(board[key], end="")
            else:
                print(BOARD_MATRIX[i][j], end="")
        print()


def evaluate(current_node, phase):
    board = current_node.position
    closed_mill = 0
    if millCreated(current_node.parent.position, current_node.position, AI):
        closed_mill = 1
    elif millCreated(current_node.parent.position, current_node.position, HUMAN):
        closed_mill = -1
    mills_ai = mills(board, AI)
    mills_human = mills(board, HUMAN)
    number_of_mills = len(mills_ai) - len(mills_human)
    number_of_blocked = len(blockedPieces(current_node, HUMAN)) - len(blockedPieces(current_node, AI))
    number_of_pieces = len(playerPieces(board, AI)) - len(playerPieces(board, HUMAN))

    two_pieces_ai = twoPieces(board, AI)
    two_pieces_human = twoPieces(board, HUMAN)
    number_of_two_pieces = len(two_pieces_ai) - len(two_pieces_human)

    three_pieces_ai = threePieces(two_pieces_ai)
    three_pieces_human = threePieces(two_pieces_human)
    number_of_three_pieces = three_pieces_ai - three_pieces_human

    double_mills_ai = doubleMills(mills_ai)
    double_mills_human = doubleMills(mills_human)
    number_of_double_mills = double_mills_ai - double_mills_human
    if phase == 1:
        return 100 * closed_mill + 70 * number_of_mills + 20 * number_of_blocked + 75 * number_of_pieces + 40 * number_of_two_pieces + 70 * number_of_three_pieces
    elif phase == 2:
        return 150 * closed_mill + 80 * number_of_mills + 68 * number_of_blocked + 84 * number_of_pieces + 90 * number_of_double_mills
    elif phase == 3:
        return 400 * closed_mill + 120 * number_of_two_pieces + 100 * number_of_three_pieces


def evaluateTaken(current_node, player, phase):
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
    if phase == 1:
        return 1000 * closed_mill + 70 * number_of_mills + 10 * number_of_blocked + 50 * number_of_pieces + 20 * number_of_two_pieces + 70 * number_of_three_pieces
    elif phase == 2:
        return 2000 * closed_mill + 60 * number_of_mills + 50 * number_of_blocked + 25 * number_of_pieces + 50 * number_of_double_mills
    elif phase == 3:
        return 4000 * closed_mill + 200 * number_of_two_pieces + 100 * number_of_three_pieces


def createChildrenFirstPhase(node, depth, player, available_figures):
    board = node.position
    if depth == 0:
        return
    if available_figures == 0:
        node.children = []
        createChildrenSecondPhase(node, depth, player)
    next_player = None
    if player == HUMAN:
        next_player = AI
    else:
        next_player = HUMAN
    available_cordinates = [cordinate for cordinate in AVAILABLE_CORDINATES if cordinate not in board]
    if len(node.children) == 0:
        for cordinate in available_cordinates:
            new_board = copy.deepcopy(board)
            child = TreeNode(new_board)
            node.add_child(child)
            new_board[cordinate] = player
            if millCreated(child.parent.position, new_board, player):
                child.position = pickOponentsPiece(child, player, 1)
            createChildrenFirstPhase(child, depth - 1, next_player, available_figures-0.5)
    else:
        for child in node.children:
            createChildrenFirstPhase(child, depth - 1, next_player, available_figures - 0.5)


def createChildrenSecondPhase(node, depth, player):
    board = node.position
    if depth == 0:
        return
    next_player = None
    if player == HUMAN:
        next_player = AI
    else:
        next_player = HUMAN
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
                        pickOponentsPiece(child, player, 2)
                    createChildrenSecondPhase(child, depth - 1, next_player)
    #ako igrac ima 3 figure (treca faza)
    elif len(player_pieces) == 3:
        for from_cordinates in player_pieces:
            new_board = copy.deepcopy(board)
            del new_board[from_cordinates]
            for to_cordinates in free_cordinates:
                if to_cordinates not in new_board:
                    new_board2 = copy.deepcopy(new_board)
                    child = TreeNode(new_board2)
                    node.add_child(child)
                    new_board2[to_cordinates] = player
                    if millCreated(child.parent.position, new_board2, player):
                        pickOponentsPiece(child, player, 3)
                    createChildrenSecondPhase(child, depth - 1, next_player)
    #ako igrac ima manje od 3 figure onda se ne grana vise odnosno taj cvor je list (game over)
    else:
        return


def pickOponentsPieceHuman(current_state):
    #covek bira koju figuru zeli da uzme protivniku
    board = current_state.position
    ai_pieces = playerPieces(board, AI)
    ai_mill_pieces = mills(board, AI)
    non_mill_pieces = [piece for piece in ai_pieces if piece not in ai_mill_pieces]
    cordinates = int(input("Koju figuru želite da uzmete protivniku:"))
    while True:
        is_valid = False
        #ako nema figura izvan mice
        if len(non_mill_pieces) == 0:
            if cordinates in ai_pieces:
                is_valid = True
                del board[cordinates]
                current_state.position = board
        #ako ima figura izvan mice
        else:
            if cordinates in non_mill_pieces:
                is_valid = True
                del board[cordinates]
                current_state.position = board
        if is_valid:
            print("Figura je uklonjena")
            break
        print("Kordinate nisu ispravne, pokušajte ponovo.")
        cordinates = int(input("Koju figuru želite da uzmete protivniku:"))


def pickOponentsPiece(current_state, player, phase):
    board = current_state.position
    oposite_player = None
    if player == HUMAN:
        oposite_player = AI
    else:
        oposite_player = HUMAN

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
            evaluation_list.append(evaluateTaken(new_state, player, phase))
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
            evaluation_list.append(evaluateTaken(new_state, player, phase))
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


if __name__ == '__main__':
    main()

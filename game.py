
from copy import deepcopy
import pygame
from pygame.locals import *
from sys import exit
import random

'''
VARIABLES
'''

turn = 'white'
selected = (0, 1)  # a tuple keeping track of which piece is selected
board = 0
move_limit = [150, 0]

best_move = ()
black, white = (), ()

window_size = (256,256)
background_image_filename = 'board_brown.png'
title = 'CHECKERS'
board_size = 8
left = 1
fps = 10
pause = 7
start = True

'''
CLASSES
'''
class Piece(object):
    def __init__(self, color, king):
        self.color = color
        self.king = king

class Player(object):
    def __init__(self, type, color, strategy, ply_depth):
        self.type = type
        self.color = color
        self.strategy = strategy
        self.ply_depth = ply_depth

'''
FUNCTIONS
'''

def init_board():
    global move_limit
    move_limit[1] = 0

    result = [
        [0, 1, 0, 1, 0, 1, 0, 1],
        [1, 0, 1, 0, 1, 0, 1, 0],
        [0, 1, 0, 1, 0, 1, 0, 1],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [-1, 0, -1, 0, -1, 0, -1, 0],
        [0, -1, 0, -1, 0, -1, 0, -1],
        [-1, 0, -1, 0, -1, 0, -1, 0]
    ]
    for m in range(8):
        for n in range(8):
            if (result[m][n] == 1):
                piece = Piece('black', False)
                result[m][n] = piece
            elif (result[m][n] == -1):
                piece = Piece('white', False)
                result[m][n] = piece
    return result #array which contains object of pieces class

def init_player(type, color, strategy, ply_depth):
    return Player(type, color, strategy, ply_depth)


def avail_moves(board, player):
    moves = []

    for m in range(8):
        for n in range(8):
            if board[m][n] != 0 and board[m][n].color == player:
                if can_jump([m, n], [m + 1, n + 1], [m + 2, n + 2], board) == True:
                    moves.append([m, n, m + 2, n + 2])
                if can_jump([m, n], [m - 1, n + 1], [m - 2, n + 2], board) == True:
                    moves.append([m, n, m - 2, n + 2])
                if can_jump([m, n], [m + 1, n - 1], [m + 2, n - 2], board) == True:
                    moves.append([m, n, m + 2, n - 2])
                if can_jump([m, n], [m - 1, n - 1], [m - 2, n - 2], board) == True:
                    moves.append([m, n, m - 2, n - 2])

    '''IF NO JUMPS THEN CHECK FOR REGULAR MOVES'''
    if len(moves) == 0:
        for m in range(8):
            for n in range(8):
                if board[m][n] != 0 and board[m][n].color == player:
                    if can_move([m, n], [m + 1, n + 1], board) == True:
                        moves.append([m, n, m + 1, n + 1])
                    if can_move([m, n], [m - 1, n + 1], board) == True:
                        moves.append([m, n, m - 1, n + 1])
                    if can_move([m, n], [m + 1, n - 1], board) == True:
                        moves.append([m, n, m + 1, n - 1])
                    if can_move([m, n], [m - 1, n - 1], board) == True:
                        moves.append([m, n, m - 1, n - 1])

    return moves


def can_jump(a, via, b, board):

    '''JUMPING OUT OF BOARD'''
    if b[0] < 0 or b[0] > 7 or b[1] < 0 or b[1] > 7:
        return False

    '''JUMPING INTO SOME PIECE'''
    if board[b[0]][b[1]] != 0:
        return False

    if board[via[0]][via[1]] == 0:
        return False

    if board[a[0]][a[1]].color == 'white':
        if board[a[0]][a[1]].king == False and b[0] > a[0]:
            return False  # only move up
        if board[via[0]][via[1]].color != 'black':
            return False  # only jump blacks
        return True  # jump is possible

    if board[a[0]][a[1]].color == 'black':
        if board[a[0]][a[1]].king == False and b[0] < a[0]:
            return False  # only move down
        if board[via[0]][via[1]].color != 'white':
            return False  # only jump whites
        return True  # jump is possible


def can_move(a, b, board):

    if b[0] < 0 or b[0] > 7 or b[1] < 0 or b[1] > 7:
        return False

    if board[b[0]][b[1]] != 0:
        return False

    if board[a[0]][a[1]].king == False and board[a[0]][a[1]].color == 'white':
        if b[0] > a[0]:
            return False  # only move up
        return True  # move is possible

    if board[a[0]][a[1]].king == False and board[a[0]][a[1]].color == 'black':
        if b[0] < a[0]:
            return False  # only move down
        return True  # move is possible

    if board[a[0]][a[1]].king == True:
        return True  # move is possible

def make_move(a, b, board):
    board[b[0]][b[1]] = board[a[0]][a[1]]  # make the move
    board[a[0]][a[1]] = 0

    if b[0] == 0 and board[b[0]][b[1]].color == 'white':
        board[b[0]][b[1]].king = True
    if b[0] == 7 and board[b[0]][b[1]].color == 'black':
        board[b[0]][b[1]].king = True

    if (a[0] - b[0]) % 2 == 0:
        board[int((a[0] + b[0]) / 2)][int((a[1] + b[1]) / 2)] = 0  # delete the jumped piece



def evaluate(game, player):
    '''
    Piece=100
    King=175
    Add up the pieces and returns the differece
     '''

    def simple_score(game, player):
        black, white = 0, 0
        for m in range(8):
            for n in range(8):
                if (game[m][n] != 0 and game[m][n].color == 'black'):
                    if game[m][n].king == False:
                        black += 100
                    else:
                        black += 175
                elif (game[m][n] != 0 and game[m][n].color == 'white'):
                    if game[m][n].king == False:
                        white += 100
                    else:
                        white += 175
        if player != 'black':
            return white - black
        else:
            return black - white

    '''add bonus to pieces going to opposing side '''

    def piece_rank(game, player):
        black, white = 0, 0
        for m in range(8):
            for n in range(8):
                if (game[m][n] != 0 and game[m][n].color == 'black'):
                    if game[m][n].king != True:
                        black = black + (m * m)
                elif (game[m][n] != 0 and game[m][n].color == 'white'):
                    if game[m][n].king != True:
                        white = white + ((7 - m) * (7 - m))
        if player != 'black':
            return white - black
        else:
            return black - white

    ''' a king on an edge could become trapped, thus deduce some points '''

    def edge_king(game, player):
        black, white = 0, 0
        for m in range(8):
            if (game[m][0] != 0 and game[m][0].king != False):
                if game[m][0].color != 'white':
                    black += -25
                else:
                    white += -25
            if (game[m][7] != 0 and game[m][7].king != False):
                if game[m][7].color != 'white':
                    black += -25
                else:
                    white += -25
        if player != 'black':
            return white - black
        else:
            return black - white

    return (simple_score(game, player) + piece_rank(game, player) + edge_king(game, player)) * 1

def end_game(board):
    black, white = 0, 0
    for m in range(8):
        for n in range(8):
            if board[m][n] != 0:
                if board[m][n].color == 'black':
                    black += 1
                else:
                    white += 1

    return black, white


'''will generate possible moves and board states until a given depth'''
def minimax(board, player, ply):
    global best_move

    ply_depth = 0
    if player != 'black':
        ply_depth = white.ply_depth
    else:
        ply_depth = black.ply_depth

    end = end_game(board)

    ''' if node is a terminal node or depth = CutoffDepth '''
    if ply >= ply_depth or end[0] == 0 or end[1] == 0:  # are we still playing?
        ''' return the heuristic value of node '''
        score = evaluate(board, player)  # return evaluation of board as we have reached final ply or end state
        return score

    ''' if the adversary is to play at node '''
    if player != turn:  # if the opponent is to play on this node...

        ''' let beta := +infinity '''
        beta = +10000

        ''' foreach child of node '''
        moves = avail_moves(board, player)  # get the available moves for player
        for i in range(len(moves)):
            # create a deep copy of the board (otherwise pieces would be just references)
            new_board = deepcopy(board)
            make_move((moves[i][0], moves[i][1]), (moves[i][2], moves[i][3]), new_board)  # make move on new board

            ''' beta := min(beta, minimax(child, depth+1)) '''
            # ...make a switch of players for minimax...
            if player == 'black':
                player = 'white'
            else:
                player = 'black'

            temp_beta = minimax(new_board, player, ply + 1)
            if temp_beta < beta:
                beta = temp_beta  # take the lowest beta

        ''' return beta '''
        return beta

    else:  # else we are to play
        ''' else {we are to play at node} '''
        ''' let alpha := -infinity '''
        alpha = -10000

        ''' foreach child of node '''
        moves = avail_moves(board, player)  # get the available moves for player
        for i in range(len(moves)):
            # create a deep copy of the board (otherwise pieces would be just references)
            new_board = deepcopy(board)
            make_move((moves[i][0], moves[i][1]), (moves[i][2], moves[i][3]), new_board)  # make move on new board

            ''' alpha := max(alpha, minimax(child, depth+1)) '''
            # ...make a switch of players for minimax...
            if player == 'black':
                player = 'white'
            else:
                player = 'black'

            temp_alpha = minimax(new_board, player, ply + 1)
            if temp_alpha > alpha:
                alpha = temp_alpha  # take the highest alpha
                if ply == 0:
                    best_move = (moves[i][0], moves[i][1]), (moves[i][2], moves[i][3])  # save the move as it's our turn

        ''' return alpha '''
        return alpha

def end_turn():
    global turn
    if turn != 'black':
        turn = 'black'
    else:
        turn = 'white'

def cpu_play(player):
    global board, move_limit

    if player.strategy == 'minimax':
        alpha = minimax(board, player.color, 0)

    if alpha == -10000:  # no more moves available... all is lost
        if player.color == white:
            show_winner("black")
        else:
            show_winner("white")

    make_move(best_move[0], best_move[1], board)  # make the move on board
    move_limit[1] += 1  # add to move limit
    end_turn()  # end turn


# make changes to ply's if playing vs human (problem with scope)
def ply_check():
    global black, white

    ''' if human has higher ply_setting, cpu will do unnecessary calculations '''
    if black.type != 'cpu':
        black.ply_depth = white.ply_depth
    elif white.type != 'cpu':
        white.ply_depth = black.ply_depth

def game_init(difficulty):
    global black, white

    if difficulty == 'hard':
        black = init_player('cpu', 'black', 'minimax', 1)
        white = init_player('human', 'white', 'minimax', 1)
        board = init_board()
    else:
        black = init_player('cpu', 'black', 'minimax', 1)
        white = init_player('human', 'white', 'minimax', 1)
        board = init_board()

    return board


'''GUI FUNCTION'''

def draw_piece(row, column, color, king):

    posX = int(((window_size[0] / 8) * column) - (window_size[0] / 8) / 2)
    posY = int(((window_size[1] / 8) * row) - (window_size[1] / 8) / 2)

    if color == 'black':
        border_color = (255, 255, 255)
        inner_color = (0, 0, 0)
    elif color == 'white':
        border_color = (0, 0, 0)
        inner_color = (255, 255, 255)

    pygame.draw.circle(screen, border_color, (posX, posY), 12)
    pygame.draw.circle(screen, inner_color, (posX, posY), 10)

    if king == True:
        pygame.draw.circle(screen, border_color, (posX + 3, posY - 3), 12)  # draw piece border
        pygame.draw.circle(screen, inner_color, (posX + 3, posY - 3), 10)  # draw piece

def show_message(message):
    text = font.render(' ' + message + ' ', True, (255, 255, 255), (120, 195, 46))
    textRect = text.get_rect()
    textRect.centerx = screen.get_rect().centerx
    textRect.centery = screen.get_rect().centery
    screen.blit(text, textRect)


def show_countdown(i):
    while i >= 0:
        tim = font_big.render(' ' + repr(i) + ' ', True, (255, 255, 255), (20, 160, 210))
        timRect = tim.get_rect()
        timRect.centerx = screen.get_rect().centerx
        timRect.centery = screen.get_rect().centery + 50
        screen.blit(tim, timRect)
        pygame.display.flip()
        i -= 1
        pygame.time.wait(1000)

def show_winner(winner):
    global board  # we are resetting the global board

    if winner == 'draw':
        show_message("DRAW")
    else:
        show_message(winner + " WINS")
    pygame.display.flip()
    show_countdown(pause)
    board = init_board()


def mouse_click(pos):
    global selected, move_limit
    if (turn != 'black' and white.type != 'cpu') or (turn != 'white' and black.type != 'cpu'):
        column = int(pos[0] / (window_size[0] / board_size))
        row = int(pos[1] / (window_size[1] / board_size))

        if board[row][column] != 0 and board[row][column].color == turn:
            selected = row, column
        else:
            moves = avail_moves(board, turn)
            for i in range(len(moves)):
                if selected[0] == moves[i][0] and selected[1] == moves[i][1]:
                    if row == moves[i][2] and column == moves[i][3]:
                        make_move(selected, (row, column), board)
                        move_limit[1] += 1
                        end_turn()
'''START'''
pygame.init()
board = game_init('hard')
ply_check()

screen = pygame.display.set_mode(window_size)
pygame.display.set_caption(title)
clock = pygame.time.Clock()

background = pygame.image.load(background_image_filename).convert()
font = pygame.font.Font('freesansbold.ttf', 11)
font_big = pygame.font.Font('freesansbold.ttf', 13)

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            exit()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == left:
            mouse_click(event.pos)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F1:
                board = game_init('easy')
            if event.key == pygame.K_F2:
                board = game_init('hard')

    screen.blit(background, (0, 0))

    if (turn != 'black' and white.type == 'human') or (turn != 'white' and black.type == 'human'):
        show_message('YOUR TURN')
    else:
        show_message('CPU THINKING...')

    for m in range(8):
        for n in range(8):
            if board[m][n] != 0:
                draw_piece(m + 1, n + 1, board[m][n].color, board[m][n].king)

    if start == True:
        show_message('Welcome to ' + title)
        show_countdown(pause)
        start = False

    end = end_game(board)
    if end[1] == 0:
        show_winner("black")
    elif end[0] == 0:
        show_winner("white")

    elif move_limit[0] == move_limit[1]:
        show_winner("draw")

    else:
        pygame.display.flip()

    if turn != 'black' and white.type == 'cpu':
        cpu_play(white)
    elif turn != 'white' and black.type == 'cpu':
        cpu_play(black)

    clock.tick(fps)
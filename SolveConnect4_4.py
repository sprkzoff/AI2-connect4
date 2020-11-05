from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from copy import deepcopy
import math

import threading
import time

################## setup ##################

# minimax
max_depth = 9

#selenium
driver_path = r'C:\\Program Files (x86)\\Common Files\\selenium\\msedgedriver.exe'
driver = webdriver.Edge(executable_path=driver_path)
driver.get("http://connect4.ist.tugraz.at:8080/")

# memoization
f = open('connect4_mem.txt','r')
mem = {}
for line in f :
    print(line.strip(),end='\n')
    k,v = line.strip().split()
    mem[k]=int(v)
f.close()
f = open('connect4_mem.txt','a')

###########################################

# activate AI(b)
elem = driver.find_element_by_name("optionsaib")
elem.click()

# board to state
def board2state(board) :
    s = ''
    for row in board :
        s+= ''.join(row)
    return s

# show board
def showBoard(board) :
    print("\n============ Board ============")
    for row in board :
        for column in row :
            print(column,end=" ")
        print("")

# get data from website
def getBoard() :
    boardArray = []
    board = driver.find_element_by_id("board")
    all_tr = board.find_elements_by_tag_name("tr")
    c=0
    for tr in all_tr :
        all_td = tr.find_elements_by_tag_name("td")
        row=[]
        for td in all_td :
            if str(td.get_attribute("class")) == "" : #empty
                row.append('e')
            else :
                row.append(str(td.get_attribute("class")).strip("chip-"))
            #print(str(c+1)+" "+td.text+" "+str(td.get_attribute("class")))
            c+=1
        boardArray.append(row)
    #showBoard(boardArray)
    return boardArray

# generate all posible move
def genMove(board,chip) :
    all_generated_move = []
    for col in range(0,7) :
        new_board = deepcopy(board)
        # check top of board if can insert
        if new_board[0][col] == 'e' :
            row = 0
            while row+1 < 6 and new_board[row+1][col] == 'e' :
                row+=1
            new_board[row][col] = chip
            all_generated_move.append([col,new_board])
    # show all
    # for i in range(len(all_generated_move)) :
    #     showBoard(all_generated_move[i][1])
    return all_generated_move

########## Score ##########


def count_consecutive_chips_direction(col_idx: int, row_idx: int, filled_state: list, chip: str, direction: int) -> int:
    '''
    direction
    0 -> x
    1 -> y
    2 -> up right
    3 -> down right
    '''
    x_score = 0
    y_score = 0
    diag_score_up_right = 0
    diag_score_down_right = 0

    if direction == 0:
        for d_col in range(MAX_CONSECUTIVE):
            if not out_of_bound_x(col_idx + d_col) and filled_state[col_idx + d_col][row_idx] == chip:
                x_score += 1
            else:
                break
        return x_score
    elif direction == 1:
        for d_row in range(MAX_CONSECUTIVE):
            if not out_of_bound_y(row_idx + d_row) and filled_state[col_idx][row_idx + d_row] == chip:
                y_score += 1
            else:
                break
        return y_score
    elif direction == 2:
        for d_col_row in range(MAX_CONSECUTIVE):
            if not out_of_bound_x(col_idx + d_col_row) and not out_of_bound_y(row_idx + d_col_row) and filled_state[col_idx + d_col_row][row_idx + d_col_row] == chip:
                diag_score_up_right += 1
            else:
                break
        return diag_score_up_right
    else:
        for d_col_row in range(MAX_CONSECUTIVE):
            if not out_of_bound_x(col_idx + d_col_row) and not out_of_bound_y(row_idx - d_col_row) and filled_state[col_idx + d_col_row][row_idx - d_col_row] == chip:
                diag_score_down_right += 1
            else:
                break
        return diag_score_down_right

# get score of the board
def getScore(board,chip) :
    score = 0
    # horizontal
    for row in range(0,6) :
        for col in range(0,7) :
            for k in range(0,4):
                if col+k < 7 and board[row][col + k] == chip :
                    score += 1
                else:
                    break
    # vertical
    for col in range(0,7) :
        for row in range(0,6) :
            for k in range(0,4):
                if row+k < 6 and board[row+k][col] == chip :
                    score += 1
                else:
                    break
    # diagonal
    for row in range(0,6) :
        for col in range(0,7) :
            for k in range(0,4) :
                if row+k < 6 and col+k < 7 and board[row+k][col+k] == chip :
                    score+=1
                else :
                    break
    # reverse diagonal
    for row in range(0,6) :
        for col in range(0,7) :
            for i in range(0,4) :
                if  0 <= row-k and col+k < 7 and board[row-k][col+k] == chip :
                    score+=1
                else :
                    break
    return score

# push chip in col (with selenium)
def push(col,board):
    if board[0][col] != 'e':
        return False
    ele_board = driver.find_element_by_id("board")
    all_tr = ele_board.find_elements_by_tag_name("tr")
    for tr in all_tr :
        all_td = tr.find_elements_by_tag_name("td")
        all_td[col].click()
        break
    return True    

# minimax function
def minimax(board,depth,alpha,beta,chip) :
    if depth == 0 or sum([row.count('e') for row in board]) == 0 :
        return getScore(board,'a')-getScore(board,'b'),-1
    if chip == 'a' :
        max_score = -math.inf
        next_col = -1
        allNextMove = genMove(board,chip)
        for col,next_board in allNextMove :
            score,_ = minimax(next_board,depth-1,alpha,beta,'b')
            # maximum player
            if max_score < score :
                max_score = max(max_score,score)
                next_col = col
            alpha = max(alpha,score)
            if beta <= alpha :
                break
        return max_score,next_col
    else :
        min_score = math.inf
        next_col = -1
        allNextMove = genMove(board,chip)
        for col,next_board in allNextMove :
            score,_ = minimax(next_board,depth-1,alpha,beta,'a')
            # minimum player
            if min_score > score :
                next_col = col
                min_score = min(min_score,score)
            beta = min(beta,score)
            if beta <= alpha :
                break
        return min_score,next_col


########## main ##########

# init move
oldBoard = getBoard()
is_a_turn = False
push(3,oldBoard)
t=1
while sum([row.count('e') for row in getBoard()]) > 0 :
    if getScore(getBoard(),'a') == 4 :
        print('WIN')
        break
    if getScore(getBoard(),'b') == 4 :
        print('LOSE')
        break
    if is_a_turn:
        print('\nROUND '+str(t))
        t+=1
        tempBoard = getBoard()
        showBoard(tempBoard)
        state = board2state(tempBoard)
        if state in mem.keys() :
            push(mem[state],tempBoard)
        else :
            val,nextMove = minimax(tempBoard,max_depth,-math.inf,math.inf,'a')
            push(nextMove,tempBoard)
            f.write(state+" "+str(nextMove)+"\n")
            mem[state]=nextMove
        is_a_turn = False
    else:
        while getBoard() == oldBoard :
            time.sleep(2)
            oldBoard = getBoard()
        is_a_turn = True

f.close()
# driver.quit()
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from copy import deepcopy
import math

import threading
import time

################## setup ##################

# minimax
max_depth = 9

# selenium
print("Load Driver")
# edge

# driver_path = 'C:\\Program Files (x86)\\Common Files\\selenium\\msedgedriver.exe'
# driver = webdriver.Edge(executable_path=driver_path)

#chrome
from webdriver_manager.chrome import ChromeDriverManager
driver = webdriver.Chrome(ChromeDriverManager().install())

driver.get("http://connect4.ist.tugraz.at:8080/")
driver.refresh()
insert_channel = driver.find_element_by_id("board")
insert_channel = insert_channel.find_elements_by_tag_name("tr")[0]
print("Success!")

# memoization
f = open('connect4_mem.txt','r')
mem = {}
for line in f :
    #print(line.strip(),end='\n')
    k,v = line.strip().split()
    mem[k]=int(v)
f.close()
print("Success!")
f = open('connect4_mem.txt','a')

###########################################

# activate AI(b)
elem = driver.find_element_by_name("optionsaib")
elem.click()
print("Activate AI Perfect...")

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

# get score of the board
def getScore(board,chip) :
    score = 0
    # horizontal
    for row in range(0,6) :
        c=0
        for col in range(0,7) :
            if board[row][col] == chip :
                c+=1
            else :
                c=0
                score = max(score,c)
            if c == 4 :
                return 4
    # vertical
    for col in range(0,7) :
        r=0
        for row in range(0,6) :
            if board[row][col] == chip :
                r+=1
            else :
                r=0
                score = max(score,r)
            if r == 4 :
                return 4
    # diagonal
    for row in range(0,3) :
        for col in range(0,4) :
            d=0
            for i in range(0,4) :
                if board[row+i][col+i] == chip :
                    d+=1
                else :
                    d=0
                    score = max(score,d)
                if d == 4 :
                    return 4
    # reverse diagonal
    for row in range(3,6) :
        for col in range(0,4) :
            rh=0
            for i in range(0,4) :
                if board[row-i][col+i] == chip :
                    rh+=1
                else :
                    rh=0
                    score = max(score,rh)
                if rh == 4 :
                    return 4
    return score

# push chip in col (with selenium)
def push(col,board):
    if board[0][col] != 'e':
        return False
    all_td = insert_channel.find_elements_by_tag_name("td")
    all_td[col].click()
    return True    

# minimax function
def minimax(board,depth,alpha,beta,chip) :
    if getScore(board,chip) == 4 :
        return 4,-1
    if depth == 0 or sum([row.count('e') for row in board]) == 0 :
        return getScore(board,chip),-1
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
            score = -1*score
            if min_score > score :
                next_col = col
                min_score = min(min_score,score)
            beta = min(beta,score)
            if beta <= alpha :
                break
        return min_score,next_col

# thread
def count_down_thread():
    n=20
    print('\n'+str(n)+'..',end='')
    for i in range(n,-1,-1):
      time.sleep(1)
      if terminate_flag:
        break
      print(str(i)+'..',end='')
    print()

########## main ##########

print("Enter main")
# init move
oldBoard = getBoard()
is_a_turn = False
push(3,oldBoard)
t=1
print("Loop Game...")
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
            ct=threading.Thread(target=count_down_thread)
            terminate_flag=False
            ct.start()
            val,nextMove = minimax(tempBoard,max_depth,-math.inf,math.inf,'a')
            terminate_flag=True
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
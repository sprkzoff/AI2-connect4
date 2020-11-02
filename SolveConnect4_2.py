from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from copy import deepcopy

import threading
import time

################## setup ##################

# minimax
max_depth = 10

#selenium
driver_path = r'C:\\Program Files (x86)\\Common Files\\selenium\\msedgedriver.exe'
driver = webdriver.Edge(executable_path=driver_path)
driver.get("http://connect4.ist.tugraz.at:8080/")

###########################################

# activate AI(b)
elem = driver.find_element_by_name("optionsaib")
elem.click()

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
    showBoard(boardArray)
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
    for i in range(len(all_generated_move)) :
        showBoard(all_generated_move[i][1])
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
            if c == 4 :
                score+=1
    # vertical
    for col in range(0,7) :
        r=0
        for row in range(0,6) :
            if board[row][col] == chip :
                r+=1
            else :
                r=0
            if c == 4 :
                score+=1
    # diagonal
    for row in range(0,3) :
        for col in range(0,4) :
            h=0
            for i in range(0,4) :
                if board[row+i][col+i] == chip :
                    h+=1
                else :
                    h=0
                if h == 4 :
                    score+=1
    # reverse diagonal
    for row in range(3,6) :
        for col in range(0,4) :
            rh=0
            for i in range(0,4) :
                if board[row-i][col+i] == chip :
                    rh+=1
                else :
                    rh=0
                if rh == 4 :
                    score+=1
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


tempBoard = getBoard()
genMove(tempBoard,'a')
print(getScore(tempBoard,'a'))
driver.close()
driver.quit()
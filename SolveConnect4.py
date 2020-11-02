from selenium import webdriver
from selenium.webdriver.common.keys import Keys

import threading
import time

################## setup ##################

# minimax
debug = False

#selenium
driver_path = r'C:\\Program Files (x86)\\Common Files\\selenium\\msedgedriver.exe'
driver = webdriver.Edge(executable_path=driver_path)
driver.get("http://connect4.ist.tugraz.at:8080/")

###########################################

# activate AI(b)
elem = driver.find_element_by_name("optionsaib")
elem.click()

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
    print("\n============ Board ============")
    for row in boardArray :
        for column in row :
            print(column,end=" ")
        print("")
    return boardArray

# push chip in the board
def push(col,chip,state):
    if len(state[col]) >= 6:
        return False
    state[col].append(chip)
    board = driver.find_element_by_id("board")
    all_tr = board.find_elements_by_tag_name("tr")
    c=0
    for tr in all_tr :
        all_td = tr.find_elements_by_tag_name("td")
        all_td[col].click()
        break
    return True

def check_window(state,chip,i,j):
    state = [s+['o']*(7-len(s)) for s in state]
    # print(state)
    max_count = 0
    count = 0
    if i <= 3:
        count = 0
        for col in range(4):
            if state[i+col][j] == chip:
                count += 1
            elif state[i+col][j] != 'o':
                count = 0
                break
        if count == 4:
            return (i,j,4)
    if count > max_count:
        max_count = count
    if j >= 3:
        count = 0
        for row in range(4):
            if state[i][j-row] == chip:
                count += 1
            elif state[i][j-row] != 'o':
                count = 0
                break
        if count == 4:
            return (i,j,4)
    if count > max_count:
        max_count = count

    if i <= 3 and j >= 3:
        count = 0
        for k in range(4):
            if state[i+k][j-k] == chip:
                count += 1
            elif state[i+k][j-k] != 'o':
                count = 0
                break
        if count == 4:
            return (i,j,4)
    if count > max_count:
        max_count = count
    
    if i <= 3 and j <= 2:
        count = 0
        for k in range(4):
            if state[i+k][j+k] == chip:
                count += 1
            elif state[i+k][j+k] != 'o':
                count = 0
                break
        if count == 4:
            return (i,j,4)
    if count > max_count:
        max_count = count
        
    # if max_count == 3 and (j == 0 or state[i][j-1] != 'o') and state[i][j] == 'o':
    #    return (i,j,3)
    # if max_count == 3 and state[i][j-1] == 'o':
    #    return (i,j,3)
    return (i,j,max_count)

def utility(state,chip):
    ret=is_win(state,chip)
    if debug: show_state(state)
    if debug: print(ret)
    if chip == 'a':
        return ret[2]
    return -ret[2]
    

def is_win(state,chip):
    max = -1
    for i in range(7):
        for j in range(6):
            ret=check_window(state,chip,i,j)
            if ret[2] > max:
                max = ret[2]
                ans = ret
    return ans

def show_state(state):
    print()
    state = [s+['o']*(7-len(s)) for s in state]
    for r in range(5,-1,-1):
        str_out = ''
        for c in range(7):
            str_out += state[c][r]
        print(str_out)
    print('1234567')
    # print(state)

max_depth = 12

def min_value_function(state,a,b,level):
    # just pushed black
    if is_win(state,'a')[2] == 4:
        return 4
    if level >= max_depth:
        if debug: print('Cutoff',state)
        ret_u = utility(state,'a')
        if debug: print('Utility',ret)
        return ret_u
    v=100
    for i in range(7):
        if len(state[i]) == 6:
            continue
        new_state = tuple([list(new_col) for new_col in state])
        push(i,'b',new_state)
        v = min(v,max_value_function(new_state,a,b,level+1))
        if v <= a:
            return v
        if b == 10:
            b = v
        else:
            b = min(b,v)
    return v

def max_value_function(state,a,b,level):
    # just pushed white
    if is_win(state,'b')[2] == 4:
        return -4
    v=-100
    # if black can win
    for i in range(7):
        if len(state[i]) == 6:
            continue
        new_state = tuple([list(new_col) for new_col in state])
        push(i,'a',new_state)
        if is_win(new_state,'a')[2] == 4:
            return 4
    for i in range(7):
        if len(state[i]) == 6:
            continue
        new_state = tuple([list(new_col) for new_col in state])
        push(i,'a',new_state)
        v = max(v,min_value_function(new_state,a,b,level+1))
        if v >= b:
            return v
        if a == -10:
            a = v
        else:
            a = max(a,v)
    return v

def alpha_beta_decision(state):
    global max_depth
    s_res = sum([len(c) for c in list(state)])
    if s_res == 1:
        ind = 0
        for c in list(state):
            if len(c) == 1:
                if ind == 0:
                    return 1
                else:
                    return ind-1
            ind += 1
    elif s_res == 0:
        return 3
    if s_res < 5:
        max_depth = 4
    elif s_res < 12:
        max_depth = 6
    elif s_res < 24:
        max_depth = 8
    else:
        max_depth = 10
    max_value = -100
    a,b=-10,10
    min_score=[]
    count_win = 0
    count_lose = 0
    for i in range(7):
        if len(state[i]) == 6:
            continue
        new_state = [[list(new_col) for new_col in state]]
        push(i,'a',new_state)
        ret=min_value_function(new_state,a,b,0)
        min_score.append(ret)
        if debug: print('MiniMax Value',ret)
        if debug: show_state(new_state)
        if ret > max_value:
            max_value=ret
            action = i
        if ret == 4:
            count_win += 1
        elif ret == -4:
            count_lose += 1
    if count_win >= 1:
        print('From my calculation, I will win')
    elif count_lose == 7:
        print('From my calculation, you will win')
    print(min_score,action)
    return action

def count_down_thread():
    n=10
    print('\n'+str(n)+'..',end='')
    for i in range(n,-1,-1):
      time.sleep(1)
      if terminate_flag:
        break
      print(str(i)+'..',end='')
    print()

# main
oldBoard = getBoard()
is_a_turn = False
state = [[],[],[],[],[],[],[]]
push(3,'a',state)
#state=[['b', 'b', 'b','a'], [], ['a', 'a','b'], ['b', 'a','b'], ['a','a'], ['a'], []]
show_state(state)
t=1
while sum([len(c) for c in list(state)]) != 42:

    if is_a_turn:
        print('========== time '+str(t)+' ==========')
        t+=1
        tempBoard = getBoard()
        temp_state = [[],[],[],[],[],[],[]]
        # make state from board
        for i in range(len(tempBoard)) :
            for j in range(len(tempBoard[i])) :
                if tempBoard[i][j] != 'e' :
                    temp_state[j].append(tempBoard[i][j])
        print(temp_state)
        # ct=threading.Thread(target=count_down_thread)
        # terminate_flag=False
        # ct.start()
        c = alpha_beta_decision(temp_state)
        print(c)
        terminate_flag=True
        push(c,'a',temp_state)
        print(state)
        if is_win(temp_state,'a')[2] == 4:
            print('I win!!!')
            break
        is_a_turn = False
    else:
        while getBoard() == oldBoard :
            time.sleep(3)
            oldBoard = getBoard()
        is_a_turn = True

getBoard()
driver.quit()
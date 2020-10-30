from selenium import webdriver
from selenium.webdriver.common.keys import Keys

# setup
driver_path = r'C:\\Program Files (x86)\\Common Files\\selenium\\msedgedriver.exe'
driver = webdriver.Edge(executable_path=driver_path)
driver.get("http://connect4.ist.tugraz.at:8080/")

# activate AI(b)
elem = driver.find_element_by_name("optionsaib")
elem.click()

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

getBoard()
driver.quit()
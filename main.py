from pandemic.GameObjects import *
from pandemic.GameGUI import GameGUI, run_gui
from tkinter import *
# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    board = PandemicBoard("./pandemic/data/europe_board.csv")
    print("Loaded board.")
    print(board["essen"].players)
    gui = GameGUI(board)
    run_gui()
    # print("here")
    # board = board
    # GUIWindow = Tk()
    # GUIWindow.geometry("500x500")

    # BoardCanvas = Canvas(GUIWindow, width=500, height=300, bg="black")
    # ControlCanvas = Canvas(GUIWindow, width=500, height=200)
    # BoardCanvas.pack(side=TOP)
    # ControlCanvas.pack(side=BOTTOM)
    # GUIWindow.title("CSCE 686 Final Project - Lynch")
    #
    # board_img = PhotoImage(file="/repos/686_final/pandemic/data/pandemic_board.gif")
    # img_label = Label(image=board_img)
    # img_label.image = board_img
    # img_label.pack()
    # BoardCanvas.create_image(500, 300, anchor=NW, image=board_img)
    # GUIWindow.mainloop()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/

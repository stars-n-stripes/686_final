from tkinter import *
from pandemic.GameObjects import *
from PIL import Image, ImageTk
from pathlib import Path

def run_gui():
    mainloop()


class GameGUI:
    def __init__(self, board: PandemicBoard, width=750, height=750):
        self.board = board
        self.GUIWindow = Tk()
        self.GUIWindow.geometry(str(width) + "x" + str(height))
        img_height = 3 * height // 5
        ctrl_height = 2 * height // 5
        self.BoardCanvas = Canvas(self.GUIWindow, width=width, height=img_height, bg="black")
        self.ControlCanvas = Canvas(self.GUIWindow, width=width, height=ctrl_height, bg="grey")
        self.BoardCanvas.pack(side=TOP)
        self.ControlCanvas.pack(side=BOTTOM)
        self.GUIWindow.title("CSCE 686 Final Project - Lynch")

        # OS mumbo-jumbo opens the picture file relative to this file (inside the module)
        image_file_path = Path(__file__).parent / "./data/pandemic_board.jpg"
        board_img = Image.open(image_file_path)
        # resize_image = board_img.resize((self.BoardCanvas.winfo_width(), self.BoardCanvas.winfo_height()))
        # print((self.BoardCanvas.winfo_width(), self.BoardCanvas.winfo_height()))
        resize_image = board_img.resize((width, img_height))
        self.tk_image = ImageTk.PhotoImage(resize_image)

        # self.img_label = Label(image=board_img)
        # self.img_label.image = board_img
        # self.img_label.pack(side=TOP)
        self.BoardCanvas.create_image((0,0), anchor="nw", image=self.tk_image)

        # To be populated when we call draw_board
        self.tiles = []

        # Load up the coordinate ratios
        coord_file_path = Path(__file__).parent / "./data/board_coords.csv"

    def create_circle_on_board(self, x, y, r):  # center coordinates, radius
        x0 = x - r
        y0 = y - r
        x1 = x + r
        y1 = y + r
        return self.BoardCanvas.create_oval(x0, y0, x1, y1)

    def draw_board(self):
        if self.tiles:
            for t in self.tiles:
                t.pack_forget()
        # Create the board
        for space in self.board.spaces():
            # x, y =
            pass
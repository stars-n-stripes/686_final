from tkinter import *
from pandemic.GameObjects import *
from PIL import Image, ImageTk
from pathlib import Path
from csv import DictReader

JPG_RAW_WIDTH = 1500
JPG_RAW_HEIGHT = 900


def run_gui():
    mainloop()


class GameGUI:
    CIRCLE_RADIUS = 15
    def __init__(self, board: PandemicBoard, width=750, height=750):
        self.board = board
        self.GUIWindow = Tk()
        self.GUIWindow.geometry(str(width) + "x" + str(height))
        img_height = 3 * height // 5
        ctrl_height = 2 * height // 5
        self.BoardCanvas = Canvas(self.GUIWindow, width=width, height=img_height, bg="black")
        # self.ControlCanvas = Canvas(self.GUIWindow, width=width, height=ctrl_height, bg="grey")
        self.BoardCanvas.pack(side=TOP)
        # self.ControlCanvas.pack(side=BOTTOM)
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
        self._coords = {}
        coord_file_path = Path(__file__).parent / "./data/city_gui_coords.csv"
        with open(coord_file_path, "r") as csvfile:
            dr = DictReader(csvfile)
            for row in dr:
                # Each row in the CSV contains percentage-based offsets from the raw height/width origins of the picture
                self._coords[row["city_name"].lower()] = (
                    float(row["x"]) * width,
                    float(row["y"]) * img_height
                )

        # Add control buttons
        self.test_button = Button(self.GUIWindow, text="Draw Board", command = self.draw_board, bg="grey", activebackground="red")
        self.test_button.pack(side=BOTTOM, expand=True)


    def create_circle_on_board(self, x, y, color, r):  # center coordinates, radius
        x0 = x - r
        y0 = y - r
        x1 = x + r
        y1 = y + r
        return self.BoardCanvas.create_oval(x0, y0, x1, y1, fill=color)

    def get_coords(self, city_name):
        """
        Return the x/y coordinates of a city relative to the UL corner of the picture
        :param city_name:
        :return: A tuple of (x, y) coordinates
        """
        # print(self._coords.keys())
        if city_name.lower() not in self._coords.keys():
            raise KeyError("get_coords: {} not in GUI coordinate dictionary".format(city_name))

        return self._coords[city_name]

    def draw_board(self):
        print(self._coords)
        if self.tiles:
            for t in self.tiles:
                t.pack_forget()
        self.tiles.clear()
        # Create the board
        for space in self.board.spaces():
            x, y = self.get_coords(space.name)
            circle = self.create_circle_on_board(x, y, space.color, GameGUI.CIRCLE_RADIUS)
            self.tiles.append(circle)


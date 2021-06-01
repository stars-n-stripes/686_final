from tkinter import *
from pandemic.GameObjects import *
from PIL import Image, ImageTk
from pathlib import Path
from csv import DictReader
import pandemic
import os

JPG_RAW_WIDTH = 1500
JPG_RAW_HEIGHT = 900


def run_gui():
    mainloop()


class GameGUI:
    CIRCLE_RADIUS = 15

    def __init__(self, board: PandemicBoard, width=750, height=750):

        self.board = board
        self.GUIWindow = Tk()
        self.board_filepath = StringVar(self.GUIWindow)

        # Places to store TSP and MIS results, respectively
        self.path = []
        self.mis = set()

        self.GUIWindow.geometry(str(width) + "x" + str(height))
        img_height = 3 * height // 5
        ctrl_height = 2 * height // 5
        self.BoardCanvas = Canvas(self.GUIWindow, width=width, height=img_height, bg="black")
        # self.ControlCanvas = Canvas(self.GUIWindow, width=width, height=ctrl_height, bg="grey")
        self.BoardCanvas.grid(column=0, row=0, rowspan=5)
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
        self.BoardCanvas.create_image((0, 0), anchor="nw", image=self.tk_image)

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
        self.test_button = Button(self.GUIWindow, text="Draw Board", command=self.draw_board, bg="grey",
                                  activebackground="red")
        self.test_button.grid(column=0, row=5)

        # Add board options in a manner similar to project_genetic's cli
        datadir = os.listdir(pandemic.DATA_DIR)
        datafiles = list(filter(lambda x: "board" in x and ".csv" in x, datadir))

        df_label_names = [df.replace("_", " ").replace(".csv", "").capitalize() for df in datafiles]
        self.label_to_filepath_dict = {label: fp for label, fp in zip(df_label_names, datafiles)}
        print(df_label_names)
        self.board_filepath.set(df_label_names[0])
        self.board_choice_dropdown = OptionMenu(self.GUIWindow, self.board_filepath, df_label_names[0], *df_label_names[1:],
                                                command=self.filepath_changed)
        self.board_choice_dropdown.grid(column=0, row=6)

        # Add buttons to load a board
        self.load_board_button = Button(self.GUIWindow, text="Load Board from CSV", command=self.load_board_from_csv,
                                        bg="grey", activebackground="red")
        self.load_board_button.grid(column=1, row=6)

        #Initialize the private _board_filepath variable
        self._board_filepath = ""
        self.filepath_changed()

        # Add Parameter fields for genetic algorithm
        self._num_pop_str = StringVar(self.GUIWindow)
        self._num_iterations_str = StringVar(self.GUIWindow)
        self._mutation_rate_str = StringVar(self.GUIWindow)
        self._elite_ratio_str = StringVar(self.GUIWindow)
        self._stochastic_params = {
            "num_pop": 100,
            "num_iterations": 500,
            "mutation_rate": 0.002,
            "elite_ratio": 0.1
        }

        self.ng_label = Label(self.GUIWindow, text="Population Size: ", bg="grey")
        self.ng_label.grid(column=0, row=7)
        self.num_generations_input = Entry(self.GUIWindow, text="Population Size: ", bg="grey",
                                           textvariable=self._num_pop_str )
        self.num_generations_input.grid(column=1, row=7)
        self.mutation_rate_input = Entry(self.GUIWindow, text="Mutation Rate: ", bg="grey",
                                           textvariable=self._mutation_rate_str)
        self.mutation_rate_input.grid(column=1, row=8)
        self.elite_ratio_input = Entry(self.GUIWindow, text="Elite Ratio: ", bg="grey",
                                           textvariable=self._elite_ratio_str)
        self.elite_ratio_input.grid(column=1, row=9)
        self.num_iterations_input = Entry(self.GUIWindow, text="Number of Generations: ", bg="grey",
                                           textvariable=self._num_iterations_str)
        self.num_iterations_input.grid(column=1, row=10)
        # Do an initial draw
        self.draw_board()

    def update_stochastic_vars(self):
        try:
            self._stochastic_params["num_pop"] = int(self._num_pop_str.get())
        except ValueError:
            pass
        try:
            self._stochastic_params["num_iterations"] = int(self._num_iterations_str.get())
        except ValueError:
            pass
        try:
            self._stochastic_params["mutation_rate"] = int(self._mutation_rate_str.get())
        except ValueError:
            pass
        try:
            self._stochastic_params["elite_ratio"] = int(self._elite_ratio_str.get())
        except ValueError:
            pass



    def filepath_changed(self, *args):
        # Converts the label name we get out of the GUI to the filepath we need to actually use
        try:
            self._board_filepath = self.label_to_filepath_dict[self.board_filepath.get()]
        except KeyError:
            pass

    def load_board_from_csv(self):
        try:
            self.board = PandemicBoard(pandemic.DATA_DIR / self._board_filepath)
            print("Loaded ", pandemic.DATA_DIR / self._board_filepath)
            self.draw_board()
            print("Board drawn on GUI.")
        except Exception as e:
            print( e.__str__())

    def create_circle_on_board(self, x, y, color, r):  # center coordinates, radius
        x0 = x - r
        y0 = y - r
        x1 = x + r
        y1 = y + r
        return self.BoardCanvas.create_oval(x0, y0, x1, y1, fill=color)

    def create_text_on_board(self, x, y, text, color):  # center coordinates, text

        return self.BoardCanvas.create_text(x, y, text=text, fill=color)

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
        # print(self._coords) # debug
        if self.tiles:
            for t in self.tiles:
                self.BoardCanvas.delete(t)
        self.tiles.clear()
        # Create the board
        for space in self.board.spaces():
            x, y = self.get_coords(space.name)

            # TODO: Flag whether or not this has a research station
            # If this is in the MIS, label it green
            if space.name in self.mis:
                color = "green"
            else:
                color = space.color

            circle = self.create_circle_on_board(x, y, color, GameGUI.CIRCLE_RADIUS)
            self.tiles.append(circle)

        # If we have an active path, draw that  as well
        if self.path:
            # To hold each city's eventual text coordinates
            path_str_dict = dict()
            for i, city in enumerate(self.path):
                if i == 0:
                    text = "0"
                else:
                    text = str(i)
                space = self.board[city]
                if space.name in path_str_dict.keys():
                    path_str_dict[space.name] += ",{}".format(text)
                else:
                    path_str_dict[space.name] = text
            # Now, draw the text
            for city, string in path_str_dict.items():
                x, y = self.get_coords(city)
                self.create_text_on_board(x, y, path_str_dict[city], "white")




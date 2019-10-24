# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from matplotlib import pyplot as plt
from colorhash import ColorHash
from io import BytesIO

import telegram
from telegram.error import TelegramError

with open("api_key.txt", 'r') as f:
    TOKEN = f.read().rstrip()

bot = telegram.Bot(token=TOKEN)

# I think it might be more elegant to return non-null and return strings with error text if need be. Sometimes,
# however, I'll be returning non-errors, so I might want to implement a tuple system: (err_code, data)
# Let 0 be success and 1 be some error.

# https://www.science-emergence.com/Articles/How-to-put-the-origin-in-the-center-of-the-figure-with-matplotlib-/
# https://pythonspot.com/matplotlib-scatterplot/
# https://stackoverflow.com/questions/51113062/how-to-receive-images-from-telegram-bot

class Plot:
    def __init__(self, name, xaxisleft, xaxisright, yaxisbottom, yaxistop, minx, maxx, miny, maxy, createdby):
        self.__name = name
        self.__xaxisleft = xaxisleft
        self.__xaxisright = xaxisright
        self.__yaxisbottom = yaxisbottom
        self.__yaxistop = yaxistop
        self.__minx = minx
        self.__maxx = maxx
        self.__miny = miny
        self.__maxy = maxy
        self.__points = []
        self.__createdby = createdby

    def __check_bounds(self, x, y):
        if (self.__minx is not None and x < self.__minx) or (self.__maxx is not None and x > self.__maxx) or \
                (self.__miny is not None and x < self.__miny) or (self.__maxy is not None and x > self.__maxy):
            return False
        return True

    def plot_point(self, label, x, y):
        if not self.__check_bounds(x, y):
            return 1, "Error: Plot point cannot be out of bounds: " \
                      "x : [" + str(self.__minx if self.__minx is not None else "_") + ", " + \
                   str(self.__maxx if self.__maxx is not None else "_") + "] " + \
                   "y : [" + str(self.__miny if self.__miny is not None else "_") + ", " + \
                   str(self.__maxy if self.__maxy is not None else "_") + "]"

        for i in range(len(self.__points)):
            if self.__points[i][0] == label:
                self.__points[i] = (label, x, y)
                return 0, ""

        self.__points.append((label if label is not None else "", x, y))

        return 0, ""

    def remove_point(self, label):
        if label not in [t[0] for t in self.__points]:
            return 1, "Error: You haven't plotted yourself in this plot."
        self.__points.remove(next(p for p in self.__points if p[0] == label))

        return 0, ""

    def generate_plot(self):
        X = [p[1] for p in self.__points]
        Y = [p[2] for p in self.__points]
        labels = [p[0] for p in self.__points]
        colors = [(color_hash[0] / 255, color_hash[1] / 255, color_hash[2] / 255)
                  for color_hash in [ColorHash(label).rgb for label in labels]]

        fig = plt.figure()
        plt.scatter(X, Y, c=colors)
        plt.grid(True)
        plt.axhline(y=0, color='k')
        plt.axvline(x=0, color='k')

        for i in range(len(X)):
            plt.annotate(labels[i], (X[i], Y[i]))

        if self.__xaxisleft is not None and self.__xaxisright is not None:
            plt.xlabel("<-- " + str(self.__xaxisright) + " || " + str(self.__xaxisleft) + " -->")
        elif self.__xaxisleft is not None:
            plt.xlabel(str(self.__xaxisleft))
        elif self.__xaxisright is not None:
            plt.xlabel(str(self.__xaxisright))

        if self.__yaxistop is not None and self.__yaxisbottom is not None:
            plt.ylabel("<-- " + str(self.__yaxistop) + " || " + str(self.__yaxisbottom) + " -->")
        elif self.__yaxistop is not None:
            plt.xlabel(str(self.__yaxistop))
        elif self.__yaxisbottom is not None:
            plt.xlabel(str(self.__yaxisbottom))

        if self.__name is not None:
            plt.title(str(self.__name))

        buffer = BytesIO()
        fig.savefig(buffer, format="png")
        buffer.seek(0)

        # bot.send_photo(chat_id=chat_id, photo=buffer)
        # This returns the image itself that can then be sent.
        return 0, buffer

    def get_name(self):
        return self.__name

    def get_xaxisleft(self):
        return self.__xaxisleft

    def get_xaxisright(self):
        return self.__xaxisright

    def get_yaxisbottom(self):
        return self.__yaxisbottom

    def get_yaxistop(self):
        return self.__yaxistop

    def get_minx(self):
        return self.__minx

    def get_maxx(self):
        return self.__maxx

    def get_miny(self):
        return self.__miny

    def get_maxy(self):
        return self.__maxy
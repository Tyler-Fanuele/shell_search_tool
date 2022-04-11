#!/usr/bin/env python3
import sys
import os

G = 32
R = 31
B = 34
# format
BLD = 1
UND = 4
REG = 0

def add_color(wString, color, form):
    temp1 = "\033[" + str(form) + ";" + str(color) + "m" + wString + "\033[0m" # add color to the given string
    return temp1

path = os.getcwd()

file = open("/etc/paths", "a")

print(add_color("=== Path Adding Tool\n=== Copyright 2022, Tyler Fanuele\n===", G, REG))

print(add_color("=== Adding " + path + " to the path...", G, REG))

file.write(path + "\n")

#!/usr/bin/env python3
import os
import re
import sys

def main():
    path = os.getcwd()
    files = [f for f in os.listdir(".") if os.path.isfile(f)]
    needed = []
    for f in files:
        if re.search(r"\w(\.cpp)", f) or re.search(r"\w*(\.h)", f) or re.search(r"Makefile", f):
            print(f)
            os.system("enscript -C --margins=50:50:50:50 " + f + " -o " + f + ".ps &&  ps2pdf " + f + ".ps")
            needed.append(f + ".ps")
            needed.append(f + ".pdf")
    print("Making pdf directory")
    os.system("mkdir pdf")
    print("copying and deleting items")
    for f in needed:
        os.system("cp " + f + " pdf/" + f)
        os.system("rm " + f)
    
    
            
main()
#!/usr/bin/env -S python3 -i

from matrix import *
from matrix.__version__ import version

art = r"""
              __      _     
  __ _  ___ _/ /_____(_)_ __
 /  ' \/ _ `/ __/ __/ /\ \ /
/_/_/_/\_,_/\__/_/ /_//_\_\ 

"""
WIDTH = 60

print('\n' + "WELCOME TO".center(WIDTH).rstrip(' '), end='')
print(*(line.center(WIDTH).rstrip(' ') for line in art.splitlines()), sep='\n')
print(f"VERSION {version}\n".center(WIDTH).rstrip(' '))
print("Below is a sample of what a 4x4 matrix looks like:".center(WIDTH).rstrip(' '))
print('\n'.join(line.center(WIDTH).rstrip(' ')
                for line in str(randint_matrix(4, 4, range(0, 10))).split('\n')
               ))
print("Have a nice time testing out the library :)\n".center(WIDTH).rstrip(' '))


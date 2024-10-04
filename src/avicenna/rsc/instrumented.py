import sflkitlib.lib
sflkitlib.lib.add_line_event(0)
from math import cos as rcos
sflkitlib.lib.add_line_event(1)
from math import sin as rsin
sflkitlib.lib.add_line_event(2)
from math import tan as rtan

def sqrt(x):
    sflkitlib.lib.add_line_event(3)
    if x == 0:
        sflkitlib.lib.add_line_event(4)
        return 0
    sflkitlib.lib.add_line_event(5)
    assert x > 0
    sflkitlib.lib.add_line_event(6)
    approx = None
    sflkitlib.lib.add_line_event(7)
    guess = x / 2
    sflkitlib.lib.add_line_event(8)
    while approx != guess:
        sflkitlib.lib.add_line_event(9)
        approx = guess
        sflkitlib.lib.add_line_event(10)
        guess = (approx + x / approx) / 2
    sflkitlib.lib.add_line_event(11)
    return approx

def tan(x):
    sflkitlib.lib.add_line_event(12)
    return rtan(x)

def cos(x):
    sflkitlib.lib.add_line_event(13)
    return rcos(x)

def sin(x):
    sflkitlib.lib.add_line_event(14)
    return rsin(x)

def main(arg):
    sflkitlib.lib.add_line_event(15)
    return eval(arg)
import sflkitlib.lib


def middle(x, y, z):
    sflkitlib.lib.add_line_event('middle.py', 2, 0)
    m = z
    sflkitlib.lib.add_line_event('middle.py', 3, 1)
    if y < z:
        sflkitlib.lib.add_line_event('middle.py', 4, 2)
        if x < y:
            sflkitlib.lib.add_line_event('middle.py', 5, 3)
            m = y
        else:
            sflkitlib.lib.add_line_event('middle.py', 6, 4)
            if x < z:
                sflkitlib.lib.add_line_event('middle.py', 7, 5)
                m = y
    else:
        sflkitlib.lib.add_line_event('middle.py', 9, 6)
        if x > y:
            sflkitlib.lib.add_line_event('middle.py', 10, 7)
            m = y
        else:
            sflkitlib.lib.add_line_event('middle.py', 11, 8)
            if x > z:
                sflkitlib.lib.add_line_event('middle.py', 12, 9)
                m = x
    sflkitlib.lib.add_line_event('middle.py', 13, 10)
    return m

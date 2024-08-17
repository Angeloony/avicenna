import sflkitlib.lib

def middle(x, y, z):
    sflkitlib.lib.add_line_event(0)
    m = z
    sflkitlib.lib.add_line_event(1)
    if y < z:
        sflkitlib.lib.add_line_event(2)
        if x < y:
            sflkitlib.lib.add_line_event(3)
            m = y
        else:
            sflkitlib.lib.add_line_event(4)
            if x < z:
                sflkitlib.lib.add_line_event(5)
                m = y
    else:
        sflkitlib.lib.add_line_event(6)
        if x > y:
            sflkitlib.lib.add_line_event(7)
            m = y
        else:
            sflkitlib.lib.add_line_event(8)
            if x > z:
                sflkitlib.lib.add_line_event(9)
                m = x
    sflkitlib.lib.add_line_event(10)
    return m
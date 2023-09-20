import sflkitlib.lib


def middle(x, y, z):
    m = z
    if y < z:
        sflkitlib.lib.add_branch_event('middle.py', 3, 0, 0, 1)
        if x < y:
            sflkitlib.lib.add_branch_event('middle.py', 4, 2, 2, 3)
            m = y
        else:
            sflkitlib.lib.add_branch_event('middle.py', 4, 3, 3, 2)
            if x < z:
                sflkitlib.lib.add_branch_event('middle.py', 6, 4, 4, 5)
                m = y
            else:
                sflkitlib.lib.add_branch_event('middle.py', 6, 5, 5, 4)
    else:
        sflkitlib.lib.add_branch_event('middle.py', 3, 1, 1, 0)
        if x > y:
            sflkitlib.lib.add_branch_event('middle.py', 9, 6, 6, 7)
            m = y
        else:
            sflkitlib.lib.add_branch_event('middle.py', 9, 7, 7, 6)
            if x > z:
                sflkitlib.lib.add_branch_event('middle.py', 11, 8, 8, 9)
                m = x
            else:
                sflkitlib.lib.add_branch_event('middle.py', 11, 9, 9, 8)
    return m

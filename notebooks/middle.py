def middle(x, y, z):
    m = z
    if y < z:
        if x < y:
            m = y
        elif x < z: #3, 2, 1 x > z, y > z, x < y 2 3 1 
            m = x  
    else:
        if x > y:
            m = y
        elif x > z:
            m = x # line to call
    return m

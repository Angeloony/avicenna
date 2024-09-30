import sflkitlib.lib

def remove_html_markup(s):
    sflkitlib.lib.add_line_event(0)
    tag = False
    sflkitlib.lib.add_line_event(1)
    quote = False
    sflkitlib.lib.add_line_event(2)
    out = ''
    sflkitlib.lib.add_line_event(3)
    for c in s:
        sflkitlib.lib.add_line_event(4)
        if c == '<' and (not quote):
            sflkitlib.lib.add_line_event(5)
            tag = True
        else:
            sflkitlib.lib.add_line_event(6)
            if c == '>' and (not quote):
                sflkitlib.lib.add_line_event(7)
                tag = False
            else:
                sflkitlib.lib.add_line_event(8)
                if c == '"' or (c == "'" and tag):
                    sflkitlib.lib.add_line_event(9)
                    quote = not quote
                else:
                    sflkitlib.lib.add_line_event(10)
                    if not tag:
                        sflkitlib.lib.add_line_event(11)
                        out = out + c
    sflkitlib.lib.add_line_event(12)
    return out
# python

import lx

def message(table, message_id, *args):
    if len(args) != 0:
        args_list = ["{%s}" % arg for arg in args]
        cmd = ("query messageservice msgcompose ? {@%s@@%s@" + " %s" * len(args) + "}") % tuple([table, message_id] + args_list)
    else:
        cmd = ("query messageservice msgfind ? {@%s@@%s@}") % (table, message_id)
    return lx.eval(cmd)

import re
from ast import literal_eval
import agentspeak as asp


def parse_literal(msg):
    functor = msg.split("(")[0]

    if "(" in msg:
        args = msg.split("(")[1]
        args = args.split(")")[0]

        x = re.search("^_X_*", args)

        if x is not None:
            args = asp.Var()
        else:
            args = literal_eval(args)

        def recursion(arg):
            if isinstance(arg, list):
                return tuple(recursion(i) for i in arg)
            return arg

        new_args = (recursion(args),)

    else:
        new_args = ""
    return functor, new_args

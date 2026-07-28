import re
from ast import literal_eval
import agentspeak as asp


def parse_literal(msg):
    functor = msg.split("(")[0]
    if "(" in msg:
        args_str = msg.split("(", 1)[1].rsplit(")", 1)[0]
        parsed = [_parse_arg(a) for a in _split_args(args_str)]
        if len(parsed) == 1:
            new_args = (parsed[0],)
        else:
            new_args = tuple(parsed)
    else:
        new_args = ""
    return functor, new_args


def _split_args(s):
    """Split a comma-separated args string respecting nested parentheses."""
    args = []
    depth = 0
    current = []
    for c in s:
        if c == '(':
            depth += 1
        elif c == ')':
            depth -= 1
        if c == ',' and depth == 0:
            args.append(''.join(current).strip())
            current = []
        else:
            current.append(c)
    if current:
        args.append(''.join(current).strip())
    return [a for a in args if a]


def _parse_arg(s):
    """Convert a single serialized argument to the appropriate Python/agentspeak type."""
    s = s.strip()
    if not s:
        return None
    # Variable
    if re.search("^_X_*", s):
        return asp.Var()
    # Quoted string → Python str
    if s.startswith('"') and s.endswith('"'):
        return s[1:-1]
    # Number or other Python literal
    try:
        return literal_eval(s)
    except Exception:
        pass
    # Unquoted → atom (agentspeak Literal)
    return asp.Literal(s)

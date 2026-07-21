from collections import defaultdict
import re
from ast import literal_eval
import agentspeak as asp
from agentspeak.runtime import plan_to_str


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


def _ask_how(self, term):
    """
    AskHow is a performative that allows the agent to ask for a plan to another agent.
    We look in the plan.list of the slave agent the plan that master want,
    if we find it: master agent use tellHow to tell the plan to slave agent
    """
    sender_name = None

    # Receive the agent that ask for the plan
    for annotation in list(term.annots):
        if annotation.functor == "source":
            sender_name = annotation.args[0].functor

    if sender_name is None:
        raise asp.AslError("expected source annotation")

    plans_wanted = defaultdict(lambda: [])
    plans = self.plans.values()

    # Find the plans
    for plan in plans:
        for differents in plan:
            if differents.head.functor in term.args[0]:
                plans_wanted[
                    (
                        differents.trigger,
                        differents.goal_type,
                        differents.head.functor,
                        len(differents.head.args),
                    )
                ].append(differents)

    for plan in plans_wanted.values():
        for different in plan:
            strplan = plan_to_str(different)
            message = asp.Literal("plain_text", (strplan,), frozenset())
            message.with_annotation(asp.Literal("source", (asp.Literal(sender_name),)))
            self._call_ask_how(sender_name, message, asp.runtime.Intention())

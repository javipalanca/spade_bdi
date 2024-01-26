# -*- coding: utf-8 -*-
import asyncio
import collections
import time
from ast import literal_eval
from collections import deque

import agentspeak as asp
from agentspeak import runtime as asp_runtime, stdlib as asp_stdlib
from agentspeak.runtime import plan_to_str
from loguru import logger
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
from spade.template import Template

import re


PERCEPT_TAG = frozenset([asp.Literal("source", (asp.Literal("percept"),))])


class BeliefNotInitiated(Exception):
    pass


class BDIAgent(Agent):
    def __init__(
        self, jid: str, password: str, asl: str, actions=None, *args, **kwargs
    ):
        self.asl_file = asl
        self.bdi_enabled = False
        self.bdi_intention_buffer = deque()
        self.bdi = None
        self.bdi_agent = None

        super().__init__(jid, password, *args, **kwargs)
        while not self.loop:
            time.sleep(0.01)

        template = Template(metadata={"performative": "BDI"})
        self.add_behaviour(self.BDIBehaviour(), template)

        self.bdi_env = asp_runtime.Environment()
        self.bdi_actions = asp.Actions(asp_stdlib.actions) if not actions else actions
        self.bdi.add_actions()
        self.add_custom_actions(self.bdi_actions)
        self._load_asl()

    def add_custom_actions(self, actions):
        pass

    def pause_bdi(self):
        self.bdi_enabled = False

    def resume_bdi(self):
        self.bdi_enabled = True

    def add_behaviour(self, behaviour, template=None):
        if type(behaviour) == self.BDIBehaviour:
            self.bdi = behaviour
        super().add_behaviour(behaviour, template)

    def set_asl(self, asl_file: str):
        self.asl_file = asl_file
        self._load_asl()

    def _load_asl(self):
        self.pause_bdi()
        try:
            with open(self.asl_file) as source:
                self.bdi_agent = self.bdi_env.build_agent(source, self.bdi_actions)
            self.bdi_agent.name = self.jid
            self.resume_bdi()
        except FileNotFoundError:
            logger.info(
                "Warning: ASL specified for {} does not exist. Disabling BDI.".format(
                    self.jid
                )
            )
            self.asl_file = None
            self.pause_bdi()

    class BDIBehaviour(CyclicBehaviour):
        def add_actions(self):
            @self.agent.bdi_actions.add(".send", 3)
            def _send(agent, term, intention):
                receivers = asp.grounded(term.args[0], intention.scope)
                if isinstance(receivers, str) or isinstance(receivers, asp.Literal):
                    receivers = (receivers,)
                ilf = asp.grounded(term.args[1], intention.scope)
                if not asp.is_atom(ilf):
                    return
                ilf_type = ilf.functor
                mdata = {
                    "performative": "BDI",
                    "ilf_type": ilf_type,
                }
                for receiver in receivers:
                    body = asp.asl_str(asp.freeze(term.args[2], intention.scope, {}))
                    msg = Message(to=str(receiver), body=body, metadata=mdata)
                    self.agent.submit(self.send(msg))
                yield

        def set_belief(self, name: str, *args):
            """Set an agent's belief. If it already exists, updates it."""
            new_args = ()
            for x in args:
                if type(x) == str:
                    new_args += (asp.Literal(x),)
                else:
                    new_args += (x,)
            term = asp.Literal(name, tuple(new_args), PERCEPT_TAG)
            found = False
            for belief in list(self.agent.bdi_agent.beliefs[term.literal_group()]):
                if asp.unifies(term, belief):
                    found = True
                else:
                    self.agent.bdi_intention_buffer.append(
                        (
                            asp.Trigger.removal,
                            asp.GoalType.belief,
                            belief,
                            asp.runtime.Intention(),
                        )
                    )
            if not found:
                self.agent.bdi_intention_buffer.append(
                    (
                        asp.Trigger.addition,
                        asp.GoalType.belief,
                        term,
                        asp.runtime.Intention(),
                    )
                )

        def remove_belief(self, name: str, *args):
            """Remove an existing agent's belief."""
            new_args = ()
            for x in args:
                if type(x) == str:
                    new_args += (asp.Literal(x),)
                else:
                    new_args += (x,)
            term = asp.Literal(name, tuple(new_args), PERCEPT_TAG)
            self.agent.bdi_intention_buffer.append(
                (
                    asp.Trigger.removal,
                    asp.GoalType.belief,
                    term,
                    asp.runtime.Intention(),
                )
            )

        def get_belief(self, key: str, source=False):
            """Get an agent's existing belief. The first belief matching
            <key> is returned. Keep <source> False to strip source."""
            key = str(key)
            for beliefs in self.agent.bdi_agent.beliefs:
                if beliefs[0] == key:
                    if len(self.agent.bdi_agent.beliefs[beliefs]) == 0:
                        raise BeliefNotInitiated(key)
                    raw_belief = str(list(self.agent.bdi_agent.beliefs[beliefs])[0])
                    raw_belief = self._remove_source(raw_belief, source)
                    belief = raw_belief
                    return belief
            return None

        @staticmethod
        def _remove_source(belief, source):
            if ")[source" in belief and not source:
                belief = belief.split("[")[0].replace('"', "")
            return belief

        def get_belief_value(self, key: str):
            """Get an agent's existing value or values of the <key> belief. The first belief matching
            <key> is returned"""
            belief = self.get_belief(key)
            if belief:
                return tuple(belief.split("(")[1].split(")")[0].split(","))
            else:
                return None

        def get_beliefs(self, source=False):
            """Get agent's beliefs.Keep <source> False to strip source."""
            belief_list = []
            for beliefs in self.agent.bdi_agent.beliefs:
                try:
                    raw_belief = str(list(self.agent.bdi_agent.beliefs[beliefs])[0])
                    raw_belief = self._remove_source(raw_belief, source)
                    belief_list.append(raw_belief)
                except IndexError:
                    pass
            return belief_list

        def print_beliefs(self, source=False):
            """Print agent's beliefs.Keep <source> False to strip source."""
            for beliefs in self.agent.bdi_agent.beliefs.values():
                for belief in beliefs:
                    print(self._remove_source(str(belief), source))

        async def run(self):
            """
            Coroutine run cyclic.
            """
            if self.agent.bdi_enabled:
                msg = await self.receive(timeout=0)
                if msg:
                    mdata = msg.metadata
                    ilf_type = mdata["ilf_type"]
                    if ilf_type == "tell":
                        goal_type = asp.GoalType.belief
                        trigger = asp.Trigger.addition
                    elif ilf_type == "untell":
                        goal_type = asp.GoalType.belief
                        trigger = asp.Trigger.removal
                    elif ilf_type == "achieve":
                        goal_type = asp.GoalType.achievement
                        trigger = asp.Trigger.addition
                    elif ilf_type == "unachieve":
                        goal_type = asp.GoalType.achievement
                        trigger = asp.Trigger.removal
                    elif ilf_type == "tellHow":
                        goal_type = asp.GoalType.tellHow
                        trigger = asp.Trigger.addition
                    elif ilf_type == "untellHow":
                        goal_type = asp.GoalType.tellHow
                        trigger = asp.Trigger.removal
                    elif ilf_type == "askHow":
                        goal_type = asp.GoalType.askHow
                        trigger = asp.Trigger.addition
                    else:
                        raise asp.AslError(
                            "unknown illocutionary force: {}".format(ilf_type)
                        )

                    intention = asp.runtime.Intention()

                    # Prepare message. The message is either a plain text or a structured message.
                    if ilf_type in ["tellHow", "untellHow"]:
                        message = asp.Literal("plain_text", (msg.body,), frozenset())
                    elif ilf_type == "askHow":
                        message = asp.Literal("plain_text", (msg.body,), frozenset())

                        def _call_ask_how(self, receiver, message, intention):
                            # message.args[0] is the string plan to be sent
                            body = asp.asl_str(
                                asp.freeze(message.args[0], intention.scope, {})
                            )
                            mdata = {
                                "performative": "BDI",
                                "ilf_type": "tellHow",
                            }
                            msg = Message(to=receiver, body=body, metadata=mdata)
                            _call_ask_how.spade_agent.submit(
                                _call_ask_how.spade_class.send(msg)
                            )

                        _call_ask_how.spade_agent = self.agent

                        _call_ask_how.spade_class = self

                        asp_runtime.Agent._call_ask_how = _call_ask_how

                        # Overrides function ask_how from module agentspeak
                        asp_runtime.Agent._ask_how = _ask_how

                    else:
                        # Sends a literal
                        functor, args = parse_literal(msg.body)

                        message = asp.Literal(functor, args)

                    message = asp.freeze(message, intention.scope, {})

                    # Add source to message
                    tagged_message = message.with_annotation(
                        asp.Literal("source", (asp.Literal(str(msg.sender)),))
                    )
                    if ilf_type == "tellHow":
                        pass

                    self.agent.bdi_intention_buffer.append(
                        (trigger, goal_type, tagged_message, intention)
                    )

                if self.agent.bdi_intention_buffer:
                    temp_intentions = deque(self.agent.bdi_intention_buffer)
                    for trigger, goal_type, term, intention in temp_intentions:
                        self.agent.bdi_agent.call(trigger, goal_type, term, intention)
                        self.agent.bdi_intention_buffer.popleft()

                self.agent.bdi_agent.step()

            else:
                await asyncio.sleep(0.1)


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

    plans_wanted = collections.defaultdict(lambda: [])
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
            tagged_message = message.with_annotation(
                asp.Literal("source", (asp.Literal(sender_name),))
            )
            self._call_ask_how(sender_name, message, asp.runtime.Intention())

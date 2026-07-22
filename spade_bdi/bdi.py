from collections import deque

import agentspeak as asp
from agentspeak import runtime as asp_runtime, stdlib as asp_stdlib
from loguru import logger
from spade.agent import Agent
from spade.template import Template

from spade_bdi.bdi_behaviour import BDIBehaviour

PERCEPT_TAG = frozenset([asp.Literal("source", (asp.Literal("percept"),))])


class BDIAgent(Agent):
    def __init__(
        self, jid: str, password: str, asl: str, actions=None, *args, **kwargs
    ):
        self.asl_file = asl
        self.bdi_enabled = False
        self.bdi_intention_buffer = deque()
        self.bdi: BDIBehaviour = None
        self.bdi_agent = None

        super().__init__(jid, password, *args, **kwargs)

        template = Template(metadata={"performative": "BDI"})
        self.add_behaviour(BDIBehaviour(), template)

        self.bdi_env = asp_runtime.Environment()
        self.bdi_actions = asp.Actions(asp_stdlib.actions) if not actions else actions
        self.bdi.add_actions()
        self.add_custom_actions(self.bdi_actions)
        self._load_asl()

    def add_custom_actions(self, actions):  # pragma: no cover
        pass

    def pause_bdi(self):
        self.bdi_enabled = False

    def resume_bdi(self):
        self.bdi_enabled = True

    def add_behaviour(self, behaviour, template=None):
        if isinstance(behaviour, BDIBehaviour):
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

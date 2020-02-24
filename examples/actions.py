import argparse

import agentspeak
from spade import quit_spade

from spade_bdi.bdi import BDIAgent

parser = argparse.ArgumentParser(description='spade bdi basic example')
parser.add_argument('--server', type=str, default="localhost", help='XMPP server address.')
parser.add_argument('--name', type=str, default="basicagent", help='XMPP name for the agent.')
parser.add_argument('--password', type=str, default="bdipassword", help='XMPP password for the agent.')
arguments = parser.parse_args()


class MyCustomBDIAgent(BDIAgent):
    def add_custom_actions(self, actions):
        @actions.add_function(".my_function", (int,))
        def _my_function(x):
            return x * x

        @actions.add(".my_action", 1)
        def _my_action(agent, term, intention):
            arg = agentspeak.grounded(term.args[0], intention.scope)
            print(arg)
            yield


a = MyCustomBDIAgent("{}@{}".format(arguments.name, arguments.server), arguments.password, "actions.asl")

a.start()

import time

time.sleep(2)
a.stop().result()

quit_spade()

import getpass
import time

import agentspeak
from spade import quit_spade

from spade_bdi.bdi import BDIAgent

jid = input("JID> ")
passwd = getpass.getpass()


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


a = MyCustomBDIAgent(jid, passwd, "actions.asl")

a.start()


time.sleep(2)
a.stop().result()

quit_spade()

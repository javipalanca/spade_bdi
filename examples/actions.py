import asyncio
import getpass

import agentspeak
import spade

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


async def main():
    a = MyCustomBDIAgent(jid, passwd, "actions.asl")

    await a.start()

    await asyncio.sleep(2)
    await a.stop()


if __name__ == "__main__":
    spade.run(main())

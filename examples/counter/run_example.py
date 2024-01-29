import argparse
import asyncio
import getpass
from datetime import datetime, timedelta

import spade
from spade.behaviour import PeriodicBehaviour, TimeoutBehaviour
from spade.template import Template

from spade_bdi.bdi import BDIAgent


class CounterAgent(BDIAgent):
    async def setup(self):
        template = Template(metadata={"performative": "B1"})
        self.add_behaviour(self.UpdateCounterBehav(period=0.5, start_at=datetime.now()), template)
        template = Template(metadata={"performative": "B2"})
        self.add_behaviour(self.ResetCounterBehav(period=2, start_at=datetime.now()), template)
        template = Template(metadata={"performative": "B3"})
        self.add_behaviour(self.SwitchBeliefBehav(period=1, start_at=datetime.now()), template)
        template = Template(metadata={"performative": "B4"})
        self.add_behaviour(self.RemoveBeliefsBehav(start_at=datetime.now() + timedelta(seconds=4.5)), template)

    class UpdateCounterBehav(PeriodicBehaviour):
        async def on_start(self):
            self.counter = self.agent.bdi.get_belief_value("counter")[0]

        async def run(self):
            if self.counter != self.agent.bdi.get_belief_value("counter")[0]:
                self.counter = self.agent.bdi.get_belief_value("counter")[0]
                print(self.agent.bdi.get_belief("counter"))

    class ResetCounterBehav(PeriodicBehaviour):
        async def run(self):
            self.agent.bdi.set_belief('counter', 0)

    class SwitchBeliefBehav(PeriodicBehaviour):
        async def run(self):
            try:
                type = self.agent.bdi.get_belief_value("type")[0]
                if type == 'inc':
                    self.agent.bdi.set_belief('type', 'dec')
                else:
                    self.agent.bdi.set_belief('type', 'inc')
            except Exception as e:
                print("No belief 'type'.")

    class RemoveBeliefsBehav(TimeoutBehaviour):
        async def run(self):
            self.agent.bdi.remove_belief('type', 'inc')
            self.agent.bdi.remove_belief('type', 'dec')


async def main(server, password):
    a = CounterAgent("counter@" + server, password, "counter.asl")
    await a.start()

    await asyncio.sleep(5)
    await a.stop()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--server", help="XMPP Server")
    parser.add_argument("--password", help="Password")
    args = parser.parse_args()

    if args.server is None:
        server = input("XMPP Server> ")
    else:
        server = args.server

    if args.password is None:
        passwd = getpass.getpass()
    else:
        passwd = args.password
    spade.run(main(server, passwd))

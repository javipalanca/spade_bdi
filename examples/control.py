import asyncio
import getpass
from datetime import datetime, timedelta

import spade
from spade.behaviour import PeriodicBehaviour, TimeoutBehaviour
from spade.template import Template

from spade_bdi.bdi import BDIAgent


class MasterAgent(BDIAgent):
    async def setup(self):
        template = Template(metadata={"performative": "Modify"})
        self.add_behaviour(self.Modify(period=5, start_at=datetime.now()), template)

        template = Template(metadata={"performative": "Ending"})
        self.add_behaviour(self.Behav4(start_at=datetime.now() + timedelta(seconds=11)), template)

    class Modify(PeriodicBehaviour):
        async def run(self):
            if self.agent.bdi_enabled:
                try:
                    count_type = self.agent.bdi.get_belief_value("type")[0]
                    if count_type == 'inc':
                        self.agent.bdi.set_belief('type', 'dec')
                    else:
                        self.agent.bdi.set_belief('type', 'inc')
                except Exception as e:
                    self.kill()

    class Behav4(TimeoutBehaviour):
        async def run(self):
            self.agent.bdi.remove_belief('type', 'inc')
            self.agent.bdi.remove_belief('type', 'dec')


async def main(server, password):
    b = BDIAgent("slave_1@{}".format(server), password, "slave.asl")
    b.bdi.set_belief("master", "master@{}".format(server))
    await b.start()

    c = BDIAgent("slave_2@{}".format(server), password, "slave.asl")
    c.pause_bdi()
    await c.start()

    a = MasterAgent("master@{}".format(server), password, "master.asl")
    a.bdi.set_belief("slave1", "slave_1@{}".format(server))
    a.bdi.set_belief("slave2", "slave_2@{}".format(server))
    a.bdi.set_belief('type', 'dec')
    await a.start()


    await asyncio.sleep(5)
    print("Enabling BDI for slave2")
    c.set_asl("slave.asl")
    c.bdi.set_belief("master", "master@{}".format(server))
    await asyncio.sleep(5)
    print("Disabling BDI for slave2")
    c.pause_bdi()


if __name__ == "__main__":

    server = input("XMPP Server> ")
    passwd = getpass.getpass()

    try:
        spade.run(main(server, passwd))
    except KeyboardInterrupt:
        print("Exiting...")

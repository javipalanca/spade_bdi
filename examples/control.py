import argparse
import time

from spade_bdi.bdi import BDIAgent
from spade.template import Template
from spade.behaviour import PeriodicBehaviour
from spade.behaviour import TimeoutBehaviour
from datetime import datetime
from datetime import timedelta


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


def main(server, password):
    b = BDIAgent("slave_1@{}".format(server), password, "slave.asl")
    b.bdi.set_belief("master", "master@{}".format(server))
    future = b.start()
    future.result()

    c = BDIAgent("slave_2@{}".format(server), password, "slave.asl")
    c.pause_bdi()
    future = c.start()
    future.result()

    a = MasterAgent("master@{}".format(server), password, "master.asl")
    a.bdi.set_belief("slave1", "slave_1@{}".format(server))
    a.bdi.set_belief("slave2", "slave_2@{}".format(server))
    a.bdi.set_belief('type', 'dec')
    future = a.start()
    future.result()

    time.sleep(5)
    print("Enabling BDI for slave2")
    c.set_asl("slave.asl")
    c.bdi.set_belief("master", "master@{}".format(server))
    time.sleep(5)
    print("Disabling BDI for slave2")
    c.pause_bdi()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='spade bdi master-server example')
    parser.add_argument('--server', type=str, default="localhost", help='XMPP server address.')
    parser.add_argument('--password', type=str, default="bdipassword", help='XMPP password for the agents.')
    args = parser.parse_args()

    try:
        main(args.server, args.password)
    except KeyboardInterrupt:
        print("Exiting...")

import argparse
import asyncio
import getpass

import spade

from spade_bdi.bdi import BDIAgent


async def main(server, password):
    a = BDIAgent(f"bdiagent@{server}", password, "basic.asl")
    await a.start()

    await asyncio.sleep(1)

    a.bdi.set_belief("car", "azul", "big")
    a.bdi.print_beliefs()
    print("GETTING FIRST CAR BELIEF")
    print(a.bdi.get_belief("car"))
    a.bdi.print_beliefs()
    a.bdi.remove_belief("car", 'azul', "big")
    a.bdi.print_beliefs()
    print(a.bdi.get_beliefs())
    a.bdi.set_belief("car", 'amarillo')

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

import argparse
import asyncio
import getpass

import spade

from spade_bdi.bdi import BDIAgent


async def main(server, password):
    receiver = BDIAgent("BDIReceiverAgent@" + server, password, "receiver.asl")
    await receiver.start()

    sender = BDIAgent("BDISenderAgent@" + server, password, "sender.asl")
    sender.bdi.set_belief("receiver", "BDIReceiverAgent@" + server)
    await sender.start()

    await asyncio.sleep(1.5)
    await sender.stop()
    await receiver.stop()


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

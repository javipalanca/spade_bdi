import argparse
import asyncio
import getpass
import spade

from spade_bdi.bdi import BDIAgent


async def main(server, password):
    a = BDIAgent("receiver@{}".format(server), password, "receiver.asl")
    a.bdi.set_belief("sender", "sender@{}".format(server))
    await a.start()

    b = BDIAgent("sender@{}".format(server), password, "sender.asl")
    b.bdi.set_belief("receiver", "receiver@{}".format(server))
    await b.start()

    await asyncio.sleep(5)
    await a.stop()
    await b.stop()


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

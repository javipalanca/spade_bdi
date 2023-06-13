import getpass

import spade

from spade_bdi.bdi import BDIAgent


async def main():
    a = BDIAgent("BDISenderAgent@" + server, passwd, "sender.asl")
    a.bdi.set_belief("receiver", "BDIReceiverAgent@" + server)
    await a.start()


if __name__ == '__main__':
    server = input("XMPP Server> ")
    passwd = getpass.getpass()

    spade.run(main())

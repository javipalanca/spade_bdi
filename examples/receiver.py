import getpass

import spade

from spade_bdi.bdi import BDIAgent


async def main():
    a = BDIAgent("BDIReceiverAgent@" + server, passwd, "receiver.asl")
    await a.start()


if __name__ == '__main__':
    server = input("XMPP Server> ")
    passwd = getpass.getpass()

    spade.run(main())

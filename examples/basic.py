import asyncio
import getpass

import spade

from spade_bdi.bdi import BDIAgent


async def main():

    jid = input("JID> ")
    passwd = getpass.getpass()

    a = BDIAgent(jid, passwd, "basic.asl")
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

    await asyncio.sleep(1)

    await a.stop()

if __name__ == "__main__":
    spade.run(main())

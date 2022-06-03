import time
import getpass

from spade import quit_spade

from spade_bdi.bdi import BDIAgent

jid = input("JID> ")
passwd = getpass.getpass()

a = BDIAgent(jid, passwd, "basic.asl")
a.start()

time.sleep(1)

a.bdi.set_belief("car", "azul", "big")
a.bdi.print_beliefs()
print("GETTING FIRST CAR BELIEF")
print(a.bdi.get_belief("car"))
a.bdi.print_beliefs()
a.bdi.remove_belief("car", 'azul', "big")
a.bdi.print_beliefs()
print(a.bdi.get_beliefs())
a.bdi.set_belief("car", 'amarillo')

time.sleep(1)

a.stop().result()

quit_spade()
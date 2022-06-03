import getpass

from spade_bdi.bdi import BDIAgent

if __name__ == '__main__':
    server = input("XMPP Server> ")
    passwd = getpass.getpass()

    a = BDIAgent("BDISenderAgent@" + server, passwd, "sender.asl")
    a.bdi.set_belief("receiver", "BDIReceiverAgent@" + server)
    a.start()

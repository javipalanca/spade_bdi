import argparse
import getpass
import subprocess

examples = [
    "basic",
    "actions",
    "counter",
    "sender_receiver",
    "master_slave",
    "ask_how",
    "send_achieve",
    "send_achieve_param",
    "tell_belief",
    "tell_how",
    "unachieve_no_recursive",
    "unachieve_while",
    "untell",
    "untell_how",
]
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

    for example in examples:
        l = 20 + len(example)
        print(l*"*" + "\n" + f"* Running {example} example *" + "\n" + l*"*")
        # Run example using subprocess
        subprocess.call(args=["python", "run_example.py", "--server",  f"{server}", "--password", f"{passwd}"],
                        cwd=f"./{example}")
        print("Finished {}".format(example))

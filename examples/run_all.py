import argparse
import getpass
import subprocess

examples = [
    "ask_how",
    "send_achieve",
    "send_achieve_param",
    "tell_belief",
    # "tell_how",
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
        print("Running {}".format(example))
        # Run example using subprocess
        subprocess.call(["python", f"{example}/run_example.py", "--server",  f"{server}", "--password", f"{passwd}"])
        print("Finished {}".format(example))

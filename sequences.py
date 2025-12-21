import time
from threading import Thread

def run_sequence(terminal, commands):
    def execute():
        for cmd in commands:
            if cmd.startswith("WAIT"):
                seconds = int(cmd.split()[1])
                time.sleep(seconds)
            else:
                terminal.channel.send(cmd + "\n")
                time.sleep(0.5) # Basic pacing
    Thread(target=execute, daemon=True).start()

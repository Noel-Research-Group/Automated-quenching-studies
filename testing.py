"""
Author: Elia Savino
github: github.com/EliaSavino

Happy Hacking!

Descr: Reverse engineering of the codes

"""

import numpy as np
import pandas as pd
from DeviceClasses import Autosampler
import itertools

#
# port = '/dev/tty.usbserial-FTALDLQA'
#
# autosampler = Autosampler(comnumber=port, baudrate=9600)
# autorsampler.SendCommand(task = '0831', message='000000')


def save_progress(filename, command):
    with open(filename, "a+") as f:
        f.write(f"{command}\n")



def load_progress(filename):
    try:
        with open(filename, "r") as f:
            return [line.strip() for line in f]
    except FileNotFoundError:
        return []


# File to save valid commands and progress
valid_commands_file = "valid_commands.txt"
progress_file = "progress.txt"

# Load previously found valid commands and progress
valid_commands = load_progress(valid_commands_file)
processed_commands = set(load_progress(progress_file))

# Set of known valid commands (for simulation purposes, replace with actual known commands)
known_commands = {
    "1001",
    "5001",
    "0150",
    "0100",
    "0108",
    "0109",
    "0501",
    "0510",
    "0830",
    "0112",
    "0131",
    '0193',
    '0500',
    '0192',
    '0124',
    '0130',
    '0111',
    '0107'
}  # Example known commands

# autosampler = Autosampler()
# Iterate over all 4-digit combinations

print('''
   __                                __            _   ___       _   
  /__\ _____   _____ _ __ ___  ___  /___ __   __ _(_) / __\ ___ | |_ 
 / \/// _ \ \ / / _ | '__/ __|/ _ \/_\| '_ \ / _` | |/__\/// _ \| __|
/ _  |  __/\ V |  __| |  \__ |  __//__| | | | (_| | / \/  | (_) | |_ 
\/ \_/\___| \_/ \___|_|  |___/\___\__/|_| |_|\__, |_\_____/\___/ \__|
                                             |___/                   

Good Morning Hackers! let's try to hack the Autosampler!

''')
for combo in itertools.product("0123456789", repeat=4):
    command = "".join(combo)
    print(f"Trying command {command} ...")
    print(f"Processed commands: {len(processed_commands)} That is {len(processed_commands) / 10000 * 100}%")

    # Skip if already processed
    if command in processed_commands or command in known_commands:
        continue

    # Send command to the Autosampler
    response = autosampler.SendCommand(command, message='000000', send = 0)

    # Check if the command was recognized
    if response != "\x15":
        valid_commands.append(command)
        save_progress(valid_commands_file, command)

    # Mark command as processed
    processed_commands.add(command)
    save_progress(progress_file, command)

print("Process completed.")

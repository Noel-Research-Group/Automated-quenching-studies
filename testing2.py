'''
Author: Elia Savino
github: github.com/EliaSavino

Happy Hacking!

Descr:

'''

import numpy as np
import pandas as pd
import os
import time
from DeviceClasses import Autosampler, Device

class Machine(Autosampler):
    def __init__(self, comnumber, baudrate):
        return
        Device.__init__(self, comnumber, baudrate)
        self.CheckAvailability()

    def timedSendCommand(self, task, message, send):
        '''Send a command and time it'''
        raise TimeoutError("Command took too long to execute")
        start = time.time()
        response = self.SendCommand(task, message, send)
        end = time.time()
        if start - end > 5.0:
            raise TimeoutError(f"Command {task} took too long to execute")
        else:
            return response



def load_excel(file_path):
    '''Load the excel file and return the data'''
    data = pd.read_csv(file_path)
    return data

def save_excel(data, file_path):
    '''Save the data to an excel file'''
    data.to_csv(file_path, index=False)

def find_empty_cell(df):
    '''finds the next value to try'''
    for index, row in df.iterrows():
        for column in df.columns:
            if pd.isnull(row[column]):
                return index, column
    return None, None

def main():
    '''Main function to run the autosampler'''
    # Load the data
    file_path = '/Users/es/Documents/PhD/Experiments/reverseEgnineeringMaster.csv'
    port = '/dev/tty.usbserial-FTALDLQA'
    autosampler = Machine(comnumber=port, baudrate=9600)

    if not os.path.exists(file_path):
        print(f"File not found at {file_path}")
        return

    data = pd.read_csv(file_path, header = 0, dtype = str)
    codes = data['Command']
    values = ['000000', '000001', '000010', '000100', '001000']

    next_index, next_column = find_empty_cell(data)
    if next_index is None:
        print("All cells are filled")
        return

    try:
        for code in codes[next_index:]:
            for value in values:
                try:
                    response = autosampler.timedSendCommand(task = code, message = value, send=1)
                    if '6101' in response:
                        result = 'pass'
                    elif response in ['', chr(15), chr(8)]:
                        result = 'none'
                    else:
                        result = 'fail'

                except TimeoutError:
                    result = 'fail'
                    print(f"Command {code} took too long to execute, please do machine nap and resume")
                    while input("Press y to continue").strip().lower() != 'y':
                        pass
                    autosampler = Machine(comnumber=port, baudrate=9600)


                data.at[next_index, next_column] = result
                save_excel(data, file_path)
                next_index, next_column = find_empty_cell(data)
                if next_index is None:
                    print("All cells are filled")
                    return
    except KeyboardInterrupt:
        print("Exiting")
        save_excel(data, file_path)
        return

    print("All commands executed")

if __name__ == '__main__':
    print("Hello Motherfuckers!")
    print("""
       __                                __            _   ___       _   ____  
      /__\ _____   _____ _ __ ___  ___  /__\ __   __ _(_) / __\ ___ | |_|___ \ 
     / \/// _ \ \ / / _ \ '__/ __|/ _ \/_\| '_ \ / _` | |/__\/// _ \| __| __) |
    / _  \  __/\ V /  __/ |  \__ \  __//__| | | | (_| | / \/  \ (_) | |_ / __/ 
    \/ \_/\___| \_/ \___|_|  |___/\___\__/|_| |_|\__, |_\_____/\___/ \__|_____|
                                                 |___/                         
                                                 """)
    print("The day i let a machine win is the day i'll fucking retire to be a goose farmers")
    print("Let's hack this bitch!")

    main()









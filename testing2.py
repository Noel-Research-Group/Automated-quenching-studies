'''
Author: Elia Savino
github: github.com/EliaSavino

Happy Hacking!

Descr: Second set of tests for the Autosampler

'''

import numpy as np
import pandas as pd
import os
import time
from DeviceClasses import Autosampler, Device

class Machine(Autosampler):
    def __init__(self, comnumber, baudrate):
        Device.__init__(self, comnumber, baudrate)
        self.timeout = 1
        self.CheckAvailability()

    def construct_message(self, ai, task, message):
        command_message = '61{0}{1}{2}'.format(ai, task, message)
        return (chr(2) + command_message + chr(3)).encode('ascii')

    def wait_for_answer(self):
        start_time = time.time()
        while True:
            answer = self.serialObj.readline()
            if len(answer) > 0:
                answer_decoded = answer.decode()
                return self.decode_response(answer_decoded)
            if time.time() - start_time > self.timeout:
                self.logger.debug('Nothing returned from the autosampler.')
                return 'nothing returned'
            time.sleep(0.1)
            self.logger.debug('No answer from the autosampler yet.')

    def decode_response(self, response):
        if response == chr(6):
            decoded_response = 'Ack'
        elif response == chr(21):
            decoded_response = 'Nack'
        elif response == chr(8):
            decoded_response = 'Nack0'
        else:
            decoded_response = response
        self.logger.debug('Decoded response: {}'.format(decoded_response))
        return decoded_response

    def send_follow_up(self, task, send_type):
        if send_type in ['SP', 'SA']:
            follow_up_message = '6101{0}0000{1}'.format('10' if send_type == 'SP' else '00', task)
            mss = str.encode(chr(2) + follow_up_message + chr(3))
            self.serialObj.write(mss)
            self.logger.debug(
                'The follow-up message was successfully sent to the autosampler: {}.'.format(follow_up_message))
            return self.wait_for_answer()

    def send_command(self, task, message, send='none', ai='01'):
        # Construct the command message
        mss = self.construct_message(ai, task, message)

        self.serialObj.write(mss)
        self.logger.debug('The following message was sent to the autosampler: {}.'.format(mss.decode('ascii')))

        # Wait for an answer
        answer = self.wait_for_answer()

        # Handle follow-up send command
        if send in ['SP', 'SA'] and answer != 'nothing returned':
            answer = self.send_follow_up(task, send)
            self.logger.debug('Autosampler gave the following answer: {} to the follow-up request.'.format(answer))

        return answer

    def check_status(self):
        '''Check the status of the autosampler'''
        response = self.send_command('1001', '000152')
        return response

    def check_errors(self):
        '''Check the errors of the autosampler'''
        response = self.send_command('1001', '000155')
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
                    print(f"Command {code} with value {value} returned {response}")
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


def main2():
    """same as before, however now it tries the ones that returned a pass and records the response"""
    file_path = '/Users/es/Documents/PhD/Experiments/reverseEgnineeringMaster.csv'
    result_path = '/Users/es/Documents/PhD/Experiments/reverseEgnineeringMasterResults.csv'
    port = '/dev/tty.usbserial-FTALDLQA'
    autosampler = Machine(comnumber=port, baudrate=9600)


    if not os.path.exists(file_path):
        print(f"File not found at {file_path}")
        return

    data = pd.read_csv(file_path, header = 0, dtype = str)

    if not os.path.exists(result_path):
        pass
    else:
        results = pd.read_csv(result_path, header=0, dtype=str)

    codes = data['Command']
    values = ['000000', '000001', '000010', '000100', '001000']




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









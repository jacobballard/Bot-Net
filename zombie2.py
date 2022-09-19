#!/usr/bin/env python3

# Zombie Program
# Jacob Ballard
# Dr. Bradshaw
# CSC 382

import subprocess
import select
import multiprocessing
import sys
from os.path import exists
from socket import *
import _thread


class ProcessHandler:
    script_name = ""

    def __init__(self, script_name):
        self.script_name = script_name

    def run_script(self):
        # print("run script")
        script_to_run = "./" + self.script_name
        output = subprocess.check_output(script_to_run)
        # print('out')
        # print(output)
        # print(self.script_name)
        file_to_save_to = "OUT" + self.script_name[:-3] + ".txt"

        file = open(file_to_save_to, "a")
        file.write(self.script_name + "\n")

        # print("output")
        # print(output.decode())
        file.write(output.decode())
        file.write("\n")
        file.close()

    def get_report(self):
        # print("get report")
        output_file_name = "OUT" + self.script_name[:-3] + ".txt"

        if exists(output_file_name):
            file = open(output_file_name, "r")

            string_arr = file.readlines()
            file.close()
            together = ""
            for line in string_arr:
                together = together + line

            return together
        else:
            return "Program is still running!"


class ZombieProcess:
    command = ""

    def __init__(self, command):
        self.command = command

    def process_command(self, running_processes, a_socket):
        # print("process???")
        if not (self.command.find("INI") == -1):
            # print("INI")
            # print(self.command.find(".."))
            # print(len(self.command))
            if not self.command.find("..") == -1:
                # We're good to proceed with a start process command
                script = self.command[3:(self.command.find(".."))]
                # print(script)
                print("obtained script name" + script)

                if exists(script):
                    print("script existss")
                    # print("")s
                    self.start_process(script, running_processes, a_socket)
                else:
                    print("script doesn't exist")
                    to_send = "ERR" + script
                    a_socket.send(to_send.encode())
                    a_socket.close()

        elif not (self.command.find("STP") == -1):
            script = self.command[3:-2]

            self.stop_process(script, running_processes)

        elif not (self.command.find("RPT") == -1):
            script = self.command[3:-2]

            self.report(script, running_processes, a_socket)
        else:
            print("We should never get this!")

    def start_process(self, script_name, running_processes, a_socket):
        # print("start")
        try:
            if running_processes[script_name[:-3]]:
                # It already exists and is running still, do nothing
                # print("Oh no that's not good!")
                error_message = "ERR" + script_name

                # print("ERROR MESSAGE" + error_message)
                a_socket.send(error_message.encode())
                # a_socket.close()

        except:
            # Doesn't exist, time to make it
            mp_method = ProcessHandler(script_name)
            # running_processes[script_name] = multiprocessing.Process(
            #     target=mp_method.run_script(), args=())
            # running_processes[script_name].start()
            try:
                _thread.start_new_thread(mp_method.run_script, ())
                # print("success???????")
                success_message = "SUC" + script_name
                a_socket.send(success_message.encode())

            except:
                # print("failiure??!!!")
                error_message = "ERR" + script_name
                a_socket.send(error_message.encode())

    def stop_process(self, script_name, running_processes):
        try:
            running_processes[script_name[:-3]].terminate()

            # https://www.tutorialspoint.com/python/python_dictionary.htm
            del running_processes[script_name[:-3]]
        except:
            print("Script wasn't in running_processes")

    def report(self, script_name, running_processes, socket):
        print("bouta report")
        print(script_name)
        print(running_processes)
        try:
            if running_processes[script_name[:-3]].isAlive():
                print("is alive")
                header = "RPT" + script_name + ".."
                together = header + "Script still running!"
                socket.send(together.encode())

        except:
            print("Obviously can't be alive because we got here")
            report_handler = ProcessHandler(script_name)

            # print("report handler instantiated")
            to_send = report_handler.get_report()

            header = "RPT" + script_name + ".."

            together = header + to_send

            # print(together)

            socket.send(together.encode())
            # socket.close()

            # print("sent to socket???????")


def main():

    a_socket = socket(AF_INET, SOCK_STREAM)
    # print("main")
    all_sockets = [0] * 3
    all_sockets[0] = a_socket
    all_sockets[0].bind(('localhost', 5020))

    all_sockets[0].listen(1)

    running_processes = {}

    done = False
    while not done:
        input_ready, output_ready, except_ready = select.select(
            all_sockets, [], [])

        for i in input_ready:
            for j in range(len(all_sockets)):
                if i == all_sockets[j]:
                    a_socket, addr = i.accept()
                    response = a_socket.recv(1024).decode()
                    # print("response")
                    # print(response)
                    command = ZombieProcess(response)
                    command.process_command(running_processes, a_socket)


main()

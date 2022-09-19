#!/usr/bin/env python3

from socket import AF_INET, SOCK_STREAM
import select
import threading
import sys
from socket import *


class Connection:

    def __init__(self):
        pass

    def send_to_socket(self, zombie, type, command):
        if type == "INI":
            self.send_start_process_request(zombie, type, command)
        elif type == "STP":
            self.send_stop_process_request(zombie, type, command)
        elif type == "RPT":
            # print("RPT")
            self.send_report_request(zombie, type, command)
        else:
            print("Oh no this should never happen")

    def send_start_process_request(self, zombie, type, command):
        request = type + command + ".."

        # print("bouta established?")

        zombie_socket = self.establish_socket(zombie)

        zombie_socket.send(request.encode())

        # print("sending!!!!!!")

    def send_stop_process_request(self, zombie, type, command):
        request = type + command + ".."

        zombie_socket = self.establish_socket(zombie)

        zombie_socket.send(request.encode())
        all_sockets = zombie.get_sockets()
        for i in range(len(all_sockets)):
            if all_sockets[i] == zombie_socket:
                # https://www.w3schools.com/python/gloss_python_remove_list_items.asp
                del all_sockets[i]
        zombie_socket.close()

    def send_report_request(self, zombie, type, command):
        # print("sent report request")
        request = type + command + ".."

        zombie_socket = self.establish_socket(zombie)

        zombie_socket.send(request.encode())

    def establish_socket(self, zombie):
        # print("establish")
        zombie_socket = socket(AF_INET, SOCK_STREAM)
        # print("zombie")
        # print(zombie)
        # print(zombie.hostname)
        # print(zombie.port)
        zombie_socket.connect((zombie.hostname, zombie.port))

        socket_name = zombie.hostname + str(zombie.port)
        zombie.add_socket(zombie_socket, socket_name)

        return zombie_socket


class OpenSocketHandler:

    def __init__(self):
        pass

    def handle_response_data(self, socket, response, all_zombies_dict):
        # print("a response happened??")
        # print(all_zombies_dict)
        # https://www.geeksforgeeks.org/iterate-over-a-dictionary-in-python/
        for key, value in all_zombies_dict.items():
            flag = False
            all_sockets = value.get_sockets()
            # print("then all sockets")
            # print(all_sockets)
            name = ""

            for a_socket_name, a_socket in all_sockets.items():
                if socket == a_socket:
                    #Got the socket now handle
                    # print("in a socket handling stuff")
                    name = a_socket_name
                    if not response.find("RPT") == -1:
                        # print("report!!!")
                        print("Zombie Report: \n")
                        print(response[(response.find("..") + 3)::])
                        # del all_sockets[a_socket_name]
                        socket.close()
                        flag = True

                    elif not response.find("ERR") == -1:
                        # print("ERROR")
                        print(a_socket_name + " " + response)
                        # del all_sockets[a_socket_name]
                        socket.close()
                        flag = True
                    elif not response.find("SUC") == -1:
                        # del all_sockets[a_socket_name]
                        socket.close()
                        flag = True
            if flag:
                del all_sockets[name]

    def handle_request_data(self, request, all_zombies_dicts):

        if not request.find("all") == -1:
            if not request.find("start") == -1:
                start_request = Command()
                script_name = request[(request.find("start") + 6)::]

                start_request.start_process(script_name, all_zombies_dicts)
            elif not request.find("stop") == -1:
                stop_request = Command()
                script_name = request[(request.find("stop") + 5)::]
                stop_request.stop_process(script_name, all_zombies_dicts)
            elif not request.find("report") == -1:
                report_request = Command()
                script_name = request[(request.find("report") + 7)::]
                # print(script_name)
                # print("script_name jacob ballard")
                report_request.report(script_name, all_zombies_dicts)
        elif not request.find("individual") == -1:

            if not request.find("start") == -1:

                if not request.find("bill") == -1:
                    # print("found bill starts")
                    start_request = Command()
                    script_name = request[(request.find("bill") + 5)::]
                    # print("script name 2")
                    # print(script_name)
                    zom_dicts = {"bill": all_zombies_dicts["bill"]}
                    # print("here right????")
                    start_request.start_process(script_name, zom_dicts)

                elif not request.find("ned") == -1:
                    start_request = Command()
                    script_name = request[(request.find("ned") + 4)::]
                    zom_dicts = {"ned": all_zombies_dicts["ned"]}
                    start_request.start_process(script_name, zom_dicts)
                elif not request.find("ted") == -1:
                    start_request = Command()
                    script_name = request[(request.find("ted") + 4)::]
                    zom_dicts = {"ted": all_zombies_dicts["ted"]}
                    start_request.start_process(script_name, zom_dicts)

            elif not request.find("stop") == -1:

                if not request.find("bill") == -1:
                    stop_request = Command()
                    script_name = request[(request.find("bill") + 5)::]
                    stop_request.stop_process(
                        script_name, {"bill": all_zombies_dicts["bill"]})
                elif not request.find("ned") == -1:
                    stop_request = Command()
                    script_name = request[(request.find("ned") + 4)::]
                    stop_request.stop_process(
                        script_name, {"ned": all_zombies_dicts["ned"]})
                elif not request.find("ted") == -1:
                    stop_request = Command()
                    script_name = request[(request.find("ted") + 4)::]
                    stop_request.stop_process(
                        script_name, {"ted": all_zombies_dicts["ted"]})

            elif not request.find("report") == -1:
                # print("doing report???? from parse")
                if not request.find("bill") == -1:
                    report_request = Command()
                    script_name = request[(request.find("bill") + 5)::]

                    report_request.report(script_name,
                                          {"bill": all_zombies_dicts["bill"]})
                elif not request.find("ned") == -1:
                    report_request = Command()
                    script_name = request[(request.find("ned") + 4)::]
                    report_request.report(script_name,
                                          {"ned": all_zombies_dicts["ned"]})
                elif not request.find("ted") == -1:
                    report_request = Command()
                    script_name = request[(request.find("ted") + 4)::]
                    report_request.report(script_name,
                                          {"ted": all_zombies_dicts["ted"]})

    def gather_sockets(self, all_zombies_dict):
        together = [0]

        # https://stackoverflow.com/questions/7053551/python-valueerror-too-many-values-to-unpack
        # Might be misremembering 117 but I though it was (key,value) in dict but that
        # doesn't work so I troubleshooted
        for value in all_zombies_dict.values():
            # print("value")
            # print(value)
            for a_socket in value.get_sockets().values():

                if a_socket not in together:
                    # print("together")
                    together = together + [a_socket]

        # print("returning together")
        return together

    def check_on_open_ports(self, all_zombies_dict):

        active_sockets = self.gather_sockets(all_zombies_dict)

        # for a_socket in active_sockets:

        # https://code.activestate.com/recipes/531824-chat-server-client-using-selectselect/
        # print("active sockets")
        # print(active_sockets)
        # print("active sockets done")
        input_ready, output_ready, except_ready = select.select(
            active_sockets, [], [])
        # print(input_ready)
        # print("all clear again?")
        for i in input_ready:
            # print(i)
            # print("input ready")
            if i == 0:
                # print("it did!")
                # Came from the commander
                data = sys.stdin.readline().strip()
                # print(data)
                self.handle_request_data(data, all_zombies_dict)
            else:
                for j in range(len(active_sockets)):
                    # print(j)
                    # print("j")
                    if i == active_sockets[j]:
                        # print("i cleared???")
                        # print(i)

                        # the_socket, addr = i.accept()

                        # print("accepted???")
                        response = i.recv(1024).decode()

                        self.handle_response_data(i, response,
                                                  all_zombies_dict)


class Zombie:
    hostname = ""
    port = -1
    name = ""

    sockets = {}

    def __init__(self, hostname, port, name):
        self.hostname = hostname
        self.port = port
        self.name = name

    def add_socket(self, socket, name):
        if name in self.sockets:
            name = name + "01"
        self.sockets[name] = socket

    def get_sockets(self):
        # print(self.sockets)
        return self.sockets


class Command:

    def __init__(self):
        pass

    def start_process(self, script_name, on_zombies):
        # print("starting")
        # print(on_zombies)
        for client_name, client in on_zombies.items():
            connection = Connection()
            print("start")
            print(script_name)
            connection.send_to_socket(client, "INI", script_name)

    def stop_process(self, script_name, on_zombies):
        for client_name, client in on_zombies.items():
            connection = Connection()
            connection.send_to_socket(client, "STP", script_name)

    def report(self, script_name, on_zombies):
        for client_name, client in on_zombies.items():
            # print("for client on report")
            connection = Connection()
            connection.send_to_socket(client, "RPT", script_name)


def main():
    # print("here???")
    done = False

    # a_zombie = Zombie("10.14.1.69", 5016, "condor")

    a_zombie = Zombie("localhost", 5019, "condor")

    # b_zombie = Zombie("10.14.1.70", 5016, "owl")
    b_zombie = Zombie("localhost", 5021, "owl")

    # c_zombie = Zombie("10.14.1.69", 5017, "condor2")
    c_zombie = Zombie("localhost", 5022, "condor2")

    d_zombie = Zombie("localhost", 5016, "test")

    # c_zombie = Zombie("localhost", 5017, "zombie_b")

    while not done:
        # Get input on which zombies to use
        handler = OpenSocketHandler()
        # print("handle!")
        handler.check_on_open_ports({
            "bill": a_zombie,
            "ned": b_zombie,
            "ted": c_zombie,
            "test": d_zombie
        })


main()
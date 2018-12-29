#!/bin/env/python

import os
import sys
import getpass
import json
import paramiko
import pprint
from collections import OrderedDict

out = OrderedDict()
reserved_words = ["_when", "_env", "_if", "_source", "_includes"]


def load_configuration(configuration):
    return json.loads(configuration)
    pass


def run_configuration(client, configuration):
    for key, value in configuration.items():
        if (len(configuration[key]) > 0):
            check = 0
            notcheck = -1
            if ("_if" in configuration[key]):
                check =  check_command(client, configuration[key]["_if"])
            if ("_ifnot" in configuration[key]):
                notcheck =  check_command(client, configuration[key]["_ifnot"])

            if (check == 0 and notcheck != 0):
                out[key] = OrderedDict()
                for inkey, invalue in configuration[key].items():
                        if (inkey.find("_")):
                            out[key][inkey] = run_command(client, invalue)


def get_connection(server, user, passwd, *args, **kwargs):
    client = paramiko.SSHClient()
    #client.set_missing_host_key_policy(False)
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(server, username=user, password=passwd)
    return client
    pass


def run_command(client, command):
    stdin, stdout, stderr = client.exec_command(command)
    str_out = ""
    if (stdout  != ""):
        for line in stdout:
            str_out += line
    elif (stderr != ""):
        for line in stderr:
            str_out += line
    return ' '.join(str_out.split())

def check_command(client, command):
    stdin, stdout, stderr = client.exec_command(command)
    return stdout.channel.recv_exit_status()



def main(argv):
    server = argv[1]
    user = argv[2]
    passwd = argv[3]
    configuration = argv[4]
    client = get_connection(server, user, passwd)
    jstring = ""
    with open(argv[4]) as finput:
        for line in finput:
            jstring += line
    json_object = load_configuration(jstring)
    run_configuration(client, json_object)
    print("\nOrderedDict:\n")
    pprint.pprint(out)
    print("\nJSON String\n")
    print(json.dumps(out))
    pass


if __name__ == "__main__":
    main(sys.argv)

import sys
import os
import subprocess
import json
from application import application

class SSH_controller():
    def __init__(self, service, key, username, cb_username=None, cb_pw=None):
        self.service = service
        self.key = key
        self.username = username
        self.node = None
        self.bucket = None
        self.cb_username = cb_username
        self.cb_pw = cb_pw
        self.ssh = None
        self.command = None
        self.ssh_host = None

    def get_connection(self, node = None, bucket = None, path=None, ssh_host=None):
        self.node = node
        self.bucket = bucket
        self.path = path
        self.ssh_host = ssh_host

        if self.service == "cbstats":
            self.command = " ".join([self.path,
                        '{}:11210'.format(self.node),
                        '-u', self.cb_username,
                        '-p', self.cb_pw,
                        '-b', bucket,
                        '-j',
                        'all'])
            if self.ssh_host is None:
                self.ssh_host = self.node
            if application.config['CB_EXPORTER_MODE'] == "local":
                if path is None:
                    path = "/opt/couchbase/bin/cbstats"
                self.ssh = subprocess.Popen([self.command],
                                            shell=False,
                                            stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE)
                self.result = self.ssh.stdout.readlines()
                self.error = self.ssh.stderr.readlines()
            else:
                self.ssh = subprocess.Popen(["ssh", "-i", self.key, "-o", "StrictHostKeyChecking=no",
                                                "-o", "PasswordAuthentication=no",
                                                "{}@{}".format(self.username,
                                                                self.ssh_host),
                                                self.command],
                                            shell=False,
                                            stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE)
                self.result = self.ssh.stdout.readlines()
                self.error = self.ssh.stderr.readlines()
            if self.result == []:
                print("{} had an error: {}".format(self.node, self.error))
            else:
                try:
                    # python 3
                    self.result = json.loads("".join([str(i, 'utf-8') for i in self.result]))
                except:
                    # python 2
                    self.result = json.loads("".join([i.encode("utf-8") for i in self.result]))

            return self.result
        if self.service == "mctimings":
            self.command = " ".join([self.path,
                        '-h', '{}:11210'.format(self.node),
                        '-u', self.cb_username,
                        '-P', self.cb_pw,
                        '-b', bucket,
                        '-j'])

            if self.ssh_host is None:
                self.ssh_host = self.node
            self.ssh = subprocess.Popen(["ssh", "-i", self.key, "-o", "StrictHostKeyChecking=no",
                                            "-o", "PasswordAuthentication=no",
                                            "{}@{}".format(self.username,
                                                            self.ssh_host),
                                            self.command],
                                        shell=False,
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE)
            self.result = self.ssh.stdout.readlines()
            self.error = self.ssh.stderr.readlines()
            if self.result == []:
                print("{} had an error: {}".format(self.node, self.error))
                return ""
            else:
                try:
                    # python 3
                    self.result = "".join([str(i, 'utf-8') for i in self.result])
                except:
                    # python 2
                    self.result = "".join([i.encode("utf-8") for i in self.result])

                return self.result

if __name__ == '__main__':
    jim = SSH_controller("mctimings", "~/.ssh/tdenton", "vagrant", "Administrator", "password")
    print(jim.get_connection("10.112.194.101", "IdentityStore", "/opt/couchbase/bin/mctimings"))

#!/usr/bin/env python

from argparse import ArgumentParser
from ConfigParser import RawConfigParser
from subprocess import Popen
from os import kill, getpgid, environ, makedirs, remove
from os.path import join, exists
from tempfile import gettempdir
from signal import SIGKILL


class DB(object):
    def __init__(self):
        self.config = RawConfigParser()
        self.config.read(join(environ['HOME'], '.config', 'tunnels.cfg'))
        self.tempdir = join(gettempdir(), 'tunnels')
        if not exists(self.tempdir):
            makedirs(self.tempdir)

    def start(self, idd):
        pid = self.status(idd, False)
        if pid is not None and pid >= 0:
            print("Daemon {} already running {}".format(idd, pid))
        elif not self.config.has_section(idd):
            print("Unknown daemon {}".format(idd))
        else:
            data = dict(self.config.items(idd))
            pid = Popen(['/usr/bin/ssh', '-o', 'Controlmaster no', '-ND', data['port'], data['target']]).pid
            with open(join(self.tempdir, idd), 'w') as fic:
                fic.write(str(pid))
            print("Daemon {} started with pid {}".format(idd, pid))

    def stop(self, idd):
        pid = self.status(idd, False)
        if pid is None or pid < 0:
            print("Daemon {} not running".format(idd))
        else:
            print("Killing daemon {} ({})".format(idd, pid))
            kill(pid, SIGKILL)
            remove(join(self.tempdir, idd))

    def status(self, idd, direct=True):
        try:
            pid = -1
            with open(join(self.tempdir, idd), 'r') as fic:
                pid = fic.readline().strip()
        except IOError:
            if direct:
                print("Daemon {} not running".format(idd))
            return None
        if pid.isdigit():
            pid = int(pid)
            try:
                getpgid(pid)
            except OSError:
                pid = -1
        if pid < 0:
            if direct:
                print("PID file found, but daemon {} not running, removing the file".format(idd))
            remove(join(self.tempdir, idd))
        elif direct:
            print("Daemon {} is running with pid {}".format(idd, pid))
        return pid

    def restart(self, idd):
        self.stop(idd)
        self.start(idd)

    def list(self):
        for idd in self.config.sections():
            self.status(idd)

    def do(self, action, idd):
        func = getattr(self, action)
        func(idd)


def main():
    parser = ArgumentParser(description='Tunnel SSH manager as daemon')
    subparsers = parser.add_subparsers(help='subcommands', dest='action')
    for action in ('start', 'restart', 'stop', 'status'):
        subsub = subparsers.add_parser(action)
        subsub.add_argument("id", help="Identifier of the daemon to handle")
    subparsers.add_parser('list')
    args = parser.parse_args()

    if args.action == "list":
        DB().list()
    else:
        DB().do(args.action, args.id)

if __name__ == "__main__":
    main()

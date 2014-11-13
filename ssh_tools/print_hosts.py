#!/usr/bin/env python

import paramiko
from colors import red, yellow
from os.path import exists, expanduser


if __name__ == "__main__":
    sshconf = paramiko.SSHConfig()
    if exists('/etc/ssh/ssh_config'):
        sshconf.parse(open('/etc/ssh/ssh_config', 'r'))
    local_config = expanduser('~/.ssh/config')
    if exists(local_config):
        sshconf.parse(open(local_config, 'r'))
    hosts = []
    for entry in sshconf.__dict__.get('_config'):
        if 'hostname' in entry['config']:
            for host in entry['host']:
                hosts.append(host)

    known_host = []
    known_alias = []
    for host in sorted(hosts):
        entry = sshconf.lookup(host)
        printed_alias = "{:<20}".format(host)
        printed_alias = red(printed_alias) if host in known_alias else printed_alias
        user = entry.get('user', '')
        base_host = entry['hostname'].split('-')[0]
        extend_host = '' if '-' not in entry['hostname'] else '-' + entry['hostname'].split('-')[1]
        printed_host = "{:>14}{:<22}".format(base_host, extend_host)
        printed_host = yellow(printed_host) if entry['hostname'] in known_host else printed_host
        known_host.append(entry['hostname'])
        known_alias.append(host)
        proxy_chain = []
        current_lookup = host
        while True:
            while 'proxycommand' not in entry and current_lookup != entry['hostname']:
                current_lookup = entry['hostname']
                entry = sshconf.lookup(current_lookup)
                break
            if 'proxycommand' in entry:
                proxy_chain.append(entry['proxycommand'].split(' ')[2])
                entry = sshconf.lookup(proxy_chain[-1])
            else:
                break
        proxy = "via  " + "-> ".join(proxy_chain[::-1]) if len(proxy_chain) > 0 else ''
        print("{} {:>13}@{} {}".format(printed_alias, user, printed_host, proxy))

#!/usr/bin/python

import urllib
import boto
import sys
import tempfile
import os
from optparse import OptionParser

EC2_CONN = boto.connect_ec2()
PUBLIC_IP_TEMP_FILE = os.path.join(tempfile.gettempdir(),"public_ip_address")

def get_arg_parser():
    parser = OptionParser()
    parser.add_option("-g","--group", dest="group", 
                      help="Security group that port modifications will be made on.")
    parser.add_option("-p","--port", dest="port", 
                      help="The port number to be opened for the current public IP address.  All other group allowances that specify this port will be removed.")
    return parser

def is_file_less_than_five_minutes_old(f):
    current_time = time.time()
    last_modified = os.path.getmtime(f)
    return current_time - last_modified < 300

def get_public_facing_ip():
    if os.path.exists(PUBLIC_IP_TEMP_FILE) or is_file_less_than_five_minutes_old(PUBLIC_IP_TEMP_FILE):
        with open(PUBLIC_IP_TEMP_FILE) as f:
            return f.readlines()[0].strip()
    else:    
        public_ip = urllib.urlopen("http://whatismyip.org").read()
        with open(PUBLIC_IP_TEMP_FILE,"w") as f:
            f.write(public_ip)
        return public_ip

def remove_all_rules_for_port(group,port):
    for rule in group.rules:
        if int(rule.from_port) == int(port) and int(rule.to_port) == int(port):
            for grant in rule.grants:
                EC2_CONN.revoke_security_group(group_name = group.name,
                                               ip_protocol="tcp",
                                               from_port = int(port),
                                               to_port = int(port),
                                               cidr_ip = grant)

def add_rule_for_port_and_pub_ip(group, ip, port):
    if "/" not in ip:
        cidr_ip = ip + "/32"
    else:
        cidr_ip = ip
    EC2_CONN.authorize_security_group(group_name = group.name, 
                                      ip_protocol="tcp",
                                      from_port=int(port),
                                      to_port=int(port),
                                      cidr_ip=cidr_ip)

if __name__ == "__main__":
    (options,args) = get_arg_parser().parse_args()
    options.port = options.port
    ip = get_public_facing_ip()
    groups = [group for group in EC2_CONN.get_all_security_groups() if options.group == group.name]
    for group in groups:
        remove_all_rules_for_port(group,options.port)
        add_rule_for_port_and_pub_ip(group,ip,options.port)
        print("Port %s opened for %s in group %s" % (options.port,ip,group.name))

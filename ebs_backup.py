#!/usr/bin/python

import boto
import sys
from optparse import OptionParser
from datetime import datetime

def get_arg_parser():
    parser = OptionParser()
    parser.add_option("-n","--name", dest="name_tag", 
        help="'Name' tag to be applied to snapshot.  Does not override 'Name'" +
        " from volume.  Must be supplied if 'Name' tag is not set on volume" +
        " being snapshotted")
    return parser

def generate_description(base_name=""):
    now = datetime.now()
    return base_name + "-" + str(now.year) + "." + str(now.month).zfill(2) + 
        "." + str(now.day).zfill(2) + "." + str(now.hour).zfill(2) + 
        str(now.minute).zfill(2)


if __name__ == "__main__":
    (options,args) = get_arg_parser().parse_args()
    volume_id = args[0] if len(args) > 0 else None
    if volume_id is None or "vol" not in volume_id.strip():
        raise Exception("Invalid argument for volume_id.  ' +
            "Please provide an argument of the volume_id to be snapshotted.")

    ec2 = boto.connect_ec2()

    #Determine if we need to set the name or not based on the target volume
    volumes = filter(
        lambda boto_volume: volume_id == boto_volume.id, ec2.get_all_volumes())
    volume = volumes[0] if len(volumes) > 0 else None
    if volume is None: 
        vraise Exception(volume_id + " not found in volumes for account")

    #Make sure a 'Name' tag gets created for the snapshot 
    name_tag = None
    if "Name"  in volume.tags:
        name_tag = volume.tags["Name"]
    else:
        name_tag = options.name_tag
        if name_tag is None:
            raise Exception("passed in volume must have a 'Name' tag " + 
                "or a name must be passed in with the --name option.")

    #Create snapshot with a description with the name datestamped 
    snapshot = ec2.create_snapshot(volume_id,generate_description(name_tag))

    #If the "Name" tag didn't exist in the volume, add it to the snapshot
    if "Name" not in snapshot.tags:
        snapshot.add_tag("Name",name_tag)
                                   
    #Trim all snapshots.  Modify arguments to this call to override defaults.
    ec2.trim_snapshots()

    print "Snapshot " + snapshot.id + " taken and all snapshots trimmed."

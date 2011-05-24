#!/usr/bin/python

import boto
import time
import sys
from datetime import datetime
from smtplib import SMTP

MAX_STATUS_CHECKS = 20

def generate_image_name(base_name=""):
    now = datetime.now()
    return base_name + "-" + str(now.year) + "." + str(now.month).zfill(2) + "." + str(now.day).zfill(2) + "." + str(now.hour).zfill(2) + str(now.minute).zfill(2)

instance_id = sys.argv[1]
base_name = sys.argv[2]
image_name = generate_image_name(base_name)

ec2 = boto.connect_ec2()
ami_id = ec2.create_image(instance_id=instance_id, name=image_name, no_reboot=True)
print "Started AMI creation of:  " + str(ami_id)

#Loop until state is 'available' or until threshold has elapsed
iterations = 0
while True:
    iterations = iterations + 1
    time.sleep(60) 
    image = ec2.get_image(ami_id)
    if image.state == "available":
        message = "Backup succeeded for " + instance_id
        break
    elif image.state == "pending" and iterations <= MAX_STATUS_CHECKS:
        continue
    else:
        message = "Backup failed for " + instance_id + " with state of " + image.state
        break

print message

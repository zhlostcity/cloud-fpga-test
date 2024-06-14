#
# Copyright (C) 2019
# Author: Shanquan Tian <shanquan.tian@yale.edu>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301  USA
#

import datetime
from subprocess import call
import time
import subprocess
import json
import urllib
from experiment_utilities import *
import threading

# The hard-coded IP addresses are internal IP addresses that AWS uses for metadata about
# the running instance:
# https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/instancedata-data-retrieval.html

url = 'http://169.254.169.254/latest/meta-data/instance-id/'
instanceId = urllib.urlopen(url).readlines()[0]
print ("\nInstance ID is %s \n" % instanceId)

url = 'http://169.254.169.254/latest/meta-data/instance-type/'
instanceType = urllib.urlopen(url).readlines()[0]
print ("Instance Type is %s \n" % instanceType)

url = 'http://169.254.169.254/latest/meta-data/placement/availability-zone/'
region_zone = urllib.urlopen(url).readlines()[0]
myRegion = region_zone[:-1]
print ("Region is %s , zone is %s \n" % (myRegion, region_zone))


cmd = 'aws --region '+myRegion+' ec2 describe-instances --instance-ids %s'%instanceId
p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,   stderr=subprocess.PIPE)
out, err = p.communicate()
out = json.loads(out)
ipAddress = str(out['Reservations'][0]['Instances'][0]['PublicIpAddress'])
ret = call(['make', 'clean'])
ret = call(['make', 'dram_dma'])

if __name__ == '__main__':
    # One cycle takes around 1.1935483871s,
    if (instanceType == "f1.2xlarge"):
        message = "DRAMPUFonNormalInstance_%s"%instanceType
        slot0 = threading.Thread(target=dramReadOnly, args=(0,instanceId,ipAddress,message))
        slot0.start()
        slot0.join()

    elif (instanceType == "f1.4xlarge"):
        message = "DRAMPUFonNormalInstance_%s"%instanceType
        slot0 = threading.Thread(target=dramReadOnly, args=(0,instanceId,ipAddress,message))
        slot1 = threading.Thread(target=dramReadOnly, args=(1,instanceId,ipAddress,message))
        slot0.start()
        slot0.join()
        slot1.start()
        slot1.join()
    elif (instanceType == "f1.16xlarge"):
        message = "DRAMPUFonNormalInstance_%s"%instanceType
        slot0 = threading.Thread(target=dramReadOnly, args=(0,instanceId,ipAddress,message))
        slot1 = threading.Thread(target=dramReadOnly, args=(1,instanceId,ipAddress,message))
        slot2 = threading.Thread(target=dramReadOnly, args=(2,instanceId,ipAddress,message))
        slot3 = threading.Thread(target=dramReadOnly, args=(3,instanceId,ipAddress,message))
        slot4 = threading.Thread(target=dramReadOnly, args=(4,instanceId,ipAddress,message))
        slot5 = threading.Thread(target=dramReadOnly, args=(5,instanceId,ipAddress,message))
        slot6 = threading.Thread(target=dramReadOnly, args=(6,instanceId,ipAddress,message))
        slot7 = threading.Thread(target=dramReadOnly, args=(7,instanceId,ipAddress,message))
        slot0.start()
        slot0.join()
        slot1.start()
        slot1.join()
        slot2.start()
        slot2.join()
        slot3.start()
        slot3.join()
        slot4.start()
        slot4.join()
        slot5.start()
        slot5.join()
        slot6.start()
        slot6.join()
        slot7.start()
        slot7.join()


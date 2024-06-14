#
# Copyright (C) 2019
# Authors: Shanquan Tian <shanquan.tian@yale.edu>
#          Wenjie Xiong <wenjie.xiong@yale.edu>
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

import struct
import subprocess
import sys
import os
import glob
from multiprocessing import Process
from multiprocessing import Pool
import datetime
import argparse
assert sys.version_info[:2] == (2,7)

def HW(n): 
    '''
    count of high bits 
    '''
    n = (n & 0x5555555555555555) + ((n & 0xAAAAAAAAAAAAAAAA) >> 1)
    n = (n & 0x3333333333333333) + ((n & 0xCCCCCCCCCCCCCCCC) >> 2)
    n = (n & 0x0F0F0F0F0F0F0F0F) + ((n & 0xF0F0F0F0F0F0F0F0) >> 4)
    n = (n & 0x00FF00FF00FF00FF) + ((n & 0xFF00FF00FF00FF00) >> 8)
    n = (n & 0x0000FFFF0000FFFF) + ((n & 0xFFFF0000FFFF0000) >> 16)
    n = (n & 0x00000000FFFFFFFF) + ((n & 0xFFFFFFFF00000000) >> 32)
    
    return n

def Jaccard_index (arg):
    ''' 
    Jaccard index between binary measurements
    '''
    # 512 KiB = 512*1024 bytes = 524288 bytes = 4194304 bits = 1048576 hex numbers = 131072 * 8 hex numbers
    PUFsize=1048576/16
    pattern=0xffffffffffffffff #PUF initial value
    (File0_name, File1_name)=arg
    # Open input file for reading
    F_t1 = open(File0_name, "rb")
    F_t2 = open(File1_name, "rb")
    
    union=0
    intersec=0
    hw1=0
    hw2=0
    
    b_t1 = F_t1.read()
    b_t2 = F_t2.read()

    for i in range(0, PUFsize):
        b_tmp_t1 = b_t1[i*8:(i+1)*8] # read 8 bytes = 16 hex numbers
        b_tmp_t2 = b_t2[i*8:(i+1)*8] # read 8 bytes = 16 hex numbers

        t1_data = struct.unpack("Q",b_tmp_t1)[0]
        t2_data = struct.unpack("Q",b_tmp_t2)[0]
    
        #hamming weight
        cmpdata = t1_data ^ pattern
        hw1+=HW(cmpdata)
        cmpdata = t2_data ^ pattern
        hw2+=HW(cmpdata)
        #intersection
        cmpdata = ((t1_data^pattern) & (t2_data^pattern)) 
        intersec+=HW(cmpdata)                
        #union
        cmpdata = ((t1_data^pattern) | (t2_data^pattern)) 
        union+=HW(cmpdata)
    
    try:
        F_t1.close()
        F_t2.close()
        return ( File0_name, File1_name, hw1, hw2, intersec, union, float(intersec)/float(union))
    except:
        F_t1.close()
        F_t2.close()
        return ( File0_name, File1_name, hw1, hw2, intersec, union, 999)

def errorRate (args):
    SIZE=1048576/16 #
    pattern=0xffffffffffffffff #PUF initial value
    No_threads=64 #Number of threads to be run in parallel
    datafile = args
    F_data = open(datafile, "rb")

    data = F_data.read()
    hw2 = 0
    for i in range (SIZE):
        t2_data = data[i*8:(i+1)*8]
        t2_data = struct.unpack("Q",t2_data)[0]
        if t2_data != pattern:
            cmpdata = t2_data ^ pattern
            tmpmask=1
            for j in range(0,64):
                if tmpmask & cmpdata:
                    hw2 +=1            
                tmpmask = tmpmask << 1
    F_data.close()
    return (datafile, hw2)

def readDRAMData (root, slot = 0): #slot = -1 means all slots
    DRAM_A = []
    DRAM_B = []
    DRAM_C = []
    DRAM_D = []
    startTime = []
    endTime = []
    if (slot != -1):
        differentDevices = glob.glob((root+"*slot%d*"%slot))
    elif (slot == -1):
        differentDevices = glob.glob((root+"i-*"))
    differentDevices.sort(key = lambda x: x.split('_')[-6] +'-'+ x.split('_')[-5])
    
    for i in range(len(differentDevices)):
        time = differentDevices[i].split('_')[-6] +'-'+ differentDevices[i].split('_')[-5]
        time = datetime.datetime.strptime(time, '%Y-%m-%d-%H-%M')
        startTime.append(time)
        device_Time = os.listdir(str(differentDevices[i]))
        for tmp in device_Time:
            if (tmp[0:2] == "12"):
                tmp2 = tmp
        device_120s = str(differentDevices[i]) + '/' + tmp2
        drams = os.listdir(device_120s)
        for tmp in drams:
            if(tmp[0] == 'A'):
                dram = device_120s + '/' + tmp
                DRAM_A.append(dram)
            elif (tmp[0] == 'B'):
                dram = device_120s + '/' + tmp
                DRAM_B.append(dram)
            elif (tmp[0] == 'C'):
                dram = device_120s + '/' + tmp
                DRAM_C.append(dram)
            elif (tmp[0] == 'D'):
                if (tmp != "D.dat"):
                    time = tmp[:-4].split('_')[1] +'-'+ tmp[:-4].split('_')[2]
                    time = datetime.datetime.strptime(time, '%Y-%m-%d-%H-%M')
                endTime.append(time)
                dram = device_120s + '/' + tmp
                DRAM_D.append(dram)
    return (differentDevices, DRAM_A, DRAM_B, DRAM_C, DRAM_D, startTime, endTime)


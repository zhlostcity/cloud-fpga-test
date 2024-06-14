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

import os
import datetime
import argparse
import glob
import struct
import math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from calc_utilities import *
from mpl_toolkits.axes_grid1 import make_axes_locatable, axes_size
from pylab import *
from matplotlib import font_manager

fontaxes = {
    'family': 'Arial',
        'color':  'black',
        'weight': 'bold',
        'size': 8,
}

def countDifference(data):
    pattern=0xf
    errorCount = 0
    cmpdata = int(data, 16) ^ pattern
    tmpmask=1
    for j in range(0,4):
        if tmpmask & cmpdata:
            errorCount +=1            
        tmpmask = tmpmask << 1
    return errorCount

def extractHexData(FileName):
    # 512 KiB = 512*1024 bytes = 524288 bytes = 4194304 bits = 1048576 hex numbers = 1024*1024
    #         = 131072 * 8 hex numbers
    # The unit of data storage is byte
    ####### defines
    pattern=0xffffffffffffffff
    #############
    print errorRate(FileName)
    with open (FileName, "rb") as file:
        data = file.read()
    dim = int(math.sqrt(len(data)*2))
    plot_data = []
    plot_data_01 = []
    count = 0
    for i in range (dim):
        data_line = []
        data_line_01 = []
        for j in range(dim/16):
            tmp_data = data[count*8:(count+1)*8]
            tmp_data = struct.unpack("Q",tmp_data)[0]
            count = count + 1
            str_data = "%x"%tmp_data
            for c in str_data:
                data_line.append(countDifference(c))
                if (c == 'f'):
                    data_line_01.append(0)
                else:
                    data_line_01.append(1)
        plot_data.append(data_line)
        plot_data_01.append(data_line_01)
    return plot_data, plot_data_01, dim

def plot_whole_and_part (FileName):
    data, plot_data_01, dim = extractHexData(FileName)
    plot_data = plot_data_01
    fig, [ax0, ax1] = plt.subplots(1, 2, figsize=(3.5,2), dpi=300, facecolor='w')
    im = ax0.imshow(plot_data_01, cmap='Greys')
    rect = patches.Rectangle((700, 500), 128, 128, linewidth = 1, edgecolor='#29a329', facecolor='none')
    ax0.add_patch(rect)
    ax0.set_xticks(range(0, dim + 1 , 256))
    ax0.set_yticks(range(0, dim + 1 , 256))
    ax0.tick_params(axis='both', which='major', labelsize=7)
    ax0.tick_params(top=True, bottom=False, labeltop=True, labelbottom=False)
    
    dim = 128
    plot_data = []
    for i in range(dim):
        if (i % 2 == 1):
            for j in range(dim/2):
                lineData[j] = lineData[j] + data[600+i][500+j] + data[600+i][500+j+1]
            plot_data.append(lineData)
        else:
            lineData = []
            for j in range(dim/2):
                lineData.append(data[600+i][500+j] + data[600+i][500+j+1])
    plot_data[0][0] = 4
    dim = 128/2
    cmap = cm.get_cmap('Greys', 5)
    im = ax1.imshow(plot_data, cmap=cmap)

    pad_fraction = 2
    divider = make_axes_locatable(ax1)
    width = axes_size.AxesY(ax1, aspect=1./100)
    pad = axes_size.Fraction(pad_fraction, width)
    cax = divider.append_axes("right", size=width+0.03, pad=pad)
    cbar = plt.colorbar(im, cax=cax, ticks=range(5))
    
    cbar.ax.set_ylabel("Number of Bit Flips", rotation=-90, va="bottom",fontdict = fontaxes)
    cbar.ax.tick_params(axis='both', which='major', labelsize=7)

    ax1.set_xticks(range(0, dim + 1 , 16))
    ax1.set_yticks(range(0, dim + 1 , 16))
    ax1.tick_params(axis='both', which='major', labelsize=7)
    ax1.tick_params(top=True, bottom=False, labeltop=True, labelbottom=False)
    ax1.set_xlabel("Column",fontdict = fontaxes)
    ax0.set_ylabel("Row",fontdict = fontaxes, labelpad=-2)
    ax0.set_xlabel("Column",fontdict = fontaxes)
    plt.savefig("bitmap_whole_and_part.png", bbox_inches='tight')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="python plot_bitmap.py -d YourPath/i-0d7ef696b690b7171_XXX_slot1_DRAMPUFonSpotInstance_f1.4xlarge/120s_XXX/D_XXX.dat", formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-d", "--dat", required=True, type=str, help='Path to the data file, eg: DRAM***.dat')
    args = parser.parse_args()

    plot_whole_and_part(args.dat)


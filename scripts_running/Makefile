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


INCLUDES = -I$(SDK_DIR)/userspace/include
CFLAGS = -DCONFIG_LOGLEVEL=4 -std=gnu99 -g -w $(INCLUDES)
LDLIBS = -lfpga_mgmt -lrt -lpthread
SRC = common_dma.c test_dram_dma.c 
OBJ = $(SRC:.c=.o)

dram_dma: $(OBJ)
	gcc $(CFLAGS) -o test_dram_dma $^ $(LDFLAGS) $(LDLIBS)

experiment: experiment.py
	python experiment.py

remote_experiment: remote_experiment.py
	python remote_experiment.py

install_sshpass:
	sudo yum -y install sshpass

clean:
	rm -f *.o test_dram_dma *.pyc
	rm -rf *.csv specification*.json



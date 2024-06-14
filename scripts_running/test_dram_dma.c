// Amazon FPGA Hardware Development Kit
//
// Copyright 2016 Amazon.com, Inc. or its affiliates. All Rights Reserved.
//
// Licensed under the Amazon Software License (the "License"). You may not use
// this file except in compliance with the License. A copy of the License is
// located at
//
//    http://aws.amazon.com/asl/
//
// or in the "license" file accompanying this file. This file is distributed on
// an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, express or
// implied. See the License for the specific language governing permissions and
// limitations under the License.

#include <stdio.h>
#include <fcntl.h>
#include <errno.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
#include <poll.h>

#include "common_dma.h"

#define MEM_16G     (1ULL << 34)
#define USER_INTERRUPTS_MAX  (16)
#define WRITE_READ_COUNT 131072 // 8192 = 2^13 packets = 2^13*8*4 bits = 32 KiB  16384 = 64 KiB
// 131072 = 512 KiB

#ifndef SV_TEST
/* use the stdout logger */
const struct logger *logger = &logger_stdout;
#endif

int main(int argc, char **argv) {
    int rc;
    int slot_id = 0;
    int choice = 0;

    switch (argc) {
    case 1:
        break;
    case 2:
        sscanf(argv[1], "%d", &choice);
        //choice = 1;// write
        //choice = 2;// read
        break;
    case 3:
        sscanf(argv[1], "%d", &choice);
        sscanf(argv[2], "%x", &slot_id);
        break;
    default:
        usage(argv[0]);
        return 1;
    }

    error_count = 0;

    /* setup logging to print to stdout */
    rc = log_init("test_dram_dma");
    fail_on(rc, out, "Unable to initialize the log.");
    rc = log_attach(logger, NULL, 0);
    fail_on(rc, out, "%s", "Unable to attach to the log.");

    /* initialize the fpga_plat library */
    rc = fpga_mgmt_init();
    fail_on(rc, out, "Unable to initialize the fpga_mgmt library");

    if (choice == 1){      //write
        rc = axi_mstr_write(slot_id);
        fail_on(rc, out, "AXI Master example failed");
    }
    else if (choice == 2){ //read
        rc = axi_mstr_read(slot_id);
        fail_on(rc, out, "AXI Master example failed");
    }
    else {
        printf("Please input your choice! (1 to write, 2 to read)\n");
    }

out:
    if (rc || (error_count > 0)) {
        printf("TEST FAILED \n");
        rc = (rc) ? rc : 1;
    }
    else {
        printf("TEST PASSED \n");
    }
    return rc;
}

int axi_mstr_write(int slot_id) {
    int rc; int i;
    pci_bar_handle_t pci_bar_handle = PCI_BAR_HANDLE_INIT;
    int pf_id = 0;
    int bar_id = 0;
    int fpga_attach_flags = 0;
    uint32_t ddr_hi_addr, ddr_lo_addr, ddr_data;

    rc = fpga_pci_attach(slot_id, pf_id, bar_id, fpga_attach_flags, &pci_bar_handle);
    fail_on(rc, out, "Unable to attach to the AFI on slot id %d", slot_id);

    printf("Starting AXI Master to DDR test \n");

    // DDR A Access 
    ddr_hi_addr = 0x00000001;
    ddr_lo_addr = 0x10000000;
    ddr_data    = 0xFFFFFFFF;

    for(i = 0; i < WRITE_READ_COUNT; i++){
        rc = axi_mstr_ddr_write(slot_id, pci_bar_handle, ddr_hi_addr, ddr_lo_addr, ddr_data);
        fail_on(rc, out, "Unable to access DDR A.");
        ddr_lo_addr = ddr_lo_addr + 64;
    }
    printf("Successfully write data %x to high address %x, %d KiB at slot %d. \n", ddr_data,  ddr_hi_addr, 4*WRITE_READ_COUNT/1024, slot_id);

    //DDR B Access 
    ddr_hi_addr = 0x00000004;
    ddr_lo_addr = 0x10000000;
    ddr_data    = 0xFFFFFFFF;

    for(i = 0; i < WRITE_READ_COUNT; i++){
        rc = axi_mstr_ddr_write(slot_id, pci_bar_handle, ddr_hi_addr, ddr_lo_addr, ddr_data);
        fail_on(rc, out, "Unable to access DDR B.");
        ddr_lo_addr = ddr_lo_addr + 64;
    }
    printf("Successfully write data %x to high address %x, %d KiB at slot %d. \n", ddr_data,  ddr_hi_addr, 4*WRITE_READ_COUNT/1024, slot_id);

    //DDR C Access 
    ddr_hi_addr = 0x00000008;
    ddr_lo_addr = 0x10000000;
    ddr_data    = 0xFFFFFFFF;

    for(i = 0; i < WRITE_READ_COUNT; i++){
        rc = axi_mstr_ddr_write(slot_id, pci_bar_handle, ddr_hi_addr, ddr_lo_addr, ddr_data);
        fail_on(rc, out, "Unable to access DDR C.");
        ddr_lo_addr = ddr_lo_addr + 64;
    }
    printf("Successfully write data %x to high address %x, %d KiB at slot %d. \n", ddr_data,  ddr_hi_addr, 4*WRITE_READ_COUNT/1024, slot_id);

    //DDR D Access 
    ddr_hi_addr = 0x0000000C;
    ddr_lo_addr = 0x10000000;
    ddr_data    = 0xFFFFFFFF;

    for(i = 0; i < WRITE_READ_COUNT; i++){
        rc = axi_mstr_ddr_write(slot_id, pci_bar_handle, ddr_hi_addr, ddr_lo_addr, ddr_data);
        fail_on(rc, out, "Unable to access DDR D.");
        ddr_lo_addr = ddr_lo_addr + 64;
    }
    printf("Successfully write data %x to high address %x, %d KiB at slot %d. \n", ddr_data,  ddr_hi_addr, 4*WRITE_READ_COUNT/1024, slot_id);

out:
    return rc;
}


/* Helper function for accessing DDR controllers via AXI Master block */
int axi_mstr_ddr_write(int slot_id, pci_bar_handle_t pci_bar_handle, uint32_t ddr_hi_addr, uint32_t ddr_lo_addr, uint32_t  ddr_data) {
    int rc;
    static uint32_t ccr_offset  = 0x500;
    static uint32_t cahr_offset = 0x504;
    static uint32_t calr_offset = 0x508;
    static uint32_t cwdr_offset = 0x50C;
    static uint32_t crdr_offset = 0x510;
    uint32_t read_data;
    int poll_limit = 20;

    /* Issue AXI Master Write Command */
    rc = fpga_pci_poke(pci_bar_handle, cahr_offset, ddr_hi_addr);
    fail_on(rc, out, "Unable to write to AXI Master CAHR register!");
    rc = fpga_pci_poke(pci_bar_handle, calr_offset, ddr_lo_addr);
    fail_on(rc, out, "Unable to write to AXI Master CALR register!");
    rc = fpga_pci_poke(pci_bar_handle, cwdr_offset, ddr_data);
    fail_on(rc, out, "Unable to write to AXI Master CWDR register!");
    rc = fpga_pci_poke(pci_bar_handle, ccr_offset, 0x1);// to write
    fail_on(rc, out, "Unable to write to AXI Master CCR register!");

    /* Poll for done */
    do{
        // Read the CCR until the done bit is set
        rc = fpga_pci_peek(pci_bar_handle, ccr_offset, &read_data);
        fail_on(rc, out, "Unable to read AXI Master CCR from the fpga !");
        read_data = read_data & (0x2);
        poll_limit--;
    } while (!read_data && poll_limit > 0);
    fail_on((rc = !read_data), out, "AXI Master write to DDR did not complete. Done bit not set in CCR.");

out:
    return rc;
}


int axi_mstr_read(int slot_id) {
    int rc; int i;
    pci_bar_handle_t pci_bar_handle = PCI_BAR_HANDLE_INIT;
    int pf_id = 0;
    int bar_id = 0;
    int fpga_attach_flags = 0;
    uint32_t ddr_hi_addr, ddr_lo_addr;

    rc = fpga_pci_attach(slot_id, pf_id, bar_id, fpga_attach_flags, &pci_bar_handle);
    fail_on(rc, out, "Unable to attach to the AFI on slot id %d", slot_id);

    //DDR A Access 
    ddr_hi_addr = 0x00000001;
    ddr_lo_addr = 0x10000000;

    printf("DDR A\n");
    for (i = 0; i < WRITE_READ_COUNT; i++){
        rc = axi_mstr_ddr_read(slot_id, pci_bar_handle, ddr_hi_addr, ddr_lo_addr);
        fail_on(rc, out, "Unable to access DDR A.");
        ddr_lo_addr = ddr_lo_addr + 64;
    }

    //DDR B Access 
    ddr_hi_addr = 0x00000004;
    ddr_lo_addr = 0x10000000;
    printf("DDR B\n");
    for (i = 0; i < WRITE_READ_COUNT; i++){
        rc = axi_mstr_ddr_read(slot_id, pci_bar_handle, ddr_hi_addr, ddr_lo_addr);
        fail_on(rc, out, "Unable to access DDR B.");
        ddr_lo_addr = ddr_lo_addr + 64;
    }

    //DDR C Access 
    ddr_hi_addr = 0x00000008;
    ddr_lo_addr = 0x10000000;
    printf("DDR C\n");
    for (i = 0; i < WRITE_READ_COUNT; i++){
        rc = axi_mstr_ddr_read(slot_id, pci_bar_handle, ddr_hi_addr, ddr_lo_addr);
        fail_on(rc, out, "Unable to access DDR C.");
        ddr_lo_addr = ddr_lo_addr + 64;
    }

    //DDR D Access 
    ddr_hi_addr = 0x0000000C;
    ddr_lo_addr = 0x10000000;
    printf("DDR D\n");
    for (i = 0; i < WRITE_READ_COUNT; i++){
        rc = axi_mstr_ddr_read(slot_id, pci_bar_handle, ddr_hi_addr, ddr_lo_addr);
        fail_on(rc, out, "Unable to access DDR D.");
        ddr_lo_addr = ddr_lo_addr + 64;
    }


out:
    return rc;
}

/* Helper function for accessing DDR controllers via AXI Master block */
int axi_mstr_ddr_read(int slot_id, pci_bar_handle_t pci_bar_handle, uint32_t ddr_hi_addr, uint32_t ddr_lo_addr ) {
    int rc;
    static uint32_t ccr_offset  = 0x500;
    static uint32_t cahr_offset = 0x504;
    static uint32_t calr_offset = 0x508;
    static uint32_t cwdr_offset = 0x50C;
    static uint32_t crdr_offset = 0x510;
    uint32_t read_data;
    int poll_limit = 20;

    /* Issue AXI Master Write Command */
    rc = fpga_pci_poke(pci_bar_handle, cahr_offset, ddr_hi_addr);
    fail_on(rc, out, "Unable to write to AXI Master CAHR register!");
    rc = fpga_pci_poke(pci_bar_handle, calr_offset, ddr_lo_addr);
    fail_on(rc, out, "Unable to write to AXI Master CALR register!");
    
    /* Issue AXI Master Read Command */
    rc = fpga_pci_poke(pci_bar_handle, ccr_offset, 0x5);
    fail_on(rc, out, "Unable to write to AXI Master CCR register!");

    /* Poll for done */
    poll_limit = 20;
    do{
        // Read the CCR until the done bit is set
        rc = fpga_pci_peek(pci_bar_handle, ccr_offset, &read_data);
        fail_on(rc, out, "Unable to read AXI Master CCR from the fpga !");
        read_data = read_data & (0x2);
        poll_limit--;
    } while (!read_data && poll_limit > 0);
    fail_on((rc = !read_data), out, "AXI Master read from DDR did not complete. Done bit not set in CCR.");

    /* Compare Read/Write Data */
    // Read the CRDR for read data
    rc = fpga_pci_peek(pci_bar_handle, crdr_offset, &read_data);
    fail_on(rc, out, "Unable to read AXI Master CRDR from the fpga !");

    printf("%08x\n", read_data);

out:
    return rc;
}


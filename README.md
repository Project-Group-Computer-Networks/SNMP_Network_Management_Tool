# CSN-341 : Mini-Project - Group 6

# Network Management Tool with SNMP

This is a network management tool developed by our team Error_404 that uses **SNMP (Simple Network Management Protocol)** to monitor various devices present in the network.It offers an efficient way to track and manage device performance, real-time status, and alerts in network environments like data centers, office setups, and more.

## Features

- Device Status Tracking
- Receiving Real-Time Alerts
- Assessing Performance Metrics
- Ability to Send SNMP traps

## Tech Stack

- Python for SNMP communication and data processing.
- matplotlib for data visualization.

## Libraries Used 

### Python Libraries
- pysnmp: For SNMP communication (snmpget, snmpset, snmptrap).
- asyncio: For asynchronous SNMP requests and handling
- matplotlib: For plotting graphs and visualizing the received data.

## Installation
- Clone this from Github
- Follow this helpful article to setup a targeted device to allow remote managers to access its data: https://help.domotz.com/tips-tricks/how-to-enable-snmp-on-linux-machines/
- Add the line view all included .1 in the snmpd.conf file
- Ensure that the snmpd.conf file of the targeted device has a line rwcommunity private <ip of manager> to give permission to the manager to access and set the device name.

## Usage
### For Manager
-All you need to do is run the snmpManager.py as follows in the terminal: python snmp_manager.py <device_ip_1> <name_1> <device_ip_2> <name_2> ...
  This will SET the System name of device with ip1 as name_1 and so on..
-All the data received from various devices is now found in device_info_<ip>.csv
-Later run the graph.py file and it will graphically depict all the data recieved from polled devices. 

### For SNMP Trap Receiver
- Simply run the trap_receiver.py file in the terminal. All the traps will be displayed in outputlog.txt.

## Video Demo(to change)

## Made with ❤️ by Error_404



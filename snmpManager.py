import asyncio
import sys
from pysnmp.hlapi.v3arch.asyncio import *
from pysnmp.entity import engine, config
from pysnmp.carrier.asyncio.dgram import udp
from pysnmp.entity.rfc3413 import ntfrcv
import csv
from datetime import datetime, timedelta
import logging

# SNMP Manager OID Map
oid_map = {
    "System name":'.1.3.6.1.2.1.1.5.0',
    "System Description": '.1.3.6.1.2.1.1.1.0',
    "System Location": '.1.3.6.1.2.1.1.6.0',
    "Wifi incoming packets": '.1.3.6.1.2.1.2.2.1.10.3',
    "Ethernet incoming packets": '.1.3.6.1.2.1.2.2.1.10.2',
    "Wifi outgoing packets": '.1.3.6.1.2.1.2.2.1.16.3',
    "Ethernet outgoing packets": '.1.3.6.1.2.1.2.2.1.16.2',
    "Wifi inbound errors": '.1.3.6.1.2.1.2.2.1.14.3',
    "Ethernet inbound errors": '.1.3.6.1.2.1.2.2.1.14.2',
    "Wifi outbound errors": '.1.3.6.1.2.1.2.2.1.20.3',
    "Ethernet outbound errors": '.1.3.6.1.2.1.2.2.1.20.2',
    'System Uptime': '.1.3.6.1.2.1.25.1.1.0',
    'Number of Processes': '.1.3.6.1.2.1.25.1.6.0',
    'CPU 1 Utilisation': '.1.3.6.1.2.1.25.3.3.1.2.196608',
    'CPU 2 Utilisation': '.1.3.6.1.2.1.25.3.3.1.2.196609',
    'Total Memory Size': '.1.3.6.1.2.1.25.2.2.0',
    'Memory used': '.1.3.6.1.2.1.25.2.3.1.6.1'
}


async def set_snmp_value(target, community, oid, value):
    errorIndication, errorStatus, errorIndex, varBinds = await setCmd(
        SnmpEngine(),
        CommunityData(community, mpModel=1),  # v2c
        await UdpTransportTarget.create(((target, 161))),
        ContextData(),
        ObjectType(ObjectIdentity(oid), value))

    if errorIndication:
        print(errorIndication)
    elif errorStatus:
        print(f'{errorStatus.prettyPrint()} at {errorIndex and varBinds[int(errorIndex)-1][0] or "?"}')
    else:
        for varBind in varBinds:
            print(f'Success: {varBind}')
# Function to get device info via SNMP
async def get_device_info(ip, community_string='public'):
    """Get system information from the device using SNMP asynchronously."""
    try:
        oids = [ObjectType(ObjectIdentity(oid)) for oid in oid_map.values()]

        # Initiate an asynchronous SNMP GET command
        errorIndication, errorStatus, errorIndex, varBinds = await getCmd(
            SnmpEngine(),
            CommunityData(community_string, mpModel=1),
            await UdpTransportTarget.create((ip, 161)),
            ContextData(),
            *oids
        )

        if errorIndication:
            print(f"Error: {errorIndication}")
            return None
        elif errorStatus:
            print(f"Error Status: {errorStatus.prettyPrint()}")
            return None
        else:
            result = {'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            for varBind in varBinds:
                oid, value = varBind
                for key, val in oid_map.items():
                    if val == "." + str(oid):
                        result[key] = value.prettyPrint()
            return result
    except Exception as e:
        print(f"Error checking device {ip}: {e}")
        return None

# Function to log data for a specific device
async def log_device_info(ip, interval=5, duration=180, csv_file_prefix='device_info'):
    """Fetch device information for a fixed duration and log it into a CSV file."""
    start_time = datetime.now()
    end_time = start_time + timedelta(seconds=duration)
    csv_file = f'{csv_file_prefix}_{ip}.csv'

    with open(csv_file, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['Timestamp'] + list(oid_map.keys()))
        writer.writeheader()

        while datetime.now() < end_time:
            info = await get_device_info(ip)
            if info:
                writer.writerow(info)
                file.flush()
            await asyncio.sleep(interval)

async def main():

    if len(sys.argv) < 2:
        print("Usage: python snmp_manager.py <device_ip_1> <name_1> <device_ip_2> <name_2> ...")
        sys.exit(1)

    device_map = {}  # Dictionary to store IP-address to name mapping

    # Process command-line arguments
    for i in range(1, len(sys.argv), 2):  # Step by 2 to get pairs of IP and name
        ip = sys.argv[i]
        if i + 1 < len(sys.argv):
            name = sys.argv[i + 1]
            device_map[ip] = name  # Map IP to name

    tasks = []
    for ip, name in device_map.items():
        await set_snmp_value(ip, 'private', '.1.3.6.1.2.1.1.5.0', OctetString(device_map[ip]))
        print(f"Setting up polling for {name} at {ip}")
        polling_task = asyncio.create_task(log_device_info(ip, duration=180))  # Polling for 3 minutes
        tasks.append(polling_task)

    # Run all tasks concurrently
    await asyncio.gather(*tasks)

# Run the event loop
if __name__ == '__main__':
    asyncio.run(main())

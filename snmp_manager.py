import asyncio
from pysnmp.hlapi.v3arch.asyncio import *

map={
    "System Description": '.1.3.6.1.2.1.1.1.0',
    "System Location": '.1.3.6.1.2.1.1.6.0',
    "Wifi incoming packets":'.1.3.6.1.2.1.2.2.1.10.3',
    "Ethernet incoming packets":'.1.3.6.1.2.1.2.2.1.10.2',
    "Wifi outgoing packets":'.1.3.6.1.2.1.2.2.1.16.3',
    "Ethernet outgoing packets":'.1.3.6.1.2.1.2.2.1.16.2',
    "Wifi inbound errors":'.1.3.6.1.2.1.2.2.1.14.3',
    "Ethernet inbound errors":'.1.3.6.1.2.1.2.2.1.14.2',
    "Wifi outbound errors":'.1.3.6.1.2.1.2.2.1.20.3',
    "Ethernet outbound errors":'.1.3.6.1.2.1.2.2.1.20.2',
    'System Uptime': '.1.3.6.1.2.1.25.1.1.0',
    'Number of Processes': '.1.3.6.1.2.1.25.1.6.0',
    'CPU 1 Utilisation': '.1.3.6.1.2.1.25.3.3.1.2.196608',
    'CPU 2 Utilisation': '.1.3.6.1.2.1.25.3.3.1.2.196609',
    'Total Memory Size': '.1.3.6.1.2.1.25.2.2.0',
    'Memory used': '.1.3.6.1.2.1.25.2.3.1.6.1'
}
async def get_device_info(ip, community_string='public'):
    """Get system information from the device using SNMP asynchronously."""
    try:
        # Define the OIDs to fetch
        oids = [
           #System Description
            ObjectType(ObjectIdentity(map["System Description"])),
            ObjectType(ObjectIdentity(map["System Location"])),
            
            #Packet information
            ObjectType(ObjectIdentity(map['Wifi incoming packets'])),
            ObjectType(ObjectIdentity(map['Ethernet incoming packets'])),
            ObjectType(ObjectIdentity(map['Wifi outgoing packets'])),
            ObjectType(ObjectIdentity(map['Ethernet outgoing packets'])),

            ObjectType(ObjectIdentity(map['Wifi inbound errors'])),
            ObjectType(ObjectIdentity(map['Ethernet inbound errors'])),

            ObjectType(ObjectIdentity(map['Wifi outbound errors'])),
            ObjectType(ObjectIdentity(map['Ethernet outbound errors'])),

            # hrSystem OIDs
            ObjectType(ObjectIdentity(map["System Uptime"])),  # hrSystemUptime
            ObjectType(ObjectIdentity(map['Number of Processes'])),  # hrSystemProcesses

            # hrProcessor OIDs
            ObjectType(ObjectIdentity(map['CPU 1 Utilisation'])),  # hrProcessorLoad for CPU1
            ObjectType(ObjectIdentity(map['CPU 2 Utilisation'])),  # hrProcessorLoad for CPU2

            ObjectType(ObjectIdentity(map['Total Memory Size'])),  # hrMemorySize
            ObjectType(ObjectIdentity(map['Memory used'])),  # hrStorageUsed (Disk1)
        ]

        # Initiate an asynchronous SNMP GET command
        errorIndication, errorStatus, errorIndex, varBinds = await getCmd(
            SnmpEngine(),
            CommunityData(community_string, mpModel=1),
            await UdpTransportTarget.create((ip, 161)),
            ContextData(),
            *oids
        )
        
        # Check for errors
        if errorIndication:
            print(f"Error: {errorIndication}")
            return False
        elif errorStatus:
            print(f"Error Status: {errorStatus.prettyPrint()}")
            return False
        else:
            # Process and print the information received from the SNMP device
            print(f"Device {ip} info:")
            for varBind in varBinds:
                oid, value = varBind
                # print(oid,value)
                for key, val in map.items():  # Use items() to get key-value pairs
                    if val == "."+str(oid):
                        print(f"{key}: {value.prettyPrint()}")
            return True
    except Exception as e:
        print(f"Error checking device {ip}: {e}")
        return False

# Test device status and fetch info
asyncio.run(get_device_info('10.81.70.216'))

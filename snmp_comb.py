import asyncio
from pysnmp.hlapi.v3arch.asyncio import *
from pysnmp.entity import engine, config
from pysnmp.carrier.asyncio.dgram import udp
from pysnmp.entity.rfc3413 import ntfrcv
import csv
from datetime import datetime
import logging

# SNMP Manager OID Map
map = {
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

# Logging for the trap receiver
logging.basicConfig(
    filename="received_traps.log",
    filemode="w",
    format="%(asctime)s - %(message)s",
    level=logging.INFO,
)

# SNMP Trap Receiver Settings
TrapAgentAddress = "localhost"
Port = 162

# SNMP Manager to poll device info
async def get_device_info(ip, community_string='public'):
    """Get system information from the device using SNMP asynchronously."""
    try:
        oids = [
            ObjectType(ObjectIdentity(map["System Description"])),
            ObjectType(ObjectIdentity(map["System Location"])),
            ObjectType(ObjectIdentity(map['Wifi incoming packets'])),
            ObjectType(ObjectIdentity(map['Ethernet incoming packets'])),
            ObjectType(ObjectIdentity(map['Wifi outgoing packets'])),
            ObjectType(ObjectIdentity(map['Ethernet outgoing packets'])),
            ObjectType(ObjectIdentity(map['Wifi inbound errors'])),
            ObjectType(ObjectIdentity(map['Ethernet inbound errors'])),
            ObjectType(ObjectIdentity(map['Wifi outbound errors'])),
            ObjectType(ObjectIdentity(map['Ethernet outbound errors'])),
            ObjectType(ObjectIdentity(map["System Uptime"])),
            ObjectType(ObjectIdentity(map['Number of Processes'])),
            ObjectType(ObjectIdentity(map['CPU 1 Utilisation'])),
            ObjectType(ObjectIdentity(map['CPU 2 Utilisation'])),
            ObjectType(ObjectIdentity(map['Total Memory Size'])),
            ObjectType(ObjectIdentity(map['Memory used']))
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
            return None
        elif errorStatus:
            print(f"Error Status: {errorStatus.prettyPrint()}")
            return None
        else:
            # Prepare a dictionary to store results
            result = {'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            for varBind in varBinds:
                oid, value = varBind
                for key, val in map.items():
                    if val == "." + str(oid):
                        result[key] = value.prettyPrint()
            return result
    except Exception as e:
        print(f"Error checking device {ip}: {e}")
        return None

async def log_device_info(ip, interval=5, csv_file='device_info.csv'):
    """Fetch device information at regular intervals and store it in a CSV file."""
    with open(csv_file, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['Timestamp'] + list(map.keys()))
        writer.writeheader()

        while True:
            info = await get_device_info(ip)
            if info:
                writer.writerow(info)
                file.flush()  # Ensure data is written to disk immediately
            await asyncio.sleep(interval)

# SNMP Trap Receiver function
def setup_trap_listener():
    snmpEngine = engine.SnmpEngine()

    logging.info(f"Agent is listening for SNMP Traps on {TrapAgentAddress}, Port: {Port}")
    print(f"Agent is listening for SNMP Traps on {TrapAgentAddress}, Port: {Port}")

    config.addTransport(
        snmpEngine,
        udp.DOMAIN_NAME + (1,),
        udp.UdpTransport().openServerMode((TrapAgentAddress, Port)),
    )

    # Configure community
    config.addV1System(snmpEngine, "my-area", "public")

    # Trap callback function
    def cbFun(snmpEngine, stateReference, contextEngineId, contextName, varBinds, cbCtx):
        print("Received new Trap message")
        logging.info("Received new Trap message")
        for name, val in varBinds:
            logging.info("%s = %s" % (name.prettyPrint(), val.prettyPrint()))
            print("%s = %s" % (name.prettyPrint(), val.prettyPrint()))

        logging.info("==== End of Incoming Trap ====")

    ntfrcv.NotificationReceiver(snmpEngine, cbFun)

    # Start trap listener
    snmpEngine.transportDispatcher.jobStarted(1)

    return snmpEngine

# Main function to run both tasks concurrently
async def main():
    # Setup the trap listener (runs in the background)
    snmpEngine = setup_trap_listener()

    # Run SNMP Manager (polling) in the main event loop
    device_polling = log_device_info('localhost')

    # Create a task for SNMP polling
    task_polling = asyncio.create_task(device_polling)

    try:
        await task_polling  # Wait for the polling task to complete (runs indefinitely)
    except asyncio.CancelledError:
        snmpEngine.transportDispatcher.closeDispatcher()  # Cleanup when cancelled

# Run the event loop
asyncio.run(main())

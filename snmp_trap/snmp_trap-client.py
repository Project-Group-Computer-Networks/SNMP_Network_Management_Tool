import asyncio
from pysnmp.hlapi.v3arch.asyncio import *

# Define the target server's IP and community string
server_ip = "localhost"
community_string = "public"

# SNMP trap version and security model
trap_engine = SnmpEngine()


# Trap target configuration (Trap Receiver)
async def send_snmp_trap():
    error_indication, error_status, error_index, var_binds = await sendNotification(
        trap_engine,
        CommunityData(community_string),
        await UdpTransportTarget.create((server_ip, 162)),  # Async function call
        ContextData(),
        "trap",
        NotificationType(
            ObjectIdentity("1.3.6.1.4.1.8072.2.3.0.1")  # OID for testing purposes
        ),
    )

    # Check for errors
    if error_indication:
        print(f"Error: {error_indication}")
    else:
        print("Trap sent successfully!")


# Run the async function using asyncio
asyncio.run(send_snmp_trap())

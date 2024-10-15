import asyncio
from pysnmp.hlapi.v3arch.asyncio import *

# Define the target server's IP and community string
server_ip = "10.81.77.121"
community_string = "public"

# SNMP trap version and security model
trap_engine = SnmpEngine()


# Trap target configuration (Trap Receiver)
async def send_snmp_trap():
    trap_oid = ObjectIdentity(".1.3.6.1.2.1.1.1.0")  # Example OID for testing
    value = OctetString("This is a test value")  # Example value to send

    # Define additional OID and value to send
    additional_oid = ObjectIdentity("1.3.6.1.4.1.8072.2.3.0.2")  # Additional OID
    additional_value = OctetString("Additional Test Value")  # Additional value

    error_indication, error_status, error_index, var_binds = await send_notification(
        trap_engine,
        CommunityData(community_string),
        await UdpTransportTarget.create((server_ip, 162)),  # Async function call
        ContextData(),
        "trap",
        NotificationType(trap_oid),  # Sending trap OID
        (trap_oid, value),  # Main OID with value
        (additional_oid, additional_value),
    )

    # Check for errors
    if error_indication:
        print(f"Error: {error_indication}")
    else:
        print("Trap sent successfully!")


# Run the async function using asyncio
asyncio.run(send_snmp_trap())
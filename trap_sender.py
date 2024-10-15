import asyncio
import psutil  # To monitor system memory, CPU, and temperature
from pysnmp.hlapi.v3arch.asyncio import *
from pysnmp.smi import *

# Define the target server's IP and community string
server_ip = "10.81.77.121"
community_string = "public"
trap_engine = SnmpEngine()

# Thresholds for memory usage (e.g., 80%), temperature (e.g., 70°C), and CPU usage (e.g., 80%)
MEMORY_THRESHOLD = 50.0
TEMPERATURE_THRESHOLD = 60.0  # Temperature threshold in °C
CPU_THRESHOLD = 10.0  # CPU usage threshold in %

# Function to monitor memory usage
def check_memory_usage():
    memory_info = psutil.virtual_memory()
    memory_percent_used = memory_info.percent
    return memory_percent_used

# Function to monitor CPU usage
def check_cpu_usage():
    cpu_percent_used = psutil.cpu_percent(interval=1)  # Get CPU usage over a 1-second interval
    return cpu_percent_used

# Function to monitor temperature (if supported by the system)
def check_temperature():
    temps = psutil.sensors_temperatures()
    if "coretemp" in temps:  # This may vary depending on the system
        core_temps = temps["coretemp"]
        for temp in core_temps:
            if temp.current > TEMPERATURE_THRESHOLD:
                return temp.current
    return None

# Trap target configuration (Trap Receiver)
async def send_snmp_trap(memory_percent=None, temperature=None, cpu_percent=None):
    if memory_percent:
        trap_oid = ObjectIdentity(".1.3.6.1.2.1.1.1.0")  # Example OID for memory
        value = OctetString(f"Memory usage exceeded: {memory_percent}%")  # Trap value
        additional_oid = ObjectIdentity("1.3.6.1.4.1.8072.2.3.0.2")  # Additional OID
        additional_value = OctetString("Additional memory alert")  # Additional value

    elif temperature:
        trap_oid = ObjectIdentity(".1.3.6.1.2.1.1.2.0")  # Example OID for temperature
        value = OctetString(f"Temperature exceeded: {temperature}°C")  # Trap value
        additional_oid = ObjectIdentity("1.3.6.1.4.1.8072.2.3.0.3")  # Additional OID for temperature
        additional_value = OctetString("Additional temperature alert")  # Additional value

    elif cpu_percent:
        trap_oid = ObjectIdentity(".1.3.6.1.2.1.1.3.0")  # Example OID for CPU
        value = OctetString(f"CPU usage exceeded: {cpu_percent}%")  # Trap value
        additional_oid = ObjectIdentity("1.3.6.1.4.1.8072.2.3.0.4")  # Additional OID for CPU
        additional_value = OctetString("Additional CPU alert")  # Additional value

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
        print(f"Trap sent successfully! {('Memory usage' if memory_percent else 'Temperature' if temperature else 'CPU usage')} exceeded!")

# Main function to check memory usage, CPU usage, temperature, and send traps if thresholds are exceeded
async def monitor_system_and_send_traps():
    while True:
        # Check memory usage
        memory_used = check_memory_usage()
        print(f"Memory usage: {memory_used}%")

        if memory_used > MEMORY_THRESHOLD:
            print(f"Memory threshold exceeded: {memory_used}%, sending SNMP trap...")
            await send_snmp_trap(memory_percent=memory_used)

        # Check CPU usage
        cpu_used = check_cpu_usage()
        print(f"CPU usage: {cpu_used}%")

        if cpu_used > CPU_THRESHOLD:
            print(f"CPU threshold exceeded: {cpu_used}%, sending SNMP trap...")
            await send_snmp_trap(cpu_percent=cpu_used)

        # Check temperature (if supported)
        temperature = check_temperature()
        if temperature:
            print(f"Temperature: {temperature}°C")

            if temperature > TEMPERATURE_THRESHOLD:
                print(f"Temperature threshold exceeded: {temperature}°C, sending SNMP trap...")
                await send_snmp_trap(temperature=temperature)

        # Wait for 10 seconds before checking again
        await asyncio.sleep(10)

# Run the async function using asyncio
asyncio.run(monitor_system_and_send_traps())

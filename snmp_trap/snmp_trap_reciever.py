# python snmp trap receiver
from pysnmp.entity import engine, config
from pysnmp.carrier.asyncio.dgram import udp
from pysnmp.entity.rfc3413 import ntfrcv
import logging

snmpEngine = engine.SnmpEngine()

TrapAgentAddress = "localhost"
# Trap listerner address
Port = 162
# trap listerner port

logging.basicConfig(
    filename="received_traps.log",
    filemode="w",
    format="%(asctime)s - %(message)s",
    level=logging.INFO,
)

logging.info(
    "Agent is listening SNMP Trap on " + TrapAgentAddress + " , Port : " + str(Port)
)
logging.info(
    "--------------------------------------------------------------------------"
)

print("Agent is listening SNMP Trap on " + TrapAgentAddress + " , Port : " + str(Port))

config.addTransport(
    snmpEngine,
    udp.DOMAIN_NAME + (1,),
    udp.UdpTransport().openServerMode((TrapAgentAddress, Port)),
)

# Configure community here
config.addV1System(snmpEngine, "my-area", "public")


def cbFun(snmpEngine, stateReference, contextEngineId, contextName, varBinds, cbCtx):
    print("Received new Trap message")
    logging.info("Received new Trap message")
    for name, val in varBinds:
        logging.info("%s = %s" % (name.prettyPrint(), val.prettyPrint()))
        print("%s = %s" % (name.prettyPrint(), val.prettyPrint()))

    logging.info("==== End of Incoming Trap ====")


ntfrcv.NotificationReceiver(snmpEngine, cbFun)

snmpEngine.transportDispatcher.jobStarted(1)

try:
    snmpEngine.transportDispatcher.runDispatcher()
except:
    snmpEngine.transportDispatcher.closeDispatcher()
    raise

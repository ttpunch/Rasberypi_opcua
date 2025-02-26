# opcua_server.py
import asyncio
import logging
from datetime import datetime
from math import sin
import time
from asyncua import Server, ua, uamethod
from asyncua.ua import SecurityPolicyType

# Set up logging
logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)

class SubHandler:
    """Subscription Handler for receiving events from server"""
    def datachange_notification(self, node, val, data):
        _logger.warning("Python: New data change event %s %s", node, val)

    def event_notification(self, event):
        _logger.warning("Python: New event %s", event)

@uamethod
def multiply(parent, x, y):
    _logger.warning("multiply method call with parameters: %s %s", x, y)
    return x * y

class MyUserManager:
    def __init__(self):
        self.user_db = {"admin": "admin123"}  # Username: Password database

    async def check_user_token(self, isession, username, password, user_token):
        if username in self.user_db and self.user_db[username] == password:
            return True
        return False

async def run_server():
    # Initialize the server
    server = Server()
    await server.init()
    server.set_endpoint("opc.tcp://0.0.0.0:4841/freeopcua/server/")
    server.set_server_name("Enhanced OPC UA Server")
    
    # Set up security policies
    server.set_security_policy([
        SecurityPolicyType.NoSecurity,
        SecurityPolicyType.Basic256Sha256_SignAndEncrypt,
        SecurityPolicyType.Basic256Sha256_Sign
    ])
    server.user_manager = MyUserManager()

    # Register namespace
    uri = "http://examples.freeopcua.github.io"
    idx = await server.register_namespace(uri)

    # Create device type
    dev_type = await server.nodes.base_object_type.add_object_type(idx, "MyDevice")
    await (await dev_type.add_variable(idx, "sensor1", 1.0)).set_modelling_rule(True)
    await (await dev_type.add_property(idx, "device_id", "0001")).set_modelling_rule(True)

    # Create objects and variables
    objects = server.nodes.objects
    myobj = await objects.add_object(idx, "MyObject")
    
    # Add variables with different types
    myvar = await myobj.add_variable(idx, "MyVariable", 6.7)
    await myvar.set_writable()
    
    mystringvar = await myobj.add_variable(idx, "MyStringVariable", "Example String")
    await mystringvar.set_writable()
    
    mydtvar = await myobj.add_variable(idx, "MyDateTimeVar", datetime.utcnow())
    await mydtvar.set_writable()
    
    myarrayvar = await myobj.add_variable(idx, "MyArrayVar", [1.0, 2.0, 3.0])
    await myarrayvar.set_writable()

    # Add method
    multiply_node = await myobj.add_method(
        idx,
        "multiply",
        multiply,
        [ua.VariantType.Int64, ua.VariantType.Int64],
        [ua.VariantType.Int64]
    )

    # Create event generator
    evgen = await server.get_event_generator()
    evgen.event.Severity = 300

    print("Server started at opc.tcp://localhost:4841/freeopcua/server/")
    async with server:
        # Set up subscription handler
        handler = SubHandler()
        sub = await server.create_subscription(500, handler)
        handle = await sub.subscribe_data_change(myvar)

        # Main server loop
        while True:
            # Update variable with sine wave
            await server.write_attribute_value(myvar.nodeid, ua.DataValue(sin(time.time())))
            # Trigger test event periodically
            await evgen.trigger(message="Periodic Event Update")
            await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(run_server())
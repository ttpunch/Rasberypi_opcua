from asyncua import ua

# Server configuration settings
SERVER_URL = "opc.tcp://0.0.0.0:4841"  # OPCUA server URL (accessible on the network)
NAMESPACE_URI = "http://example.com/opcua/server"  # Namespace URI from namespaces.py
VARIABLES = {
    "variable1": 0,  # Example counter or sensor value
    "variable2": "initial_state",  # Example string state
}

# Server settings
SERVER_CONFIG = {
    "name": "OPCUA Test Server",
    "uri": NAMESPACE_URI,
    "disable_clock": False,  # Enable server clock
    "certificate": None,  # Set to None for development
    "private_key": None,  # Set to None for development
    "user_manager": None,  # No authentication for development
    "security_policy": [ua.SecurityPolicyType.NoSecurity]  # Basic security policy for development
}

# Optional security settings (uncomment and configure as needed)
# SECURITY_POLICY = ua.SecurityPolicy.Basic256Sha256
# CERTIFICATE_PATH = "/path/to/certificate.pem"
# PRIVATE_KEY_PATH = "/path/to/private_key.pem"
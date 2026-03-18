import json
import os

class ServiceRegistry:
    """Persistent state management for Vanguard Nexus Microservices."""
    DATA_FILE = "system_state.json"

    @staticmethod
    def save_state(service_name, payload):
        state = {}
        if os.path.exists(ServiceRegistry.DATA_FILE):
            with open(ServiceRegistry.DATA_FILE, 'r') as f:
                try: state = json.load(f)
                except: state = {}
        state[service_name] = payload
        with open(ServiceRegistry.DATA_FILE, 'w') as f:
            json.dump(state, f, indent=4)

    @staticmethod
    def get_state(service_name):
        if not os.path.exists(ServiceRegistry.DATA_FILE): return None
        with open(ServiceRegistry.DATA_FILE, 'r') as f:
            return json.load(f).get(service_name)

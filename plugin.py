"""
<plugin key="Domoticz-E-Flux-Plugin" name="Domoticz E-Flux Plugin" author="Mark Heinis" version="0.0.1" wikilink="http://www.domoticz.com/wiki/plugins/plugin.html" externallink="https://github.com/galadril/Domoticz-E-Flux-Plugin">
    <description>
        Plugin for retrieving and updating EV Charger data from E-Flux backoffice.
    </description>
    <params>
        <param field="Username" label="Username" width="200px" required="false" default=""/>
        <param field="Password" label="Password" width="200px" required="false" default="" password="true"/>
        <param field="Mode6" label="Debug" width="200px">
            <options>
                <option label="None" value="0"  default="true" />
                <option label="Python Only" value="2"/>
                <option label="Basic Debugging" value="62"/>
                <option label="Basic+Messages" value="126"/>
                <option label="Connections Only" value="16"/>
                <option label="Connections+Queue" value="144"/>
                <option label="All" value="-1"/>
            </options>
        </param>
    </params>
</plugin>
"""

import Domoticz
import requests

class EFluxPlugin:
    def __init__(self):
        self.token = ""
        self.api_url = "http://api.e-flux.nl"
        self.debug_level = None

    def onStart(self):
        if Parameters["Mode6"] == "":
            Parameters["Mode6"] = "-1"
        if Parameters["Mode6"] != "0": 
            Domoticz.Debugging(int(Parameters["Mode6"]))
            DumpConfigToLog()
        
        self.debug_level = Parameters["Mode6"]
        
        self.createDevices()
        
        # Print Parameters for debugging
        Domoticz.Debug(f"Parameters: {Parameters}")
        
        self.login()
        Domoticz.Heartbeat(30)

    def login(self):
        login_url = f'{self.api_url}/1/auth/login'
        username = Parameters.get("Username")
        password = Parameters.get("Password")
        
        if not username or not password:
            Domoticz.Error("Username or Password not provided")
            return
        
        payload = {
            "email": username,
            "password": password
        }
        headers = {
            'Content-Type': 'application/json'
        }
                
        try:
            response = requests.post(login_url, headers=headers, json=payload)
            response.raise_for_status()
            
            data = response.json()
            if 'token' in data.get('data', {}):
                self.token = data['data']['token']
                Domoticz.Log(f"Login successful. Token: {self.token}")
                self.updateDevice()
            else:
                Domoticz.Error("Login failed: Token not received")
        except requests.RequestException as e:
            Domoticz.Error(f"Login request failed: {str(e)}")

    def onStop(self):
        Domoticz.Debug("E-Flux Plugin stopped")

    def onHeartbeat(self):
        Domoticz.Debug("onHeartbeat called")
        if not self.token:
            Domoticz.Debug("Token not available, retrying login...")
            self.login()
        else:
            self.updateDevice()
            
    def updateDevice(self):
        if not self.token:
            Domoticz.Error("No token available")
            return

        sessions_url = f'{self.api_url}/2/sessions/cpo/mine/fast'
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
        payload = {
            "limit": 100,
            "sort": {"order": "desc", "field": "createdAt"},
            "skip": 0
        }

        try:
            response = requests.post(sessions_url, headers=headers, json=payload)
            
            # Token is invalid or expired
            if response.status_code == 401:
                Domoticz.Error("Authentication failed, token may be invalid or expired. Retrying login...")
                self.login()
                return

            response.raise_for_status()
            data = response.json()
            if 'data' in data:
                sessions = data['data']
                if sessions:
                    latest_session = sessions[0]

                    total_kwh = latest_session.get('kwh', 0)
                    total_cost = latest_session.get('totalPrice', 0)
                    energy_costs = latest_session.get('energyCosts', 0)
                    duration_seconds = latest_session.get('durationSeconds', 0)
                    charger_status = latest_session.get('status', 'Unknown')

                    total_wh = total_kwh * 1000
                    if charger_status == 'CHARGING':
                        average_charging_rate = (total_kwh / (duration_seconds / 3600)) if duration_seconds > 0 else 0
                    else:
                        average_charging_rate = 0

                    Domoticz.Log(f"Total Wh: {total_wh}")
                    Domoticz.Log(f"Total Cost: {total_cost}")
                    Domoticz.Log(f"Energy Costs: {energy_costs}")
                    Domoticz.Log(f"Duration (seconds): {duration_seconds}")
                    Domoticz.Log(f"Average Charging Rate (kW): {average_charging_rate}")
                    Domoticz.Log(f"Charger Status: {charger_status}")

                    # Update devices with new values
                    self.updateDeviceValue(1, "{:.0f}".format(total_wh), 0)
                    self.updateDeviceValue(2, "{:.2f}".format(average_charging_rate), 0)
                    self.updateDeviceValue(3, charger_status, 0)
                    self.updateDeviceValue(4, "{:.2f} €".format(total_cost), 0)  # Total Cost with Euro symbol
                    self.updateDeviceValue(5, "{:.2f} €".format(energy_costs), 0)  # Energy Costs with Euro symbol
                    self.updateDeviceValue(6, "{:.2f}".format(duration_seconds), 0)

                    Domoticz.Log("Device update successful")
                else:
                    Domoticz.Log("No session data available for update")
            else:
                Domoticz.Log("Unexpected response format: 'data' field missing")

        except requests.RequestException as e:
            Domoticz.Error(f"Update request failed: {str(e)}")


    def createDevices(self):
        device_definitions = [
            (1, "Total Usage", "Usage"),  # Custom numerical value
            (2, "Current Usage", "Usage"),  # Custom numerical value
            (3, "Charger Status", "Text", 7),  # Text
            (4, "Total Cost", "Text", 7),  # Custom numerical value
            (5, "Energy Costs", "Text", 7),  # Custom numerical value
            (6, "Duration", "Counter")  # Custom numerical value
        ]
        
        for unit, name, type_name, *options in device_definitions:
            if unit not in Devices:
                Domoticz.Device(Name=name, Unit=unit, TypeName=type_name, Options=options[0] if options else {}, Image=options[1] if len(options) > 1 else 0).Create()

    def updateDeviceValue(self, unit, sValue, nValue):
        try:
            if unit in Devices:
                Devices[unit].Update(nValue=nValue, sValue=str(sValue), TimedOut=0)
            else:
                Domoticz.Error(f"Device with unit {unit} not found.")
        except Exception as e:
            Domoticz.Error(f"Error updating device {unit}: {e}")

def DumpConfigToLog():
    for x in Parameters:
        if Parameters[x] != "":
            Domoticz.Debug(f"'{x}':'{Parameters[x]}'")
            
    Domoticz.Debug(f"Device count: {len(Devices)}")
    for x in Devices:
        device = Devices[x]
        Domoticz.Debug(f"Device: {x} - {device}")
        Domoticz.Debug(f"Device ID: '{device.ID}'")
        Domoticz.Debug(f"Device Name: '{device.Name}'")
        Domoticz.Debug(f"Device nValue: {device.nValue}")
        Domoticz.Debug(f"Device sValue: '{device.sValue}'")
        Domoticz.Debug(f"Device LastLevel: {device.LastLevel}")

global _plugin
_plugin = EFluxPlugin()

def onStart():
    global _plugin
    _plugin.onStart()

def onStop():
    global _plugin
    _plugin.onStop()

def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()

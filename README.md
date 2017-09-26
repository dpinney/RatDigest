# RatDigest

It configures and generates cyber-physical simulation results for advanced security reasearch. It's an anagram of GridState.

# GLM Assumptions

- No clock or minimum timestep settings (we add our own).

# Todo (XXX = Complete)

- XXX Add identifier to each payload.
- XXX Switch object in test system.
- XXX Add switching actions.
- XXX Add meter disconnects via service_status 1/0 attribute.
- XXX Add regulator tap change actions.
- XXX Add control messages.
- XXX Generate alarms with identifiers.
- XXX Add attacks.

# Identifier Key

- XXX Latest AMI Reading = MS-GetLatestReadings = MS-GLR
- XXX AMI Meter disconnect command = MS-IniateDisconnectConnect = MS-IDC
- XXX Regulator kWh measurement = DNP-SubstationKwH = DNP-SKW
- XXX Switch CONTROL message = DNP-SubstationBreakerSwitchStatus = DNP-SBSS
- XXX Regulator CONTROL message = DNP-SubstationVoltageControl = DNP-SVC
- XXX AMI Meter Alarm = MS-ODEventNotification = MS-ODEN
- XXX Breaker open/close = DNP-SubstationBreakerSwitchWrite
- OOO Reading From Multiple Meters (Not a total! Only include energy!) = MS-GetLatestReadingsByMeterGroup = MS-GLRBMG

# Laterbase

- OOO Add a 'restored' message post AMI alarm.
- OOO 5th attack type.
- OOO Deal with timezone set manually to PST.
- OOO Don't os.chdir.
- OOO Some device names are filenames, others are just GLD device names. Standardize.
- OOO Switch read interval different from regulator?
- OOO Probability based message drops?
- OOO Additional alarms?
- OOO Add multimeter reading payloads and identifier.
- OOO Reg voltage in output via ```w = complex('+701.409+142.17j'); i = complex('+0.290224-0.0588258j'); print abs(w/i)```
- OOO Add robustness to alarm code.
- OOO Port to RADICS model.

# Attack List

For the November 2017 exercise 5 types of attacks are considered to be in scope:

- XXX PRE - AMI.1: Authorized Employee Issues Unauthorized Mass Remote Disconnect - do meter disconnects in simulation for a long list of meters.
- XXX PRE - DGM.10: Switched Capacitor Banks are Manipulated to Degrade Power Quality - tell a bunch of caps to switch in the simulation.
- XXX POST - Denial of Service Attack - Delete all messages from (device, start, end) tuples.
- XXX POST - AMI.8: False Meter Alarms Overwhelm AMI and Mask Real Alarms - create a bunch of fake alarm messages based on a list of (meter, timestamp) pairs.
- OOO POST - DGM.6: Spoofed Substation Field Devices Influence Automated Responses - "For this attack type, Output_Message_Creation() will artificially modify the connectivity, power or voltage status/readings at specified devices.  A list of spoofed devices will be provided for this attack.  Each item in the list will include a start and end timestamps, a device identifier, a quantity identifier (connection status, power, voltage), and a code indicating the change that should be calculated. (The “codes” will indicate whether a value should be reduced to 0, multiplied by a factor, set to a specific value, etc.  [The ”codes” are to be determined.] Note: The creation of these spoofed messages does not change anything about how the GridLab-D simulation is run.

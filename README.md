# RatDigest

It configures and generates cyber-physical simulation results for advanced security reasearch. It's an anagram of GridState.

# Install Instructions.

Get the prerequisites: [GridLAB-D](https://sourceforge.net/projects/gridlab-d/files/?source=navbar) and Python [2.7.x](https://www.python.org/downloads/). Then download the ratDigest [release you want](https://github.com/dpinney/RatDigest/releases), unzip it, and run `python ratDigest.py` to run the tests.

# GLM Assumptions

- No clock or minimum timestep settings (we add our own).

# v1 Todo List (XXX = Complete)

- XXX Add identifier to each payload.
- XXX Switch object in test system.
- XXX Add switching actions.
- XXX Add meter disconnects via service_status 1/0 attribute.
- XXX Add regulator tap change actions.
- XXX Add control messages.
- XXX Generate alarms with identifiers.
- XXX Add attacks.

# v2 Todo List

- XXX Get v4.0 install instructions (not an issue) and breaker open/close info from PNNL.
- XXX Don't os.chdir. Nah, it's actually pretty clear to move the process.
- XXX Switch read interval different from regulator? Not an issue.
- XXX Amount of wall clock time available to run exercise sims? 14 hours.
- XXX Some device names are filenames, others are just GLD device names. Standardized.
- XXX Bug with not checking device ID when doing dos attack. Fixed.
- XXX Get phil craig types. Added to docs.
- XXX Install instructions. Added to readme.
- XXX Switch timezone from PST to UTC. What about climate? Did proper timezone support. Codes in tzinfo.txt.
- XXX Pairs of request/response - see Request Response Exchange.JPG
- XXX Probability based message drops? One drop rate for all responses to read messages added.
- OOO Different alarm approach that doesn't rely on stderr and will scale to all alarm types.
- OOO Run on an intermediate sized system, 2 meter groups.

# v3 Todo List
- OOO Add a 'restored' message post AMI alarm.
- OOO Alarms on power and not just voltage?
- OOO Add multimeter reading payloads and identifier - 1 request with list of meters in group, 1 response with list of values.
- OOO Add responses to control messages?
- OOO Add probability drops to control message actions?
- OOO 5th attack type.
- OOO Charts in anomalyExample.
- OOO need a control action generator with frequency basis.
- OOO Port to the final RADICS model.
- OOO inputs from file instead of in the source?
- OOO Reg voltage in output via ```w = complex('+701.409+142.17j'); i = complex('+0.290224-0.0588258j'); print abs(w/i)```

# Identifier Key

- XXX Latest AMI Reading = MS-GetLatestReadings = MS-GLR
- XXX AMI Meter disconnect command = MS-IniateDisconnectConnect = MS-IDC
- XXX Regulator kWh measurement = DNP-SubstationKwH = DNP-SKW
- XXX Switch CONTROL message = DNP-SubstationBreakerSwitchStatus = DNP-SBSS
- XXX Regulator CONTROL message = DNP-SubstationVoltageControl = DNP-SVC
- XXX AMI Meter Alarm = MS-ODEventNotification = MS-ODEN
- XXX Breaker open/close = DNP-SubstationBreakerSwitchWrite
- OOO Reading From Multiple Meters (Not a total! Only include energy!) = MS-GetLatestReadingsByMeterGroup = MS-GLRBMG

# Attack List

For the November 2017 exercise 5 types of attacks are considered to be in scope:

- XXX PRE - AMI.1: Authorized Employee Issues Unauthorized Mass Remote Disconnect - do meter disconnects in simulation for a long list of meters.
- XXX PRE - DGM.10: Switched Capacitor Banks are Manipulated to Degrade Power Quality - tell a bunch of caps to switch in the simulation.
- XXX POST - Denial of Service Attack - Delete all messages from (device, start, end) tuples.
- XXX POST - AMI.8: False Meter Alarms Overwhelm AMI and Mask Real Alarms - create a bunch of fake alarm messages based on a list of (meter, timestamp) pairs.
- OOO POST - DGM.6: Spoofed Substation Field Devices Influence Automated Responses - "For this attack type, Output_Message_Creation() will artificially modify the connectivity, power or voltage status/readings at specified devices.  A list of spoofed devices will be provided for this attack.  Each item in the list will include a start and end timestamps, a device identifier, a quantity identifier (connection status, power, voltage), and a code indicating the change that should be calculated. (The “codes” will indicate whether a value should be reduced to 0, multiplied by a factor, set to a specific value, etc.  [The ”codes” are to be determined.] Note: The creation of these spoofed messages does not change anything about how the GridLab-D simulation is run.

# RatDigest

It configures and generates cyber-physical simulation results for advanced security reasearch. It's an anagram of GridState.

# Todo (XXX = Complete)

- XXX Add identifier to each payload.
- XXX Switch object in test system.
- XXX Add switching actions.
- XXX Add meter disconnects via service_status 1/0 attribute.
- XXX Add regulator tap change actions.
- XXX Add control messages.
- OOO Generate alarms with identifiers.
- OOO Add attacks.

# Identifier Key

- XXXLatest AMI Reading = MS-GetLatestReadings = MS-GLR
- XXX AMI Meter disconnect command = MS-IniateDisconnectConnect = MS-IDC
- XXX Regulator kWh measurement = DNP-SubstationKwH = DNP-SKW
- XXX Switch CONTROL message = DNP-SubstationBreakerSwitchStatus = DNP-SBSS
- XXX Regulator CONTROL message = DNP-SubstationVoltageControl = DNP-SVC
- AMI Meter Alarm = MS-ODEventNotification = MS-ODEN
- Reading From Multiple Meters (Not a total! Only include energy!) = MS-GetLatestReadingsByMeterGroup = MS-GLRBMG
- More to be identified later...

# Laterbase

- OOO Add multimeter reading payloads and identifier.
- OOO Reg volatge in output via:
	```
	w = complex('+701.409+142.17j') # reg power
	i = complex('+0.290224-0.0588258j') # reg current
	# w=iv => v=w/i
	print abs(w/i)
	```
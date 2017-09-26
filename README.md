# RatDigest

It configures and generates cyber-physical simulation results for advanced security reasearch. It's an anagram of GridState.

# Todo
XXX Add identifier to each payload.
XXX Switch object in test system.
OOO Add switching actions.
OOO Add meter disconnects via service_status 1/0 attribute.
OOO Add regulator tap change actions.
OOO Generate alarms.
OOO Add attacks.
OOO Additional identifiers.
OOO Add multimeter reading payloads.

# Identifier Key

XXXLatest AMI Reading = MS-GetLatestReadings = MS-GLR
AMI Meter Alarm = MS-ODEventNotification = MS-ODEN
Reading From Multiple Meters (Not a total! Only include energy!) = MS-GetLatestReadingsByMeterGroup = MS-GLRBMG
AMI Meter disconnect command = MS-IniateDisconnectConnect = MS-IDC
XXX Regulator kWh measurement = DNP-SubstationKwH = DNP-SKW
Switch CONTROL message = DNP-SubstationBreakerSwitchStatus = DNP-SBSS
Regulator CONTROL message = DNP-SubstationVoltageControl = DNP-SVC
More to be identified later...

import json
from pprint import pprint as pp
from datetime import datetime, timedelta

FNAME = './littleTest/ratDigestPostAttack.json'

messages = json.load(open(FNAME))
pp(messages)

m3 = messages[3]
print m3
print m3.keys()
print m3['timestamp']

meterList = [x for x in messages if x.get('identifier','') == 'MS-GetLatestReadings']
pp(meterList)

voltage1 = [x['measured_voltage_1'] for x in messages if 'measured_voltage_1' in x]
voltage2 = [x['measured_voltage_2'] for x in messages if 'measured_voltage_2' in x]
allVolts = voltage1 + voltage2
print allVolts

compVoltages = [complex(x.replace('d','j')) for x in allVolts]
print compVoltages

voltageMags = [abs(x) for x in compVoltages]
meanVoltage = sum(voltageMags)/len(voltageMags)
print meanVoltage

def voltMag(m):
	if 'measured_voltage_1' in m:
		return abs(complex(m['measured_voltage_1'].replace('d','j')))
	elif 'measured_voltage_2' in m:
		return abs(complex(m['measured_voltage_2'].replace('d','j')))
	else:
		return None

overVolts = [m for m in messages if voltMag(m) > meanVoltage]
pp(overVolts)

def parseDate(d):
	return datetime.strptime(d[0:-4], '%Y-%m-%d %H:%M:%S')

m4 = messages[4]
print parseDate(m3['timestamp']) - parseDate(m4['timestamp'])


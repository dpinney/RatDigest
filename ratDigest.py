'''RatDigest Makes Network Messages From GridLAB-D Simulations.'''

import os, subprocess, csv, json, random
from datetime import datetime, timedelta
import inputObjects


def dig(inputDict):
	''' Run full ratDigest workflow.'''
	out = pre(inputDict)
	attackedOut = post(inputDict, out)

def pre(inDict):
	print "Starting message generation."
	#############################
	# Generate a new .glm file. #
	#############################
	FILE_UID = 'ratDigest'
	os.chdir(inDict['glmDirPath'])
	# Remove old outputs.
	for fName in os.listdir('.'):
		try:
			if fName.startswith(FILE_UID):
				os.remove(fName)
		except:
			pass # tried but couldn't delete old output.
	# Dump the inputs for our records.
	with open(FILE_UID + 'Inputs.json', 'w+') as inFile:
		json.dump(inDict, inFile, indent=4)
	# Templates used to rewrite .glm:
	timeTemplate = 'clock {\n' +\
		'\ttimezone INSERT_TIMEZONE;\n' +\
		"\tstarttime 'INSERT_START_TIME';\n" +\
		"\tstoptime 'INSERT_STOP_TIME';\n" +\
		'\t};\n' +\
		'#set minimum_timestep=INSERT_TIME_STEP;\n\n'
	recorderTemplate = 'object recorder {\n' +\
		'\tfile INSERT_FILE_NAME.csv;\n' +\
		'\tinterval INSERT_INTERVAL;\n' +\
		'\tparent INSERT_PARENT;\n' +\
		'\tproperty INSERT_PROPERTIES;\n' +\
		'};\n\n'
	playerTemplate = 'object player {\n' +\
		'\tfile INSERT_FILE_NAME.player;\n' +\
		'\tparent INSERT_PARENT;\n' +\
		'\tproperty INSERT_PROPERTIES;\n' +\
		'};\n\n'
	alarmTemplate = 'object group_recorder {\n' +\
		'\tfile INSERT_FILE_NAME.csv;\n' +\
		'\tgroup INSERT_GROUP;\n' +\
		'\tinterval INSERT_INTERVAL;\n' +\
		'\tproperty INSERT_PROPERTY;\n' +\
		'};\n\n'
	print "Updating GridLAB-D inputs."
	allPlayers = 'class player {double value;};\n\n'
	allRecorders = ''
	# Modify templates to reflect input parameters.
	timeTemplate = timeTemplate.replace('INSERT_START_TIME',inDict['preProc']['startTime'])
	timeTemplate = timeTemplate.replace('INSERT_STOP_TIME',inDict['preProc']['stopTime'])
	timeTemplate = timeTemplate.replace('INSERT_TIME_STEP',inDict['preProc']['simTimeStep'])
	timeTemplate = timeTemplate.replace('INSERT_TIMEZONE',inDict['preProc']['timezone'])
	for phase in ['1','2']:
		tempTemplate = str(alarmTemplate)
		tempTemplate = tempTemplate.replace('INSERT_FILE_NAME', FILE_UID + '_ALARM_VOLTS_' + phase)
		tempTemplate = tempTemplate.replace('INSERT_INTERVAL', inDict['preProc']['alarmMinIntervalSeconds'])
		tempTemplate = tempTemplate.replace('INSERT_GROUP', 'class=triplex_meter')
		tempTemplate = tempTemplate.replace('INSERT_PROPERTY', 'measured_voltage_' + phase)
		allRecorders += tempTemplate
	for singlePhaseMeterName in inDict['preProc']['singlePhaseMeterNames']:
		tempTemplate = str(recorderTemplate)
		tempTemplate = tempTemplate.replace('INSERT_FILE_NAME', FILE_UID + '_1METER_' + singlePhaseMeterName)
		tempTemplate = tempTemplate.replace('INSERT_INTERVAL', inDict['preProc']['meterReadInterval'])
		tempTemplate = tempTemplate.replace('INSERT_PARENT', singlePhaseMeterName)
		tempTemplate = tempTemplate.replace('INSERT_PROPERTIES', 'measured_real_energy, voltage_12')
		allRecorders += tempTemplate
	for threePhaseMeterName in inDict['preProc']['threePhaseMeterNames']:
		tempTemplate = str(recorderTemplate)
		tempTemplate = tempTemplate.replace('INSERT_FILE_NAME', FILE_UID + '_3METER_' + threePhaseMeterName)
		tempTemplate = tempTemplate.replace('INSERT_INTERVAL', inDict['preProc']['meterReadInterval'])
		tempTemplate = tempTemplate.replace('INSERT_PARENT', threePhaseMeterName)
		tempTemplate = tempTemplate.replace('INSERT_PROPERTIES', 'measured_real_energy, measured_real_power, measured_reactive_power, measured_voltage_A, measured_voltage_B, measured_voltage_C')
		allRecorders += tempTemplate	
	for regName in inDict['preProc']['regulatorNames']:
		tempTemplate = str(recorderTemplate)
		tempTemplate = tempTemplate.replace('INSERT_FILE_NAME', FILE_UID + '_REG_' + regName)
		tempTemplate = tempTemplate.replace('INSERT_INTERVAL', inDict['preProc']['regulatorReadInterval'])
		tempTemplate = tempTemplate.replace('INSERT_PARENT', regName)
		tempTemplate = tempTemplate.replace('INSERT_PROPERTIES', 'tap_A, tap_B, tap_C')
		allRecorders += tempTemplate
	for transformerName in inDict['preProc']['transformerNames']:
		tempTemplate = str(recorderTemplate)
		tempTemplate = tempTemplate.replace('INSERT_FILE_NAME', FILE_UID + '_TRANSFORMER_' + transformerName)
		tempTemplate = tempTemplate.replace('INSERT_INTERVAL', inDict['preProc']['transformerReadInterval'])
		tempTemplate = tempTemplate.replace('INSERT_PARENT', transformerName)
		tempTemplate = tempTemplate.replace('INSERT_PROPERTIES', 'current_out_A, current_out_B, current_out_C, power_out, power_out_A, power_out_B, power_out_C')
		allRecorders += tempTemplate
	for nodeName in inDict['preProc']['nodeNames']:
		tempTemplate = str(recorderTemplate)
		tempTemplate = tempTemplate.replace('INSERT_FILE_NAME', FILE_UID + '_NODE_' + nodeName)
		tempTemplate = tempTemplate.replace('INSERT_INTERVAL', inDict['preProc']['nodeReadInterval'])
		tempTemplate = tempTemplate.replace('INSERT_PARENT', nodeName)
		tempTemplate = tempTemplate.replace('INSERT_PROPERTIES', 'voltage_A, voltage_B, voltage_C')
		allRecorders += tempTemplate
	for switchName in inDict['preProc']['switchNames']:
		tempTemplate = str(recorderTemplate)
		tempTemplate = tempTemplate.replace('INSERT_FILE_NAME', FILE_UID + '_SWITCH_' + switchName)
		tempTemplate = tempTemplate.replace('INSERT_INTERVAL', inDict['preProc']['switchReadInterval'])
		tempTemplate = tempTemplate.replace('INSERT_PARENT', switchName)
		tempTemplate = tempTemplate.replace('INSERT_PROPERTIES', 'phase_A_state, phase_B_state, phase_C_state')
		allRecorders += tempTemplate
	for capacitorName in inDict['preProc']['capacitorNames']:
		tempTemplate = str(recorderTemplate)
		tempTemplate = tempTemplate.replace('INSERT_FILE_NAME', FILE_UID + '_CAP_' + capacitorName)
		tempTemplate = tempTemplate.replace('INSERT_INTERVAL', inDict['preProc']['capacitorReadInterval'])
		tempTemplate = tempTemplate.replace('INSERT_PARENT', capacitorName)
		tempTemplate = tempTemplate.replace('INSERT_PROPERTIES', 'switchA, switchB, switchC')
		allRecorders += tempTemplate
	for action in inDict['preProc']['controlActions']:
		tempTemplate = str(playerTemplate)
		fileName = FILE_UID + '_PLAYER_' + action['parent'] + '_' + action['property']
		tempTemplate = tempTemplate.replace('INSERT_FILE_NAME', fileName)
		tempTemplate = tempTemplate.replace('INSERT_PARENT', action['parent'])
		tempTemplate = tempTemplate.replace('INSERT_PROPERTIES', action['property'])
		allPlayers += tempTemplate
		with open(fileName + '.player', 'w') as pFile:
			playerContent = action['schedule'].replace(';','\n')
			pFile.write(playerContent)
	# Modify and write the new GLM.
	glmContent = open(inDict['glmName'],'r').read()
	glmContent = timeTemplate + glmContent + allPlayers + allRecorders
	with open(FILE_UID + '.glm', 'w') as outFile:
		outFile.write(glmContent)
	print "Starting GridLAB-D."
	# Run the new GLM.
	with open(FILE_UID + '_xstdout.txt','w') as stdout, open(FILE_UID + '_xstderr.txt','w') as stderr:
		proc = subprocess.Popen(['gridlabd','ratDigest.glm'], stdout=stdout, stderr=stderr)
		returnCode = proc.wait()
	#######################################################
	# Turn GridLAB-D output CSV data in to a message list #
	#######################################################
	print "GridLAB-D run complete.  Generating pre-attack message list."
	allFileNames = os.listdir('.')
	csvFileNames = [x for x in allFileNames if x.startswith(FILE_UID) and x.endswith('.csv')]
	output = []
	alarmReads = []
	tzc = ' ' + inDict['preProc']['timezone'][0:3]
	# Put recorder data in output.
	for fName in csvFileNames:
		with open(fName,'r') as inFile:
			# Burn the first 8 lines which are metadata we don't need.
			for x in xrange(8):
				inFile.readline()
			# Headers are in line 9.
			headers = inFile.readline()
			headList = headers.replace('# ','').replace('\n','').replace(' ','').split(',')
			reader = csv.DictReader(inFile, fieldnames=headList)
			for message in reader:
				# Pull out alarms for separate alarm process.
				if fName.startswith(FILE_UID + '_ALARM_'):
					alarmReads.append(message)
					continue
				# Process response.
				message['device_name'] = fName\
					.replace('.csv','')\
					.replace('ratDigest_1METER_','')\
					.replace('ratDigest_3METER_','')\
					.replace('ratDigest_REG_','')\
					.replace('ratDigest_TRANSFORMER_','')\
					.replace('ratDigest_NODE_','')\
					.replace('ratDigest_SWITCH_','')\
					.replace('ratDigest_CAP_','')
				# Add identifiers for Phil Craig.
				if fName.startswith(FILE_UID + '_1METER_'):
					ident = 'MS-GetLatestReadings-SinglePhaseMeter'
				elif fName.startswith(FILE_UID + '_3METER_'):
					ident = 'MS-GetLatestReadings-ThreePhaseMeter'
				elif fName.startswith(FILE_UID + '_REG_'):
					ident = 'DNP-Substation-RegulatorStatus'
				elif fName.startswith(FILE_UID + '_TRANSFORMER_'):
					ident = 'DNP-Substation-TransformerStatus'
				elif fName.startswith(FILE_UID + '_NODE_'):
					ident = 'DNP-Substation-Node'
				elif fName.startswith(FILE_UID + '_SWITCH_'):
					ident = 'DNP-Substation-SwitchStatus'
				elif fName.startswith(FILE_UID + '_CAP_'):
					ident = 'DNP-Substation-CapacitorStatus'
				else:
					ident = 'unknown'
				# Add voltages to regulator readings.
				# if message.get('device_name','') in smallInput['preProc']['regulatorNames']:
				# 	for phase in ['A','B','C']:
				# 		power = complex(message.get('power_out_' + phase))
				# 		current = complex(message.get('current_out_' + phase))
				# 		if current==0:
				# 			message['voltage_' + phase] = str(complex(0))
				# 		else:
				# 			message['voltage_' + phase] = str(power/current)
				# Also make a message to request each reading.
				reqMessage = {
					'device_name':message['device_name'],
					'timestamp':message['timestamp'],
					'identifier': ident,
					'attack': False
				}
				# Add a little latency to the responses:
				latencySeconds =  random.randint(0,inDict['preProc']['responseLatencySeconds'])
				stampPlusLatency = tParse(message['timestamp']) + timedelta(seconds=latencySeconds)
				message['timestamp'] = str(stampPlusLatency) + tzc
				message['identifier'] = ident + '-RESPONSE'
				message['attack'] = False
				# Write request message.
				output.append(reqMessage)
				# Drop some responses with the given probability.
				if random.random() > inDict['preProc']['responseDropProbability']:
					output.append(message)
	# Add control messages to output.
	for action in inDict['preProc']['controlActions']:
		for event in action['schedule'].split(';'):
			(timestamp, value) = event.split(',')
			outMessage = {
				'device_name':action['parent'],
				'control_variable':action['property'],
				'value': value,
				'timestamp':timestamp + tzc,
				'identifier':action['identifier'],
				'attack': False
			}
			output.append(outMessage) 
	# Process single phase meter alarms.
	for singlePhaseMeterName in inDict['preProc']['singlePhaseMeterNames']:
		voltProblem = False
		for step in alarmReads:
			voltage = complex(step[singlePhaseMeterName].replace('d','j'))
			# Note: d indicated polar coordinates, so we only want the real part here.
			voltageMag = voltage.real/120.0
			stamp = step['timestamp']
			noVolts = (voltageMag > 1.15 or voltageMag < 0.85)
			if not voltProblem and noVolts:
				# New voltage problem.
				alarmMessage = {
					'location':singlePhaseMeterName,
					'identifier':'MS-ODEventNotification',
					'type':'voltage alarm',
					'timestamp':stamp,
					'magnitude':str(voltageMag),
					'attack': False
				}
				output.append(alarmMessage)
				voltProblem = True
			elif voltProblem and not noVolts:
				# Voltage problem resolved.
				restoreMessage = {
					'location':singlePhaseMeterName,
					'identifier':'MS-ODEventNotification',
					'type':'voltage restoration',
					'timestamp':timestamp + tzc,
					'attack': False
				}
				output.append(restoreMessage)
				voltProblem = False
			else:
				continue
	print "Writing pre-attack messages to file.", len(output),"total messages generated."
	# Write full output.
	with open(FILE_UID + 'PreAttack.json','w') as outFile:
		json.dump(output, outFile, indent=4)
	# Also return output for post processing.
	return output

def post(inDict, messages):
	"Starting post attack message generation."
	# Short timezone coda for things missing it.
	tzc = ' ' + inDict['preProc']['timezone'][0:3]
	# Perform DOS attacks by dropping messages.
	deleteList = []
	attackList = []
	for attack in inDict['postProc']['dosList']:
		start = tParse(attack['start'] + tzc)
		end = tParse(attack['end'] + tzc)
		for message in messages:
			time = tParse(message['timestamp'])
			rightTime = start < time < end
			rightDevice = (attack['device_name'] == message.get('device_name',''))
			if rightTime and rightDevice:
				if "RESPONSE" in message["identifier"]:
					deleteList.append(message)
					newDeviceName = 'DELETED' + message['device_name']
					message['device_name'] = newDeviceName
					newIdentifier = 'DELETED' + message['identifier']
					message['attack'] = True
					attackList.append(message)
	for message in deleteList:
		messages.remove(message)
	for message in attackList:
		messages.append(message)
	# Perform spoof attacks.
	for attack in inDict['postProc']['spoofList']:
		start = tParse(attack['start'] + tzc)
		end = tParse(attack['end'] + tzc)
		if attack['type'] is 'alarm':
			underVoltage = random.randrange(95.0,110.0)
			overVoltage = random.randrange(130.0,145.0)
			magnitude = random.choice([underVoltage,overVoltage])
			messageTemplate = {
				'identifier': 'MS-ODEventNotification', 
				'type': 'voltage alarm', 
				'location': attack['device_name'], 
				'magnitude': str(magnitude),
				'fake':'True',
				'attack': True
			}
		else:
			raise Exception('No type specified for attack ' + str(attack))
		for count in xrange(attack['quantity']):
			fakeMessage = dict(messageTemplate)
			fakeMessage['timestamp'] = datetime.strftime(randomDate(start, end), '%Y-%m-%d %H:%M:%S' + tzc)
			messages.append(fakeMessage)
	# Perform mod attacks.
	for attack in inDict['postProc']['modList']:
		start = tParse(attack['start'] + tzc)
		end = tParse(attack['end'] + tzc)
		for message in messages:
			time = tParse(message['timestamp'])
			rightTime = start < time < end
			rightDevice = attack['device_name'] == message.get('device_name','')
			rightProp = attack['property'] in message
			if rightTime and rightDevice and rightProp:
				message['fakeMod'] = 'True'
				message['attack'] = True
				prop = message[attack['property']]
				# Perform complex affine transform.
				newProp = str(complex(prop) * complex(attack['multiply']) + complex(attack['add']))
				message[attack['property']] = newProp
	print "Writing post-attack messages to file.", len(messages), "total messages generated."
	# Dump results.
	with open('ratDigestPostAttack.json','w') as outFile:
		json.dump(messages, outFile, indent = 4)
		
	# And return as well.
	return messages

def tParse(timeString):
	''' Helper function for timestamp parsing.'''
	return datetime.strptime(timeString[0:-4], '%Y-%m-%d %H:%M:%S')

def randomDate(start, end):
	''' Helper function for random dates in a range. '''
	delta = end - start
	int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
	random_second = random.randrange(int_delta)
	return start + timedelta(seconds=random_second)

if __name__ == '__main__':
	# dig(inputObjects.smallInput)
	# dig(inputObjects.largeInput)
	dig(inputObjects.RADICS_Sub1Input)

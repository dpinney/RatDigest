'''RatDigest Makes Network Messages From GridLAB-D Simulations.'''

import os, subprocess, csv, json, random
from datetime import datetime, timedelta

smallInput = {
	'glmDirPath':'./littleTest/',
	'glmName':'smsSingle.glm',
	'preProc': {
		'startTime':'2017-01-01 12:00:00',
		'stopTime':'2017-01-01 13:00:00',
		'timezone':'PST+8PDT',
		'simTimeStep':'4',
		'responseLatencySeconds':3,
		'responseDropProbability':0,
		'alarmMinIntervalSeconds':'60',
		'meterReadInterval':'800',
		'meterNames':['tm_1','tm_2'],
		'regulatorNames':['Reg1'],
		'regulatorReadInterval':'450',
		'switchNames':['newSwitch'],
		'controlActions':[
			{'identifier':'MS-IniateDisconnectConnect','parent':'tm_1','property':'service_status','schedule':'2017-01-01 12:30:00,0'},
			{'identifier':'DNP-SubstationBreakerSwitchWrite','parent':'newSwitch','property':'phase_A_state','schedule':'2017-01-01 12:30:00,0'},
			{'identifier':'DNP-SubstationVoltageControl','parent':'Reg1','property':'tap_A','schedule':'2017-01-01 12:00:00,2;2017-01-01 12:15:00,1;2017-01-01 12:45:00,2'},
			{'identifier':'INTENTIONAL_FAULT','parent':'bigload','property':'base_power','schedule':'2017-01-01 12:45:00,60.0 kW'}
		],
	},
	'postProc': {
		'dosList':[
			{'device_name':'Reg1','start':'2017-01-01 12:45:00','end':'2017-01-01 12:59:00'}
		],
		'spoofList':[
			{'device_name':'tm_2','type':'alarm','quantity':5,'start':'2017-01-01 12:20:00','end':'2017-01-01 12:40:00'}
		],
		'modList':[
			{'device_name':'Reg1','property':'power_out_B','multiply':0.5,'add':1,'start':'2017-01-01 12:00:00','end':'2017-01-01 12:20:00',},
			{'device_name':'Reg1','property':'power_out_A','multiply':0,'add':0,'start':'2017-01-01 12:00:00','end':'2017-01-01 12:20:00',},
		]
	}
}

largeInput = {
	'glmDirPath':'./lessLittleTest/',
	'glmName':'RADICS_Sub1.glm',
	'preProc': {
		'startTime':'2009-01-01 12:00:00',
		'stopTime':'2009-01-01 14:00:00',
		'timezone':'CST+6CDT',
		'simTimeStep':'4',
		'responseLatencySeconds':3,
		'responseDropProbability':0,
		'alarmMinIntervalSeconds':'60',
		'meterReadInterval':'800',
		'meterNames':['R2-12-47-2_tm_1','R2-12-47-2_tm_2','R2-12-47-2_tm_3','R2-12-47-2_tm_4','R2-12-47-2_tm_5','R2-12-47-2_tm_6','R2-12-47-2_tm_7','R2-12-47-2_tm_8','R2-12-47-2_tm_9','R2-12-47-2_tm_10','R2-12-47-2_tm_11','R2-12-47-2_tm_12','R2-12-47-2_tm_13','R2-12-47-2_tm_14','R2-12-47-2_tm_15','R2-12-47-2_tm_16','R2-12-47-2_tm_17','R2-12-47-2_tm_18','R2-12-47-2_tm_19','R2-12-47-2_tm_20','R2-12-47-2_tm_21','R2-12-47-2_tm_22','R2-12-47-2_tm_23','R2-12-47-2_tm_24','R2-12-47-2_tm_25','R2-12-47-2_tm_26','R2-12-47-2_tm_27','R2-12-47-2_tm_28','R2-12-47-2_tm_29','R2-12-47-2_tm_30','R2-12-47-2_tm_31','R2-12-47-2_tm_32','R2-12-47-2_tm_33','R2-12-47-2_tm_34','R2-12-47-2_tm_35','R2-12-47-2_tm_36','R2-12-47-2_tm_37','R2-12-47-2_tm_38','R2-12-47-2_tm_39','R2-12-47-2_tm_40','R2-12-47-2_tm_41','R2-12-47-2_tm_42','R2-12-47-2_tm_43','R2-12-47-2_tm_44','R2-12-47-2_tm_45','R2-12-47-2_tm_46','R2-12-47-2_tm_47','R2-12-47-2_tm_48','R2-12-47-2_tm_49','R2-12-47-2_tm_50','R2-12-47-2_tm_51','R2-12-47-2_tm_52','R2-12-47-2_tm_53','R2-12-47-2_tm_54','R2-12-47-2_tm_55','R2-12-47-2_tm_56','R2-12-47-2_tm_57','R2-12-47-2_tm_58','R2-12-47-2_tm_59','R2-12-47-2_tm_60','R2-12-47-2_tm_61','R2-12-47-2_tm_62','R2-12-47-2_tm_63','R2-12-47-2_tm_64','R2-12-47-2_tm_65','R2-12-47-2_tm_66','R2-12-47-2_tm_67','R2-12-47-2_tm_68','R2-12-47-2_tm_69','R2-12-47-2_tm_70','R2-12-47-2_tm_71','R2-12-47-2_tm_72','R2-12-47-2_tm_73','R2-12-47-2_tm_74','R2-12-47-2_tm_75','R2-12-47-2_tm_76','R2-12-47-2_tm_77','R2-12-47-2_tm_78','R2-12-47-2_tm_79','R2-12-47-2_tm_80','R2-12-47-2_tm_81','R2-12-47-2_tm_82','R2-12-47-2_tm_83','R2-12-47-2_tm_84','R2-12-47-2_tm_85','R2-12-47-2_tm_86','R2-12-47-2_tm_87','R2-12-47-2_tm_88','R2-12-47-2_tm_89','R2-12-47-2_tm_90','R2-12-47-2_tm_91','R2-12-47-2_tm_92','R2-12-47-2_tm_93','R2-12-47-2_tm_94','R2-12-47-2_tm_95','R2-12-47-2_tm_96','R2-12-47-2_tm_97','R2-12-47-2_tm_98','R2-12-47-2_tm_99','R2-12-47-2_tm_100','R2-12-47-2_tm_101','R2-12-47-2_tm_102','R2-12-47-2_tm_103','R2-12-47-2_tm_104','R2-12-47-2_tm_105','R2-12-47-2_tm_106','R2-12-47-2_tm_107','R2-12-47-2_tm_108','R2-12-47-2_tm_109','R2-12-47-2_tm_110','R2-12-47-2_tm_111','R2-12-47-2_tm_112','R2-12-47-2_tm_113','R2-12-47-2_tm_114','R2-12-47-2_tm_115','R2-12-47-2_tm_116','R2-12-47-2_tm_117','R2-12-47-2_tm_118','R2-12-47-2_tm_119','R2-12-47-2_tm_120','R2-12-47-2_tm_121','R2-12-47-2_tm_122','R2-12-47-2_tm_123','R2-12-47-2_tm_124','R2-12-47-2_tm_125','R2-12-47-2_tm_126','R2-12-47-2_tm_127','R2-12-47-2_tm_128','R2-12-47-2_tm_129','R2-12-47-2_tm_130','R2-12-47-2_tm_131','R2-12-47-2_tm_132','R2-12-47-2_tm_133','R2-12-47-2_tm_134','R2-12-47-2_tm_135','R2-12-47-2_tm_136','R2-12-47-2_tm_137','R2-12-47-2_tm_138','R2-12-47-2_tm_139','R2-12-47-2_tm_140','R2-12-47-2_tm_141','R2-12-47-2_tm_142','R2-12-47-2_tm_143','R2-12-47-2_tm_144','R2-12-47-2_tm_145','R2-12-47-2_tm_146','R2-12-47-2_tm_147','R2-12-47-2_tm_148','R2-12-47-2_tm_149','R2-12-47-2_tm_150','R2-12-47-2_tm_151','R2-12-47-2_tm_152','R2-12-47-2_tm_153','R2-12-47-2_tm_154','R2-12-47-2_tm_155','R2-12-47-2_tm_156','R2-12-47-2_tm_157','R2-12-47-2_tm_158','R2-12-47-2_tm_159','R2-12-47-2_tm_160','R2-12-47-2_tm_161','R2-12-47-2_tm_162','R2-12-47-2_tm_163','R2-12-47-2_tm_164','R2-12-47-2_tm_165','R2-12-47-2_tm_166','R2-12-47-2_tm_167','R2-12-47-2_tm_168','R2-12-47-2_tm_169','R2-12-47-2_tm_170','R2-12-47-2_tm_171','R2-12-47-2_tm_172','R2-12-47-2_tm_173','R2-12-47-2_tm_174','R2-12-47-2_tm_175','R2-12-47-2_tm_176','R2-12-47-2_tm_177','R2-12-47-2_tm_178','R2-12-47-2_tm_179','R2-12-47-2_tm_180','R2-12-47-2_tm_181','R2-12-47-2_tm_182','R2-12-47-2_tm_183','R2-12-47-2_tm_184','R2-12-47-2_tm_185','R2-12-47-2_tm_186','R2-12-47-2_tm_187','R2-12-47-2_tm_188','R2-12-47-2_tm_189','R2-12-47-2_tm_190','R2-12-47-2_tm_191','R2-12-47-2_tm_192'],
		'regulatorNames':['R2-12-47-2_reg_1','R2-12-47-2_reg_2'],
		'regulatorReadInterval':'450',
		'switchNames':['R2-12-47-2_switch_1','R2-12-47-2_switch_2','R2-12-47-2_switch_3','R2-12-47-2_switch_4','R2-12-47-2_switch_5','R2-12-47-2_switch_6','R2-12-47-2_switch_7','R2-12-47-2_switch_8','R2-12-47-2_switch_9','R2-12-47-2_switch_10','R2-12-47-2_switch_11','R2-12-47-2_switch_12'],
		'controlActions':[
			{'identifier':'MS-IniateDisconnectConnect','parent':'R2-12-47-2_tm_141','property':'service_status','schedule':'2009-01-01 12:30:00,0'},
			{'identifier':'DNP-SubstationBreakerSwitchWrite','parent':'R2-12-47-2_switch_7','property':'phase_A_state','schedule':'2009-01-01 12:30:00,0'},
			{'identifier':'DNP-SubstationVoltageControl','parent':'R2-12-47-2_reg_2','property':'tap_A','schedule':'2009-01-01 12:00:00,2;2009-01-01 12:15:00,1;2009-01-01 12:45:00,2'}
		],
	},
	'postProc': {
		'dosList':[{'device_name':'R2-12-47-2_reg_2','start':'2009-01-01 12:07:00','end':'2009-01-01 12:16:00'}],
		'spoofList':[{'device_name':'R2-12-47-2_tm_141','type':'alarm','quantity':5,'start':'2009-01-01 12:20:00','end':'2009-01-01 12:40:00'}],
		'modList':[]
	}
}


def dig(inputDict):
	''' Run full ratDigest workflow.'''
	out = pre(inputDict)
	attackedOut = post(inputDict, out)

def pre(inDict):
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
	for meterName in inDict['preProc']['meterNames']:
		tempTemplate = str(recorderTemplate)
		tempTemplate = tempTemplate.replace('INSERT_FILE_NAME', FILE_UID + '_METER_' + meterName)
		tempTemplate = tempTemplate.replace('INSERT_INTERVAL', inDict['preProc']['meterReadInterval'])
		tempTemplate = tempTemplate.replace('INSERT_PARENT', meterName)
		tempTemplate = tempTemplate.replace('INSERT_PROPERTIES', 'measured_real_energy, measured_real_power, measured_reactive_power, measured_voltage_1, measured_voltage_2')
		allRecorders += tempTemplate
	for regName in inDict['preProc']['regulatorNames']:
		tempTemplate = str(recorderTemplate)
		tempTemplate = tempTemplate.replace('INSERT_FILE_NAME', FILE_UID + '_REG_' + regName)
		tempTemplate = tempTemplate.replace('INSERT_INTERVAL', inDict['preProc']['regulatorReadInterval'])
		tempTemplate = tempTemplate.replace('INSERT_PARENT', regName)
		tempTemplate = tempTemplate.replace('INSERT_PROPERTIES', 'power_out_A, power_out_B, power_out_C, current_out_A, current_out_B, current_out_C, tap_A, tap_B, tap_C')
		allRecorders += tempTemplate
	for switchName in inDict['preProc']['switchNames']:
		tempTemplate = str(recorderTemplate)
		tempTemplate = tempTemplate.replace('INSERT_FILE_NAME', FILE_UID + '_SWITCH_' + switchName)
		tempTemplate = tempTemplate.replace('INSERT_INTERVAL', inDict['preProc']['regulatorReadInterval'])
		tempTemplate = tempTemplate.replace('INSERT_PARENT', switchName)
		tempTemplate = tempTemplate.replace('INSERT_PROPERTIES', 'phase_A_state, phase_B_state, phase_C_state')
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
	# Run the new GLM.
	with open(FILE_UID + '_xstdout.txt','w') as stdout, open(FILE_UID + '_xstderr.txt','w') as stderr:
		proc = subprocess.Popen(['gridlabd','ratDigest.glm'], stdout=stdout, stderr=stderr)
		returnCode = proc.wait()
	#######################################################
	# Turn GridLAB-D output CSV data in to a message list #
	#######################################################
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
					.replace('ratDigest_METER_','')\
					.replace('ratDigest_REG_','')\
					.replace('ratDigest_SWITCH_','')
				# Add identifiers for Phil Craig.
				if fName.startswith(FILE_UID + '_METER_'):
					ident = 'MS-GetLatestReadings'
				elif fName.startswith(FILE_UID + '_REG_'):
					ident = 'DNP-SubstationKwH'
				elif fName.startswith(FILE_UID + '_SWITCH_'):
					ident = 'DNP-SubstationBreakerSwitchStatus'
				else:
					ident = 'unknown'
				# Add voltages to regulator readings.
				if message.get('device_name','') in smallInput['preProc']['regulatorNames']:
					for phase in ['A','B','C']:
						power = complex(message.get('power_out_' + phase))
						current = complex(message.get('current_out_' + phase))
						if current==0:
							message['voltage_' + phase] = str(complex(0))
						else:
							message['voltage_' + phase] = str(power/current)
				# Also make a message to request each reading.
				reqMessage = {
					'device_name':message['device_name'],
					'timestamp':message['timestamp'],
					'identifier': ident
				}
				# Add a little latency to the responses:
				latencySeconds =  random.randint(0,inDict['preProc']['responseLatencySeconds'])
				stampPlusLatency = tParse(message['timestamp']) + timedelta(seconds=latencySeconds)
				message['timestamp'] = str(stampPlusLatency) + tzc
				message['identifier'] = ident + '-RESPONSE'
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
				'identifier':action['identifier']
			}
			output.append(outMessage)
	# Process alarms.
	for meterName in inDict['preProc']['meterNames']:
		voltProblem = False
		for step in alarmReads:
			voltage = complex(step[meterName].replace('d','j'))
			voltageMag = abs(voltage)/120.0
			stamp = step['timestamp']
			noVolts = (voltageMag > 1.15 or voltageMag < 0.85)
			if not voltProblem and noVolts:
				# New voltage problem.
				alarmMessage = {
					'location':meterName,
					'identifier':'MS-ODEventNotification',
					'type':'voltage alarm',
					'timestamp':stamp,
					'magnitude':str(voltageMag)
				}
				output.append(alarmMessage)
				voltProblem = True
			elif voltProblem and not noVolts:
				# Voltage problem resolved.
				restoreMessage = {
					'location':meterName,
					'identifier':'MS-ODEventNotification',
					'type':'voltage restoration',
					'timestamp':timestamp + tzc
				}
				output.append(restoreMessage)
				voltProblem = False
			else:
				continue
	# Write full output.
	with open(FILE_UID + 'PreAttack.json','w') as outFile:
		json.dump(output, outFile, indent=4)
	# Also return output for post processing.
	return output

def post(inDict, messages):
	# Short timezone coda for things missing it.
	tzc = ' ' + inDict['preProc']['timezone'][0:3]
	# Perform DOS attacks by dropping messages.
	deleteList = []
	for attack in inDict['postProc']['dosList']:
		start = tParse(attack['start'] + tzc)
		end = tParse(attack['end'] + tzc)
		for message in messages:
			time = tParse(message['timestamp'])
			rightTime = start < time < end
			rightDevice = (attack['device_name'] == message.get('device_name',''))
			if rightTime and rightDevice:
				deleteList.append(message)
	for message in deleteList:
		messages.remove(message)
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
				'fake':'True'
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
				prop = message[attack['property']]
				# Perform complex affine transform.
				newProp = str(complex(prop) * complex(attack['multiply']) + complex(attack['add']))
				message[attack['property']] = newProp
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
	dig(smallInput)
	# dig(largeInput)

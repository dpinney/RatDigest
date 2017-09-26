'''RatDigest Makes Network Messages From GridLAB-D Simulations.'''

import os, subprocess, csv, json, random
from datetime import datetime, timedelta

testInput = {
	'glmDirPath':'./littleTest/',
	'glmName':'smsSingle.glm',
	'preProc': {
		'startTime':'2017-01-01 12:00:00',
		'stopTime':'2017-01-01 13:00:00',
		'simTimeStep':'4',
		'meterReadInterval':'900',
		'meterNames':['tm_1','tm_2'],
		'meterLoadMap':{'house1':'tm_1','house2':'tm_2'},
		'regulatorNames':['Reg1'],
		'regulatorReadInterval':'450',
		'switchNames':['newSwitch'],
		'controlActions':[
			{'identifier':'MS-IniateDisconnectConnect','parent':'tm_1','property':'service_status','schedule':'2017-01-01 12:30:00 PST,0'},
			{'identifier':'DNP-SubstationBreakerSwitchWrite','parent':'newSwitch','property':'phase_A_state','schedule':'2017-01-01 12:30:00 PST,0'},
			{'identifier':'DNP-SubstationVoltageControl','parent':'Reg1','property':'tap_A','schedule':'2017-01-01 12:00:00 PST,2;2017-01-01 12:15:00 PST,1;2017-01-01 12:45:00 PST,2'},
			{'identifier':'INTENTIONAL_FAULT','parent':'bigload','property':'base_power','schedule':'2017-01-01 12:45:00 PST,60.0 kW'}
		],
	},
	'postProc': {
		'dosList':[{'device':'Reg1','start':'2017-01-01 12:07:00 PST','end':'2017-01-01 12:16:00 PST'}],
		'floodList':[{'device':'tm_2','type':'alarm','quantity':5,'start':'2017-01-01 12:20:00 PST','end':'2017-01-01 12:40:00 PST'}],
	}
}

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
		'\ttimezone PST+8PDT;\n' +\
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
	allPlayers = 'class player {double value;};\n\n'
	allRecorders = ''
	# Modify templates to reflect input parameters.
	timeTemplate = timeTemplate.replace('INSERT_START_TIME',inDict['preProc']['startTime'])
	timeTemplate = timeTemplate.replace('INSERT_STOP_TIME',inDict['preProc']['stopTime'])
	timeTemplate = timeTemplate.replace('INSERT_TIME_STEP',inDict['preProc']['simTimeStep'])
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
			for row in reader:
				row['device_name'] = fName
				# Add identifier for Phil Craig
				if fName.startswith(FILE_UID + '_METER_'):
					row['identifier'] = 'MS-GetLatestReadings'
				elif fName.startswith(FILE_UID + '_REG_'):
					row['identifier'] = 'DNP-SubstationKwH'
				elif fName.startswith(FILE_UID + '_SWITCH_'):
					row['identifier'] = 'DNP-SubstationBreakerSwitchStatus'
				else:
					row['identifier'] = 'unknown'
				output.append(row)
	# Add control messages to output.
	for action in inDict['preProc']['controlActions']:
		for event in action['schedule'].split(';'):
			(timestamp, value) = event.split(',')
			outMessage = {
				'device_name':action['parent'],
				'control_variable':action['property'],
				'value': value,
				'timestamp':timestamp,
				'identifier':action['identifier']
			}
			output.append(outMessage)
	# Add alarms to output.
	with open(FILE_UID + '_xstderr.txt') as errFile:
		lines = errFile.read().split('\n')
		for x in lines:
			if "is outside of ANSI standards" in x:
				out = {}
				out['identifier'] = 'MS-ODEventNotification'
				out['type'] = 'voltage alarm'
				rawLocation = x[x.find(' : ') + 3:x.find(' - ')]
				out['location'] = inDict['preProc']['meterLoadMap'][rawLocation]
				magnitude = x[x.find(' = ') + 3 :x.find(' percent')]
				out['magnitude'] = str(float(magnitude)/100.0 * 120.0)
				out['timestamp'] = x[10:33]
				output.append(out)
	# Write full output.
	with open(FILE_UID + 'PreAttack.json','w') as outFile:
		json.dump(output, outFile, indent=4)
	# Also return output for post processing.
	return output

def post(inDict, messages):
	# Helper function for timestamp parsing.
	def tParse(timeString):
		return datetime.strptime(timeString[0:-4], '%Y-%m-%d %H:%M:%S')
	# Helper function for random dates in a range.
	def randomDate(start, end):
		delta = end - start
		int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
		random_second = random.randrange(int_delta)
		return start + timedelta(seconds=random_second)
	# Perform DOS attacks by dropping messages.
	for attack in inDict['postProc']['dosList']:
		start = tParse(attack['start'])
		end = tParse(attack['end'])
		for message in messages:
			time = tParse(message['timestamp'])
			if start < time < end:
				del message
	# Perform flood attacks.
	for attack in inDict['postProc']['floodList']:
		start = tParse(attack['start'])
		end = tParse(attack['end'])
		if attack['type'] is 'alarm':
			underVoltage = random.randrange(95.0,110.0)
			overVoltage = random.randrange(130.0,145.0)
			magnitude = random.choice([underVoltage,overVoltage])
			messageTemplate = {
				'identifier': 'MS-ODEventNotification', 
				'type': 'voltage alarm', 
				'location': attack['device'], 
				'magnitude': str(magnitude),
				'fake':'True'
			}
		else:
			raise Exception('No type specified for attack ' + str(attack))
		for count in xrange(attack['quantity']):
			fakeMessage = dict(messageTemplate)
			fakeMessage['timestamp'] = datetime.strftime(randomDate(start, end), '%Y-%m-%d %H:%M:%S PST')
			messages.append(fakeMessage)
	# Dump results.
	with open('ratDigestPostAttack.json','w') as outFile:
		json.dump(messages, outFile, indent = 4)
	# And return as well.
	return messages

if __name__ == '__main__':
	out = pre(testInput)
	attackedOut = post(testInput, out)

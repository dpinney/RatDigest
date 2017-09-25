'''RatDigest Workflow'''

import os, subprocess, csv, json
from pprint import pprint

exampleInput = {
	'glmDirPath':'./littleTest/',
	'glmName':'smsSingle.glm',
	'preProc': {
		'startTime':'2017-01-01 12:00:00',
		'stopTime':'2017-01-01 13:00:00',
		'timeStep':'4',
		'meterReadInterval':'900',
		'meterNames':['tm_1','tm_2'],
		'regulatorNames':['Reg1'],
		'regulatorReadInterval':'4',
	},
	'postProc': {
		'voltAlarmMin':110,
		'voltAlarmMax':130,
		'powerAlarmMin':0,
		'powerAlarmMax':9000,
		'probMessageSend':0.99
	}
}

def go(inDict):
	#################################################
	# PREPROCESS to create and run a new .glm file. #
	#################################################
	FILE_UID = 'ratDigest'
	# Templates used to rewrite .glm:
	timeTemplate = 'clock {\n' +\
		'\ttimezone PST+8PDT;\n' +\
		"\tstarttime 'INSERT_START_TIME';\n" +\
		"\tstoptime 'INSERT_STOP_TIME';\n" +\
		'\t};\n' +\
		'#set minimum_timestep=INSERT_TIME_STEP;\n'
	allRecorders = ''
	recorderTemplate = 'object recorder {' +\
		'\tfile INSERT_FILE_NAME.csv;\n' +\
		'\tinterval INSERT_INTERVAL;\n' +\
		'\tparent INSERT_PARENT;\n' +\
		'\tproperty INSERT_PROPERTIES;\n' +\
		'};\n'
	# Modify templates to reflect input parameters.
	timeTemplate = timeTemplate.replace('INSERT_START_TIME',inDict['preProc']['startTime'])
	timeTemplate = timeTemplate.replace('INSERT_STOP_TIME',inDict['preProc']['stopTime'])
	timeTemplate = timeTemplate.replace('INSERT_TIME_STEP',inDict['preProc']['timeStep'])
	for meterName in inDict['preProc']['meterNames']:
		tempTemplate = str(recorderTemplate)
		tempTemplate = tempTemplate.replace('INSERT_FILE_NAME', FILE_UID + '_METER_' + meterName)
		tempTemplate = tempTemplate.replace('INSERT_INTERVAL', inDict['preProc']['meterReadInterval'])
		tempTemplate = tempTemplate.replace('INSERT_PARENT', meterName)
		tempTemplate = tempTemplate.replace('INSERT_PROPERTIES', 'measured_real_energy, measured_real_power, measured_reactive_power, measured_voltage_1, measured_voltage_2')
		allRecorders += (tempTemplate)
	for regName in inDict['preProc']['regulatorNames']:
		tempTemplate = str(recorderTemplate)
		tempTemplate = tempTemplate.replace('INSERT_FILE_NAME', FILE_UID + '_REG_' + regName)
		tempTemplate = tempTemplate.replace('INSERT_INTERVAL', inDict['preProc']['regulatorReadInterval'])
		tempTemplate = tempTemplate.replace('INSERT_PARENT', regName)
		tempTemplate = tempTemplate.replace('INSERT_PROPERTIES', 'power_out_A, power_out_B, power_out_C, current_out_A, current_out_B, current_out_C, tap_A, tap_B, tap_C')
		allRecorders += (tempTemplate)
	# Remove old outputs.
	for fName in os.listdir(inDict['glmDirPath']):
		try:
			os.remove(fName)
		except:
			pass # tried but couldn't delete old output.
	# Modify and write the new GLM.
	glmContent = open(inDict['glmDirPath'] + inDict['glmName'],'r').read()
	glmContent = timeTemplate + glmContent + allRecorders
	with open(inDict['glmDirPath'] + FILE_UID + '.glm', 'w') as outFile:
		outFile.write(glmContent)
	# Run the new GLM.
	os.chdir(inDict['glmDirPath'])
	proc = subprocess.Popen(['gridlabd', FILE_UID + '.glm'], stderr=None, stdout=None)
	proc.wait()
	#########################################################
	# POSTPROCESS to turn the CSV data in to a message list #
	#########################################################
	allFileNames = os.listdir('.')
	csvFileNames = [x for x in allFileNames if x.startswith(FILE_UID) and x.endswith('.csv')]
	output = []
	for fName in csvFileNames:
		with open(fName,'r') as inFile:
			# Burn the first 8 lines which are just metadata.
			for x in xrange(8):
				inFile.readline()
			# Headers are in line 9.
			headers = inFile.readline()
			headList = headers[2:].replace('\n','').split(',')
			reader = csv.DictReader(inFile, fieldnames=headList)
			for row in reader:
				row['device_name'] = fName
				output.append(row)
	with open(FILE_UID + '.json','w') as outFile:
		json.dump(output, outFile, indent=4)

if __name__ == '__main__':
	go(exampleInput)

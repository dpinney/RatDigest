'''RatDigest Workflow'''

input = {
	'pathToGlm':'./littleTest/smsSingle.glm',
	'preProc': {
		'startTime':'2017-01-01 00:00',
		'endTime':'2017-01-02 00:00',
		'timeStep':4
	},
	'postProc': {
		'voltAlarmMin':110,
		'voltAlarmMax':130,
		'powerAlarmMin':0,
		'powerAlarmMax':9000,
		'probMessageSend':0.99
	}
}

CONSTANTS = {
	'meterReadInterval':15*60
}

output = [
	{'deviceId':'blah','metricA':34}
]

def go(input):
	#preProc: modify glm file
	#runGld: just run it
	#postProc: take csvs, make nice output
	pass

if __name__ == '__main__':
	print 'hay'

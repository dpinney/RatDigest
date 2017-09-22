import os, urllib2, subprocess, time

# HACK: get in the directory so GridLAB-D's includes work (sigh).
os.chdir('RADICS-Ex2-GLD-Models')

# Start servert in server mode, note that the .glm has pauseat set for 1 day in to the simulation.
proc = subprocess.Popen(['gridlabd','RADICS_substation_model.glm','--quiet','--server','-P','6267'],stderr=None, stdout=None)

# Hack: wait for the dang server to start up and load the model.
time.sleep(60)

try:
	# Read the clock and a meter.
	print urllib2.urlopen('http://localhost:6267/clock').read()
	print urllib2.urlopen('http://localhost:6267/tpm3_C1_R2-12-47-2_tm_56/measured_power').read()
	# Step the simulation.
	urllib2.urlopen('http://localhost:6267/control/pauseat=2009-07-01%2009:00:30').read()
	print 'Stepped ahead to 30 seconds.'
	time.sleep(30) # Hack: give the simulation some time to run.
	# Get the value and clock again.
	print urllib2.urlopen('http://localhost:6267/clock').read()
	print urllib2.urlopen('http://localhost:6267/tpm3_C1_R2-12-47-2_tm_56/measured_power').read()
	# Set a value.
	urllib2.urlopen('http://localhost:6267/COSIM_LOAD_HACK/base_power=6000').read()
	# Step again.
	urllib2.urlopen('http://localhost:6267/control/pauseat=2009-07-01%2009:00:59').read()
	print 'Stepped ahead to 59 seconds.'
	time.sleep(30) # Hack: give the simulation some time to run.
	print urllib2.urlopen('http://localhost:6267/clock').read()
	print urllib2.urlopen('http://localhost:6267/tpm3_C1_R2-12-47-2_tm_56/measured_power').read()
	# Finish out the simulation.
	urllib2.urlopen('http://localhost:6267/control/resume').read()

except:
	pass # server being weird.

# Stop the simulation.
try:
	urllib2.urlopen('http://localhost:6267/control/shutdown')
except:
	pass # should be shut down now.
print proc.stdout
# proc.kill() # For those hard-to-stop servers.

#!/usr/bin/python
import sys
import getopt
import os
import json

dir_path = os.path.dirname(os.path.realpath(__file__))

cliOpts = 'hp:'
cliLongOpts = ['help',
               'testcaseid=',
               'logdir=',
               'testbedjson='
               ]

testcaseid = None
logdir = None
testbedjson = None
cmd = None


def usage():
    print("Usage: %s [-h,--help]" % os.path.basename(sys.argv[0]))


try:
    opts, args = getopt.getopt(sys.argv[1:], cliOpts, cliLongOpts)
    for opt, value in opts:
        if opt in ('-h', '--help'):
            usage()
            sys.exit(2)
        elif opt in ('--testcaseid',):
            testcaseid = value
        elif opt in ('--logdir',):
            logdir = value
        elif opt in ('--testbedjson',):
            testbedjson = value

except getopt.GetoptError as e:
    print(sys.stderr, "%s\n" % e)
    usage()
    sys.exit(2)
except Exception as e:
    print(sys.stderr, "Error parsing command arguments: %s" % e)
    sys.exit(1)

resp_json = json.loads(testbedjson)
print(testcaseid)
print(logdir)
print(testcaseid)
print(resp_json)

deviceId = resp_json['device'][0]['SerialNumber'][0]
appiumIp = resp_json['device'][0]['appiumIp'][0]
appiumPort = resp_json['device'][0]['appiumPort'][0]
junitxml = str(logdir) + "/" + str(testcaseid) + ".out.xml"
pytesthtml = str(logdir) + "/" + str(testcaseid) + ".html"

cmd = "python -m pytest " + dir_path + " -k test_" + str(testcaseid) + "_" +\
      " --device_id " + str(deviceId) + \
      " --log_path " + str(logdir) + \
      " --hub " + "http://" + str(appiumIp) + ":" + str(appiumPort) + "/wd/hub" + \
      " --junitxml " + junitxml + \
      " --appium_ip " + appiumIp + \
      " --testcaseid " + str(testcaseid) + \
      " --tb short"

print(cmd)
os.system(cmd)

f = open(junitxml).read()

if 'test setup failure' in f:
    print("ABORT")
    sys.exit(2)
elif 'failure message' in f:
    print("FAILURE")
    sys.exit(5)
elif 'error message' in f:
    print("FAILURE")
    sys.exit(5)
else:
    print("SUCCESS")
    sys.exit(0)

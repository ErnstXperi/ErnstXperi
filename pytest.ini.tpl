# Content of pytest.ini, pytest reads this test configuration while executing the tests,
# Content of these values will be overridden if command line values are passed

## Command Line options:
## AppleTV
#   python3 -m pytest /sandbox/d-alviso/autotestscripts/CAT/UTAF/set_top_box/ -v -s --junitxml ./test_result.out.xml --html ./test_result.html --tb short \
#           --device_ip  10.101.119.39 --port 12345 --driver_type  appletv  --tsn A8F000007F440D2 --mso cabelco3 --platform appletv --log-level=DEBUG
## AndroidTV devices
#   python3 -m pytest /sandbox/d-alviso/autotestscripts/CAT/UTAF/set_top_box/ -v-s --junitxml ./test_result.out.xml --html ./test_result.html --tb short \
#           --device_id  192.168.1.2:5555 --appium_ip 192.168.1.9 --driver_type  appium  --tsn A8F000007F440D2 --mso cabelco3 --platform appletv
#           --hub http://192.168.1.9:4723/wd/hub --app_package com.tivo.ccunmanag --log-level=DEBUG
## DevHost
#   python3 -m pytest /sandbox/d-alviso/autotestscripts/CAT/UTAF/set_top_box/ -v -s --junitxml ./test_result.out.xml --html ./test_result.html --tb short \
#           --device_ip  127.0.1.1 --port 12345 --driver_type  appletv  --tsn A8F000007F440D2 --mso cabelco3 --platform appletv --log-level=DEBUG

[pytest]
# pytest  options
addopts = -v --junitxml ./test_result.out.xml --html ./test_result.html --tb short --log-level=DEBUG

# user  options, all are sample values, change values as needed
# [appletv]
driver_type = appletv
port = 12345
# device_ip = 10.100.188.64
device_ip = 10.101.119.39
log_path = .
platform = appletv
mso = cableco3


## copy paste whatever configuration you would like to run in above space.
## Tests will care only under the tag ```[pytest]```
[devhost]
driver_type = appletv
port = 12345
device_ip = 127.0.1.1
log_path = ./
platform = amino
mso = cableco3

[mibox]
device_id = 192.168.1.2:5555
log_path = ./
appium_ip = 192.168.1.9
hub = http://192.168.1.9:4723/wd/hub
platform = mibox
mso = cableco3
tsn = A8F000007F440D2
username = samco2@cableco.com
driver_type = appium
port = 5555
app_package = com.tivo.ccunmanag

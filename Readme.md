# Description

check_idrac.py can be used to query the RedFish API of DELL iDRAC devices and return a Nagios/Naemon conform output.

- The output is HTML formatted

## Help output

```bash
check_idrac.py -h
usage: check_idrac.py [-h] -H HOSTNAME [-U USER] -P PASSWORD [-t TIMEOUT] [--dumpresponse] --mode {health,controller,powersupply,disk,thermal,memory,dellsystem,version}

Check DELL iDRAC Management Controllers

options:
  -h, --help            show this help message and exit
  -H HOSTNAME, --hostname HOSTNAME
                        HOSTNAME or IP of target device
  -U USER, --user USER  Monitoring user
  -P PASSWORD, --password PASSWORD
                        Monitoring user password
  -t TIMEOUT, --timeout TIMEOUT
                        Timeout in seconds
  --dumpresponse        Dump the response into a <mode>_response.json file.
  --mode {health,controller,powersupply,disk,thermal,memory,dellsystem,version}
                        Select the mode you want..

Checking status of DELL iDRAC management controllers
```

## Example Output

### Mode health

```html
OK: 12/12 component(s) are healthy. 0 without status.
<table><tr><th>Component</th><th>Category</th><th>Health</th></tr><tr><td>iDRAC.Embedded.1#SubSystem.1#Voltage</td><td>Voltage</td><td style="background-color:#23a34e">OK</td></tr><tr><td>iDRAC.Embedded.1#SubSystem.1#Current</td><td>Current</td><td style="background-color:#23a34e">OK</td></tr><tr><td>iDRAC.Embedded.1#SubSystem.1#Intrusion</td><td>Intrusion</td><td style="background-color:#23a34e">OK</td></tr><tr><td>iDRAC.Embedded.1#SubSystem.1#Processor</td><td>Processor</td><td style="background-color:#23a34e">OK</td></tr><tr><td>iDRAC.Embedded.1#SubSystem.1#PowerSupply</td><td>PowerSupply</td><td style="background-color:#23a34e">OK</td></tr><tr><td>iDRAC.Embedded.1#SubSystem.1#Memory</td><td>Memory</td><td style="background-color:#23a34e">OK</td></tr><tr><td>iDRAC.Embedded.1#SubSystem.1#Fan</td><td>Fan</td><td style="background-color:#23a34e">OK</td></tr><tr><td>iDRAC.Embedded.1#SubSystem.1#Temperature</td><td>Temperature</td><td style="background-color:#23a34e">OK</td></tr><tr><td>iDRAC.Embedded.1#SubSystem.1#Battery</td><td>Battery</td><td style="background-color:#23a34e">OK</td></tr><tr><td>iDRAC.Embedded.1#SubSystem.1#Storage</td><td>Storage</td><td style="background-color:#23a34e">OK</td></tr><tr><td>System.Chassis.1#SubSystem.1#Fan</td><td>Fan</td><td style="background-color:#23a34e">OK</td></tr><tr><td>iDRAC.Embedded.1#SubSystem.1#SEL/Misc</td><td>SEL/Misc</td><td style="background-color:#23a34e">OK</td></tr></table>
```

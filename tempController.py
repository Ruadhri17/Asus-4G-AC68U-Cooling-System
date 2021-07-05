# Fan Controller to Asus 4G-AC68U Router using raspberry pi 0 and piOLED display (in progress)#
# Created by Krzysztof Piotrowski #
import sys
from time import sleep
from gpiozero import LED
from paramiko import AutoAddPolicy, SSHClient
from paramiko.ssh_exception import AuthenticationException, BadHostKeyException, SSHException, NoValidConnectionsError

# Host Info #
router_ip = "192.168.1.1" #<Enter your router ip here>
router_port = 22 #<Enter your router ssh port (by default 22)>
router_username = "admin" #<Enter your router login> 
router_password = "admin"#<Enter you router password>

# Fan Info #
fan = LED(16) #Enter pin used to control fan

# Connect via SSH to router #
router_connection = SSHClient()
router_connection.load_system_host_keys()
router_connection.set_missing_host_key_policy(AutoAddPolicy())

# If there will be problem with SSH connection, try again after 10 seconds
while True:
    try:
        router_connection.connect(router_ip, port=router_port, username=router_username, password=router_password, look_for_keys=False)
        print("[CONNECTION]: Succesfully connected to Router!")
        while True:
            try:
                stdin, stdout, stderr = router_connection.exec_command('cat /proc/dmu/temperature') # Asus instruction for displaying CPU temperature
                stdout = stdout.read(20)
                temp = int(stdout[-2:]) # Take only temperature value as integer
                print(temp)
                sleep(3) # Read new value every 3 sec
                if temp > 70: # Turn on fans if temperature exceeds 70 degrees celsius
                    fan.on()
                if temp < 68: # Turn of fans if temperature drop down to 68 degrees
                    fan.off()
            except SSHException: # if connection was dropped, try to establish it again 
                print("[ERROR] Lost Connection! Trying to connect again in 10 sec."); break
    except BadHostKeyException:
        print("[ERROR]: Router's host key could not be verified! Try Again in 10 sec."); sleep(10); continue
    except AuthenticationException:
        print("[ERROR]: Authentication failed! Try again in 10 sec."); sleep(10); continue
    except SSHException:
        print("[ERROR]: There was an Error while connecting or establishing a session! Try again in 10 sec."); sleep(10); continue
    except NoValidConnectionsError:
        print("[ERROR]: Cannot connect to router! Try again in 10 sec."); sleep(10); continue






# Fan Controller to Asus 4G-AC68U/RT-AC68U Router using raspberry pi 0 and piOLED display#
# Created by Krzysztof Piotrowski #
import sys
from busio import I2C
from time import sleep
import adafruit_ssd1306
from gpiozero import LED
from board import SCL, SDA
from PIL import Image, ImageDraw, ImageFont
from paramiko import AutoAddPolicy, SSHClient
from paramiko.ssh_exception import AuthenticationException, BadHostKeyException, SSHException, NoValidConnectionsError

def main():
        # Host Info #
        router_ip = "192.168.1.1"
        router_port = 22
        router_username = "admin"
        router_password = "admin"

        # Fan Info #
        fan = LED(16) # Enter pin used to control fan

        # Init. OLED display #
        i2c = I2C(SCL, SDA)
        display = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)
        display.fill(0)
        display.show()

        # Create image for drawing and set defualt font#
        image = Image.new("1", (display.width, display.height))
        draw = ImageDraw.Draw(image)
        font = ImageFont.load_default()

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
                                        if temp > 70:
                                                fan.on()
                                                fill_screen(draw, display, font, image, temp, "ON", "CONNECTED")
                                        if temp < 68:
                                                fan.off()
                                                fill_screen(draw, display, font, image, temp, "OFF", "CONNECTED")
                                        sleep(3)
                                except SSHException:
                                        print("[ERROR]: Lost Connection! Try to connect again in 10 sec."); fill_screen(draw, display, font, image, "--", "OFF", "ERROR [1]"); break
                except BadHostKeyException:
                        print("[ERROR]: Router's host key could not be verified! Try Again in 10 sec."); fill_screen(draw, display, font, image, "--", "OFF", "ERROR [2]"); sleep(10); continue
                except AuthenticationException:
                        print("[ERROR]: Authentication failed! Try again in 10 sec."); fill_screen(draw, display, font, image, "--", "OFF", "ERROR [3]"); sleep(10); continue
                except SSHException:
                        print("[ERROR]: There was an Error while connecting or establishing a session! Try again in 10 sec."); fill_screen(draw, display, font, image, "--", "OFF", "ERROR [4]"); sleep(10); continue
                except NoValidConnectionsError:
                        print("[ERROR]: Cannot connect to router! Try again in 10 sec."); fill_screen(draw, display, font, image, "--", "OFF", "ERROR [5]"); sleep(10); continue

def fill_screen(pass_draw, pass_display, pass_font, pass_image, temp, fan_status, connection_status):
        pass_draw.rectangle((0, 0, pass_display.width, pass_display.height), outline=0, fill=0)
        pass_draw.text((0, -2), "Temp. Controller", font=pass_font, fill=255)
        pass_draw.text((0, 6), "Temperature: " + temp, font=pass_font, fill=255)
        pass_draw.text((0, 14), "Fans: " + fan_status, font=pass_font, fill=255)
        pass_draw.text((0, 23), "Status: " + connection_status, font=pass_font, fill=255)

        pass_display.image(pass_image)
        pass_display.show()
        sleep(0.1)

if __name__ == '__main__':
        main()

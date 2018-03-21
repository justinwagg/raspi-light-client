# Raspi-light-client

Raspi-light-client is a internet connected LED light. It has two (or more) inputs, and subscribes to a MQTT broker to listen for setting changes. Setting changes are broadcast by the raspi-light-server and controlled in a flask web app.

## Details
The light has a schedule it adheres to, with three modes (on, off, low), during which the light intensity and response to input (PIR sensor) changes.

The client has three time settings, which break the day into three sections:

- off_time (generally daytime)
- on_time (generally evening)
- low_time (generally overnight)

Between these times, the four light intensity settings (low, high, manual, off) combine with inputs (button/PIR) to make a range of light experiences.

- off_time: Light is off unless the button is pressed.
- on_time: Light is low unless PIR is triggered, or button is pressed, after which the light goes high or manual, respectively.
- low_time: Light is off unless PIR is triggered, or button is pressed, after which the light goes low, or manual, respectively.



## Getting Started
From scratch, you'll need a new formatted SD card, a raspberry pi with internet connectivity, and a little creativity.

### Flash SD Card
1. Format new Raspian SD card
Following [raspberrypi.org's documentation]( https://www.raspberrypi.org/documentation/installation/installing-images/mac.md) will be helpful in the next step.
[Download](https://www.raspberrypi.org/downloads/raspbian/) the Raspian image and move to your SD card. From the terminal, having found your SD card mount point:
```
sudo dd bs=1m if=/path/to-your-image.img of=/dev/rdiskn conv=sync
```

1. Once the image is transferred, you'll want to setup headless access. Create a file in `boot` on the SD Card named `wpa_supplicant.conf` with the contents below. Change `SSID` and `PASS` to be your local credentials.

	```
	ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
	update_config=1
	country=US

	network={
		ssid="SSID"
		psk="PASS"
		key_mgmt=WPA-PSK
	}
	```

1. To enable SSH (default is not enabled) create an empty file `ssh.txt` in same directory.
1. Boot your RasberryPi.
1. After a minute or so the image should boot and gain access to your provided network SSID.

### Connect to your Raspberry Pi
Replace the IP shown with your own modules IP. Checking your router for attached devices might expedite the processes.

```
ssh pi@192.168.1.55
pi@192.168.1.55's password:
```



##### Install PiGPIO

pigpio is a library for the Raspberry which allows control of the General Purpose Input Outputs (GPIO).

Download & Install - Source: http://abyz.me.uk/rpi/pigpio/download.html

Start pigpio and run on boot:

```
sudo crontab -e
@reboot  /usr/local/bin/pigpiod
```
For our purposes, we can launch it now by running `sudo pigpiod`

##### Setup Project Requirements

Install requirements.

```
sudo apt-get update
sudo apt-get install python-pip git netatalk sqlite3
sudo pip install virtualenv
```

##### Setup GitHub Access
Get a public key, add to GitHub, and clone the repo.

```
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
cat /home/pi/.ssh/id_rsa.pub
cd
cd mkdir Projects
cd Projects
git clone git@github.com:justinwagg/raspi-light-client.git
```
##### Setup Virtualenv

```
cd raspi-light-client
virtualenv venv
venv/bin/pip install -r requirements.txt
```

##### Build settings database

```
cd setup
python create_database.py
```

##### Test
Test run should succeed. Logging and terminal printing is available for debugging.

Run `venv/bin/python main.py`

If successful, setup a cronjob to launch the client on boot.

```
sudo crontab -e
@reboot sh /path/to/folder/launcher.sh > /path/to/folder/cronlog 2>&1
```

### Notes:
#### MQTT & Settings
Default settings are created when running `python setup/create_database.py`, but new settings can be passed to the client by sending a messages to the subscribed to topic in `config.py`. Raspi-light-server usually accomplishes this task, but a broker running on any server publishing ot the topic will do. The client expects a dictionary of settings in the form:

```
{
"off_time": "07:30:00",
"on_time": "17:00:00",
"low_time": "23:30:00",
"low": 30,
"high": 75,
"manual": 100,
"submit": true,
"device": 1,
}
```

#### Localization

Remember to change the localization settings of your Raspberry Pi
`sudo raspi-config`

### To Do
- Rate limit settings changes, publisher could go wild with messages, no protection against this currently.
- Increase in number of inputs
- More flexible combination of timing/lighting
- Upload schematics/hardware design

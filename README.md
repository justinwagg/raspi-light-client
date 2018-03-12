# Raspi-light-client

A connected LED light. Works in unison with Raspi-light-server, a Flask app interface.

## Getting Started
From scratch, you'll need a new formatted SD card, a raspberry pi with internet connectivity, and a little creativity.

### From Scratch
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
	```
	```
network={
	ssid="SSID"
	psk="PASS"
	key_mgmt=WPA-PSK
}
	```

1. Create an empty file `ssh.txt` in same directory.
1. Boot your RasberryPi.
1. After a minute or so the image should boot and gain access to your provided network SSID.

	```
ssh pi@192.168.1.55
pi@192.168.1.55's password:

	```
1. [Install pigpio](http://abyz.me.uk/rpi/pigpio/download.html). Setup to run pigpio daemon at startup:

	```
sudo crontab -e
@reboot  /usr/local/bin/pigpiod
	```

1. Get project requirements setup

	```
sudo pip install virtualenv
sudo apt-get install netatalk
sudo apt-get install sqlite3
mkdir Projects
cd Projects
git clone git@github.com:justinwagg/raspi-light-client.git
	```

1. Create virtualenv for project and install requirements
	
	```
cd raspi-light-client
virtualenv venv
pip install -r requirements.txt
	```

1. Build the intitial settings database. A default row will be inserted.

	```
cd setup
python create_database.py
```

1. Setup a cronjob to launch the client on boot. 

	```
sudo crontab -e
@reboot sh /path/to/folder/launcher.sh > /path/to/folder/cronlog 2>&1
	```

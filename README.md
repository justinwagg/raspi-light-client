# Raspi-light-client

A remote, MQTT connected, node controlling LED lights. Together with a mosquitto server lighting becomes fully automated. 


## Getting Started

#### Format new Raspian SD card 
Following [raspberrypi.org's documentation]( https://www.raspberrypi.org/documentation/installation/installing-images/mac.md) through this process proves useful.

[Download and copy](https://www.raspberrypi.org/downloads/raspbian/) the disk image to your formatted SD card.
```
sudo dd bs=1m if=pathofyour_image.img of=/dev/rdiskn conv=sync
```

#### Settting up headless access 
Create a file in `boot` on the SD Card named `wpa_supplicant.conf` with the contents below. Change `SSID` and `PASS` to be your logical credentials.

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

Also, create an empty file `ssh.txt` in same directory.

Boot your RasberryPi.

#### SSH

After a minute or so the image should boot and gain access to your provided network SSID.

```
ssh pi@192.168.1.55
pi@192.168.1.55's password:

```
#### PIGPIO
Once in, you can begin installing the rest of the program.

[Install pigpio](http://abyz.me.uk/rpi/pigpio/download.html). 

Setup to run pigpio daemon at startup:

```
sudo crontab -e>># Add to cron job
@reboot  /usr/local/bin/pigpiod
```

Get project requirements setup

```
sudo pip install virtualenv
sudo apt-get install netatalk
sudo apt-get install sqlite3
mkdir Projects
cd Projects
git clone git@github.com:justinwagg/raspi-light-client.git
```

Create virtualenv for project and install requirements

```
cd raspi-light-client
virtualenv venv
pip install -r requirements.txt
```

#### build the intitial settings database
```
cd setup
python create_database.py
```
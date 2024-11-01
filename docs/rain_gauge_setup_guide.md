# Acoustic Rain Gauge Setup Guide

## Hardware Setup
- Use Raspberry Pi 4 as board 
- Insert SD Card
- Connect USB Microphone and LAN
- Connect Davis to GPIO pin number 13 and ground (optional)

## Software Setup
### 1. Install Ubuntu Server 22.04.4 LTS (64-bit) using **Raspberry Pi Imager** Software
![screenshot_1](../images/screenshot_1.png)

### 2. Enable SSH Settings, give user credentials and WiFi credentials
![screenshot_2](../images/screenshot_2.png)
![screenshot_3](../images/screenshot_3.png)
![screenshot_4](../images/screenshot_4.png)

### 3. Flash the operating system and boot the Raspberry Pi

### 4. Check IP is getting assigned in Ethernet and Wifi

```bash
ip -br a
```
Both Ethernet and Wifi should be UP and IP should be assigned

### 5. Update and upgrade OS

```bash
sudo apt update
sudo apt upgrade
sudo reboot
```

### 6. Clone project repository and setup environment

```bash
# clone repo
git clone https://github.com/cksajil/rainfall_monitor.git

# Set executable permission for setup.sh
chmod a+x rainfall_monitor/src/setup.sh

# run setup.sh
bash rainfall_monitor/src/setup.sh
```

### 7. Check audio recording system

* Check in command line if microphone is detected
```bash
lsusb
```
This will list out all the USB devices connected to Raspberry Pi. To make sure that microphone is getting detected run the above command without connecting microphone and see the output. Repeat the same after connecting the microphone. Now the microphone or soundcard name should appear in the list as an additional entry.

* Check if $arecord$ command lists the input devices
```bash
arecord -l
```
* Reboot the Raspberry Pi
```bash
sudo reboot
```

### 8. After rebooting check if $arecord$ command is working
```bash
# Records a 5 second test audio as wav file
arecord --duration=5 sample.wav

# Delete the test file
rm sample.wav
```
### 9. Enable I2C (for moisture sensor) and UART (for battery monitoring) communication and Reboot
```bash
sudo raspi-config
# interfacing options >> I2C >> yes
# interfacing options >> serial port >> no >> yes
sudo reboot
```
### 10. Connect and Setup ADS1115 ADC Module and Grove moisture sensor to Raspberry Pi 4

#### Hardware mapping 

| ADC1115 | Physical Pin                 | Grove Sensor        |
|---------|------------------------------|---------------------|
| VDD     | 5V                           | VCC                 |
| GND     | GND                          | GND                 |
| SCL     | 5 (SCL.1)                    |                     |    
| SDA     | 3 (SDA.1)                    |                     |
| ADDR    | GND                          |                     |    
| A0      |                              | Grove Sensor output |

####  Check if I2C device is detected
```bash
i2cdetect -y 1
```
### 11. Connect and setup battery monitoring
#### Hardware mapping

* optocoupler connection diagram can be seen [here](https://github.com/cksajil/rainfall_monitor/blob/gitlab/docs/images/optocupler%20conectin.png)
* optocoupler pinout can be seen [here](https://github.com/cksajil/rainfall_monitor/blob/gitlab/docs/images/opto%20coupler.png)

| Pi physical Pin       | optocoupler | solar charge controlller |
|-----------------------|-------------|--------------------------|
|                       | 1           | TX (via 470ohm resistor) |
|                       | 2           | GND                      |
| 10 (GPIO 15-RX)       | 3           |                          |
| 39 (GND) via 470ohm R | 3           |                          |
| 1 (3.3v)              | 4           |                          |
   
### 12. Connect and Setup RFM95 Module to Raspberry Pi 4
#### Hardware mapping 

The complete WiringPi pin mapping can be seen [here](https://raw.githubusercontent.com/cksajil/rainfall_monitor/gitlab/src/lmic_rpi/raspberry_pi_wiring_gpio_pins.png) 
| WiringPi Pin | Function        | Physical Pin    |
|--------------|-----------------|-----------------|
| 0            | Reset           | 11              |
| 4            | DIO0            | 16              |
| 5            | DIO1            | 18              |
| 1            | DIO2 (Not used) | 12              |      
| 12           | MOSI            | 19              |
| 13           | MISO            | 21              |
| 14           | SCK             | 23              |
| 6            | SS              | 22              |     
| 25           | LORAWAN LED     | 37              |
| GND          | GND             | 39              |
| 3.3V         | +3.3V           | 1               |

#### Install the WiringPi library 

The [WiringPi](https://github.com/WiringPi/WiringPi) library provides the Raspberry Pi GPIO interface. Follow the instructions in that repository or do the following.

```bash
# Clone the repository 
$ git clone https://github.com/WiringPi/WiringPi.git 

# Access the wiringPi folder 
$ cd WiringPi 

# Build the library
$ ./build 
```

#### Compile [LoraWANPi](https://github.com/lucasmaziero/lmic-rpi-fox.git) 

```bash
# Access the lmic_rpi folder 
$ cd /home/pi/raingauge/src/lmic_rpi/examples/ttn-abp-send 

# Make the project 
# This will generate the executable for LoraWAN communication
$ make 

# Add the executable to system path
$ nano ~/.bashrc

# Appened the following line to the end of .bashrc file 
$ export PATH="$PATH:/home/pi/raingauge/src/lmic_rpi/examples/ttn-abp-send"

# to avoid rebooting after change
$ source ~/.bashrc

# Usage
# LED flag (0/1) can be used as an indication for data sending
$ ttn-abp-send <DevAddr> <Nwkskey> <Appskey> <Rain_mm> <solar_V> <battery_V> <solar_I> <battery_I> <LED_FLAG>
```

### 13. Add influx-db yaml file (`influxdb_api.yaml`) or LoraWAN keys yaml file (`lorawan_keys.yaml`) to config folder
Download these from `API_Keys` folder in `SWSICFOSS`  Google Drive. 

### 14. Edit device details in config file
```bash
# open config.yaml
nano /home/pi/raingauge/src/config/config.yaml

# edit device name based on names in infulxdb or lora key files
eg: 
    device_name: rainpi_test
    device_name: rainpi_x

# edit device location
eg: 
    device_location: greenfield tvm 

# edit device field deployment status
eg:
    field_deployed: false
```
### 15. Add the device to Zerotier account

Follow the instructions on [Zerotier for Raspberry Pi Tutorial](https://pimylifeup.com/raspberry-pi-zerotier/). Go to  [Zerotier](https://my.zerotier.com/) platform and login with the credentials shared via email/open project to monitor/connect to device IPs.

### 16. Setup the python script run automatically after booting 

you can do this in many ways
* Using bashrc
* Running the script as service
 
```bash
#Add Python scripts to bashrc file 
nano ~/.bashrc

# Appened the following line to the end of .bashrc file 
python3 /home/pi/raingauge/src/daq_pi.py

# Reboot the device
sudo reboot
```



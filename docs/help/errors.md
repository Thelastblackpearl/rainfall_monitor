## GENERAL
* OS installation is crucial, as any errors during this stage can have serious consequences.
* The error when building WiringPi library often occurs due to missing packages or files in the Linux system. This may happen during the OS installation or if the file system wasn’t updated properly during a system update.if so,
    * try reinstalling OS
    * if make is present in system (installing make)
        https://www.makeuseof.com/how-to-fix-make-command-not-found-error-ubuntu/
* if there is an error like "error writing to file -write (28:no space left on device)"
    * check how much space is left on your partitions using command
        * df -h
    * check what makes the memory full.
        * It could be a service spamming the log with errors.check this usinng the command
            * sudo du -sh /var/log/*
        * if syslogs is the cause of memory fill.then remove it using the following command
            * sudo truncate -s 0 /var/log/syslog
    * then free up some space by removing unnecessary data or packages       

* add device to zerotier: Follow the instructions on [Zerotier for Raspberry Pi Tutorial](https://pimylifeup.com/raspberry-pi-zerotier/). Go to  [Zerotier](https://my.zerotier.com/) platform and login with the credentials shared via email/open project to monitor/connect to device IPs. 

### Running the script as service

```bash
#create the service file
sudo nano /etc/systemd/system/raingauge.service

# add the following content into raingauge.service and save it
# change user name and path accordingly

[Unit]
Description=acoustic raingauge Script Service
After=network.target

[Service]
ExecStart=/usr/bin/python3 /home/pi/raingauge/src/daq_pi.py
WorkingDirectory=/home/pi/raingauge/src
StandardOutput=inherit
StandardError=inherit
Restart=always
User=pi

[Install]
WantedBy=multi-user.target

# use the following commands
sudo systemctl daemon-reload
sudo systemctl start raingauge.service
sudo systemctl enable raingauge.service

# use the commands to see status,stop and start service
sudo systemctl status raingauge.service
sudo systemctl stop raingauge.service
sudo systemctl restart raingauge.service

* if youu are running the log as service log of service can be found at /var/log/journal
```

## PERIPHERALS
* UART in python and c: https://www.electronicwings.com/raspberry-pi/raspberry-pi-uart-communication-using-python-and-c
* Enabling UART for battery monitoring: https://www.electronicwings.com/raspberry-pi/raspberry-pi-uart-communication-using-python-and-c        
* Default state of gpio pins in raspberry pi : https://roboticsbackend.com/raspberry-pi-gpios-default-state/

## NETWORKS
* how to ON/OFF ethernet/wlan: https://stackoverflow.com/questions/23487728/ethernet-disabling-in-raspberry-pi
* issue: IP V4 is not assigning to ethernet(V6 is present): https://www.freshblurbs.com/blog/2022/08/07/fix-eth0-rpi-ubuntu.html
* Add wifi credentials and ethernet details to the existing system
    * sudo vim  /etc/netplan/50-cloud-init.yaml
    * Add the following content to the file (use Vim editor to make sure consistent indentation)
``` bash
network:
    ethernets:
        eth0:
            dhcp4: true
            optional: true
    version: 2
    wifis:
        wlan0:
            dhcp4: true
            optional: true
            access-points:
                "wifi_name":
                        password: "password"

 ``` 	

    * Then run ,to know if it is working
	    * sudo netplan generate
        * sudo netplan apply	


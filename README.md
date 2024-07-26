
# Domoticz-E-Flux

E-Flux Plugin for Domoticz home automation
This plugin allows you to see all the relevant information from your 'E-Flux by Road' back office of your EV Charger

More info about 'E-Flux by Road' back office:
https://www.e-flux.io/


## Installation

Python version 3.4 or higher required & Domoticz version 3.87xx or greater.

To install:
* Go in your Domoticz directory using a command line and open the plugins directory.
* Run: ```git clone https://github.com/galadril/Domoticz-E-Flux-Plugin.git```
* Restart Domoticz.

## Devices

![image](https://github.com/user-attachments/assets/f481aae1-6fd4-4f7c-ab92-f4f4afd6a071)


## Configuration

* Open the Domoticz web interface.
* Go to Setup > Hardware.
* Add a new hardware with under the type E-Flux.
* Set the Scan interval (in seconds) for how often the plugin should scan for E-Flux devices.
* Save and close the dialog.


## Updating

To update:
* Go in your Domoticz directory using a command line and open the plugins directory then the Domoticz-E-Flux-Plugin directory.
* Run: ```git pull```
* Restart Domoticz.


## Usage

The plugin will automatically discover compatible E-Flux devices on your local network and create/update devices in Domoticz. 


## Debugging

You can enable debugging by setting the Debug parameter to a value between 1 and 6 in the Setup > Hardware dialog. More information about the debugging levels can be found in the Domoticz documentation.


## Change log

| Version | Information |
| ----- | ---------- |
| 0.0.1 | Initial version |


# Donation

If you like to say thanks, you could always buy me a cup of coffee (/beer)!   
(Thanks!)  
[![PayPal donate button](https://img.shields.io/badge/paypal-donate-yellow.svg)](https://www.paypal.me/markheinis)

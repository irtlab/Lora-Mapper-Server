# Lora-Mapper-Server
Server to use with lora mapper device and TTNMapper to generate uplink and downlink signal coverage map data

# Usage

### Pre-Requisite
- LoRaWAN device with firmware from https://github.com/irtlab/lora-tester
- TTN account with device regestered to an application and the MQTT access keys and URL
- TTNMapper application in an android phone with a reliable location service
- A server routable on the internet, with port 5000 open, and python3
- Installed Python Packages using PIP: flask, threading, paho, json, os, time

### Running the server
- Use the server version with the higest numeric heading (currently server5.py)
- Edit lines 11-13 to preferred output file names
- Edit lines 16-20 to update MQTT stream access
- Run python3 server5.py
- Trigger test device and observer console output


*Latest Version as on 25 Dec 2023 Written by Hayagreevan Sriram for the IRT Lab*

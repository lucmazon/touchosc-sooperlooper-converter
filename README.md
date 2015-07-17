Description
===========

By default, [TouchOSC](http://hexler.net/software/touchosc) doesn't work well with [SooperLooper](http://essej.net/sooperlooper/). SooperLooper can receive multiple parameters of multiple types (string, float…), but TouchOSC can only send a single float. And when you try to get values from SooperLooper, you have to wrap the response to send it back to TouchOSC.

This little software aims to do just that.

Requirements
============

- python 3
- python-osc (`sudo pip3 install python-osc`)

Usage
=====

TouchOSC
--------

The osc message must be manually set, and looks like this (example for a fader):

```
/1##/sl/-1/set##wet
```

Here, `##` is the separator (defined in `converter.py`). It is used here to split the TouchOSC's page (`/1` here, required for feedback), the "actual" osc url (`/sl/-1/set`) and the "virtual" additional parameter (`wet`).

For the moment, the only feedback registered is when you have a fader mapped to the volume of all loops (the one defined just above), and a fader for each loop's volume (or at least one). When you change the global volume, you want the individual faders to be updated with the new value. To make it happen, you have to name your fader `X_control`, where `X` is your loop number (0, 1, 2…) and `control` is the control you want to monitor (`wet` here).

For `hit`  commands, SooperLooper requires as parameter a single command name, so when our converter receives a push event, it only converts the "pressed" value (0.0) to the `hit` command:

```
/1##/sl/0/hit##record 0.0    # push button pressed: converting to /sl/0/hit record
/1##/sl/0/hit##record 1.0    # push button released: do nothing
```

A (very) basic TouchOSC layout is included in this repository, with not even all the buttons mapped. But still, it works out of the box with SooperLooper, so feel free to examine and improve it (you can even send me pull requests of awesome layouts you came up with!).

converter.py
============

`./converter.py -h` will give you all the informations you need ;)

```
usage: converter.py [-h] [-d] [--server-ip SERVER_IP]
                    [--server-port SERVER_PORT] --touchosc-ip TOUCHOSC_IP
                    [--touchosc-port TOUCHOSC_PORT]
                    [--sooperlooper-ip SOOPERLOOPER_IP]
                    [--sooperlooper-port SOOPERLOOPER_PORT]

optional arguments:
  -h, --help            show this help message and exit
  -d                    Debug mode
  --server-ip SERVER_IP
                        Server ip
  --server-port SERVER_PORT
                        The port the OSC server is listening to
  --touchosc-ip TOUCHOSC_IP
                        Touch OSC client ip
  --touchosc-port TOUCHOSC_PORT
                        Touch OSC port to send messages to
  --sooperlooper-ip SOOPERLOOPER_IP
                        SooperLooper client ip
  --sooperlooper-port SOOPERLOOPER_PORT
                        SooperLooper port to send messages to
```

The only parameter you have to provide is `--touchosc-ip`, which is your TouchOSC device ip (it cannot be guessed!). By default, TouchOSC sends to port 8000 and receives on port 9000, so we kept those default for the parameters `--touchosc-port` and `--server-port`. The server port is by default "0.0.0.0", so in most cases, you don't have to change it. Same goes for SooperLooper ip ("0.0.0.0") and port (9951) which are the default ones.

The separator (##), the amount of loops (3) and TouchOSC pages (1) are currently hard-coded. Change them as you see fit.

Wifi
====

If you are in a place where no wireless network is available, I strongly encourage you to use something like [create_ap](https://github.com/oblique/create_ap):

```
sudo create_ap -n wlan0 my-ssid my-password
```

Conclusion
==========

This project is still in pre-alpha state, so don't hesitate to tell me if there's stuff you want me to add. Oh, and you can send me pull requests too ;)

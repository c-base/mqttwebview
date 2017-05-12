# A MQTT-connected web view

- heavily based on https://github.com/c-base/mqttluakit/

## How to install

- Install the dependencies like this:

```
sudo apt install python3-gi gir1.2-webkit-3.0
pip3 install --user pywebview paho-mqtt validators
```

- Then clone the git repo: `https://github.com/c-base/mqttwebview.git`

## How to run

- cd into the freshly cloned directory
- Run the program with `./run_mqttwebview.sh`

## Run automatically at boot time

Set i3 as the default window manage (session) in lightdm.

Add the following line to `/home/$USER/.i3/config`:
```
exec /home/siri/mqttwebview/run_mqttwebview.sh
```

## Hwith no X11 cursor

in `/etc/lightdm/lightdm.conf` change the line
```
xserver-command=X
```
into this: 
```
xserver-command=X -nocursor -s 0 dpms
```

# A MQTT-connected 

- heavily based on http://github.com/c-base/mqttluakit

## How to install

```
sudo apt install python3-gi gir1.2-webkit-3.0
pip3 install --user pywebview paho-mqtt validators
```

## How to run

- Clone git repo: `http://github.com/c-base/mqttwebview.git`
- cd into the freshly cloned directory
- ./run_mqttwebview.sh

## Run automatically at boot time with no X11 cursor

in /etc/lightdm/lightdm.conf change

xserver-command=X

to 

xserver-command=X -nocursor -s 0 dpms



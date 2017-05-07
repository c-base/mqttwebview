#
heavily based on http://github.com/c-base/mqttluakit

## How to install

sudo apt install python3-gi gir1.2-webkit-3.0
pip3 install --user pywebview
pip3 install --user paho-mqtt
pip3 install --user validators

## How to run

Clone git repo

goto cloned dir

run run_mqtt

## Run automatically at boot time with no X11 cursor

in /etc/lightdm/lightdm.conf change

xserver-command=X

to 

xserver-command=X -nocursor -s 0 dpms



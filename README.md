# A MQTT-connected web view

- heavily based on https://github.com/c-base/mqttluakit/

## How to install

- Install the dependencies like this:

```
sudo apt install python3-gi gir1.2-webkit-3.0 libwebkitgtk-3.0-dev i3 
pip3 install --user pywebview paho-mqtt validators config
```

- Then clone the git repo: `https://github.com/c-base/mqttwebview.git`

## How to run

- cd into the freshly cloned directory
- copy config.py.sample to config.py
- edit config.py
- Run the program with `./run_mqttwebview.sh`

## Run automatically at boot time

- Set i3 as the default window manage (session) in lightdm:
- You have to go edit lightdm configuration's file:

```
$ nano /etc/lightdm/lightdm.conf
```

and change that line: `user-session=i3`
This will make i3 as "default" when you login.

- Reboot.
- When booting into i3 for the first time you are asked to generate the i3 config file. Acceppt by hitting Return.
- Add the following line to `/home/$USER/.i3/config`:
```
exec /home/$USER/mqttwebview/run_mqttwebview.sh
```

## How to run X11 without mouse cursor and also disable display sleep

in `/etc/lightdm/lightdm.conf` change the line
```
xserver-command=X
```
into this: 
```
xserver-command=X -nocursor -s 0 dpms
```

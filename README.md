# 2025_01_01_APIntTrustedLobbyIID

You just want to Websocket with not security on your LAN to share integer between your devices.
You can find here  Websocket IID server that just take value and broadcast it to all the connected users.


```
```


```

git clone https://github.com/EloiStree/2025_01_01_TrustedServerAPIntIID.git /git/apint_trusted_push_iid
cd /etc/systemd/system/
sudo nano apint_trusted_push_iid.service
sudo nano apint_trusted_push_iid.timer
```
```
[Unit]
Description=APIntIO Trusted Push IID Service
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 /git/apint_trusted_push_iid/RunServer.py
Restart=always
User=root
WorkingDirectory=/git/apint_trusted_push_iid

[Install]
WantedBy=multi-user.target
```

```
[Unit]
Description=APIntIO Push IID Timer

[Timer]
OnBootSec=0min
OnUnitActiveSec=10s

[Install]
WantedBy=timers.target
```

```
cd /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable apint_trusted_push_iid.service
chmod +x /git/apint_trusted_push_iid/RunServer.py
sudo systemctl restart apint_trusted_push_iid.service

sudo systemctl enable apint_trusted_push_iid.timer
sudo systemctl start apint_trusted_push_iid.timer
sudo systemctl list-timers | grep apint_udp_relay_iid

sudo systemctl restart apint_trusted_push_iid.service
sudo systemctl restart apint_trusted_push_iid.timer


sudo systemctl status apint_trusted_push_iid.service
sudo systemctl status apint_trusted_push_iid.timer
```


```
pip install requests tornado --break-system-packages
```

```

sudo systemctl stop apint_trusted_push_iid.service
sudo systemctl stop apint_trusted_push_iid.timer
python /git/apint_trusted_push_iid/RunServer.py
```

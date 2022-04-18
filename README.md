Control volumio radio through GPIO pins on Raspberry Pi

sudo cp /home/volumio/GPIO_radio/volumiostartonboot.service /etc/systemd/system
sudo systemctl daemon-reload
sudo systemctl start volumiostartonboot.service
sudo systemctl enable volumiostartonboot.service

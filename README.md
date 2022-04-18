Control volumio radio through GPIO pins on Raspberry Pi

Install as a service:
---------------------------------
sudo cp /home/volumio/GPIO_radio/volumiostartonboot.service /etc/systemd/system</br>
sudo systemctl daemon-reload</br>
sudo systemctl start volumiostartonboot.service</br>
sudo systemctl enable volumiostartonboot.service</br>

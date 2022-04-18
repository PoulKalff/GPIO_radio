Control volumio radio through GPIO pins on Raspberry Pi


Install prerequisites:
---------------------------------
sudo apt install python3-pip</br>
sudo pip3 install RPi.GPIO</br>

Install as a service:
---------------------------------
sudo cp /home/volumio/GPIO_radio/volumiostartonboot.service /etc/systemd/system</br>
sudo systemctl daemon-reload</br>
sudo systemctl start volumiostartonboot.service</br>
sudo systemctl enable volumiostartonboot.service</br>

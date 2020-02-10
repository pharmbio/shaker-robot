# Shaker robot modifications and code


## Arduino
```
# Install arduino-cli
cd /tmp
curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | sh
sudo mv bin/arduino-cli /usr/local/bin/

# setup arduini-cli
arduino-cli config init
arduino-cli core update-index
arduino-cli core install arduino:megaavr

# Add user to serial user group
sudo usermod -a -G dialout $USER
# Logout from computer (for getting the usermod changes)
```

## Python
```
# create and activate venv
sudo apt install python3-venv
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt

# run client
pyhton arduino_shaker_client.py
```

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
``

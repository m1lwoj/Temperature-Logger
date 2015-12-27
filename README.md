# Temperature-Logger
Raspberry PI Temperature logger, using DHT 11

Results you can find under result.png file.

Installed python3, sqlite, apache with cgi, internet connection are mandatory to use project.

In my case DHT11 termometer is connected to GPIO pin 4, use 3,5V power and 3,5kohm resistor.

Shell script collects data form termometer i use Adafrui_DHT script for that.

If you want to use it regularly in same time periods you should add "skrypt.sh" to device's crontab.

Apache is required to handle cgi script in python language, you can find a nice tutorial here (https://www.linux.com/community/blogs/129-servers/757148-configuring-apache2-to-run-python-scripts)

Python script should be placed in yout apache cgi-bin directory.

A device have to be connected to internet, becasue of using google charts libraries.


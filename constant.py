"""Application configuration."""
IP_DST = "10.0.0.1"
PORT_DST = 14999

IP_RASPI = "10.0.0.10"
PORT_RASPI = 8080

START_GPIO = 10
MAYA_GPIO = 11
CONSOLE_GPIO = 9
USINE_GPIO = 5

# Do not modify below this line.
URL_DST = "http://{}:{}/".format(IP_DST, PORT_DST)

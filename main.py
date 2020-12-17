import RPi.GPIO as GPIO
import subprocess
import time
import logging

import listener
import constant

LOG = logging.getLogger(__name__)


class Sensor:
    """
    Interface with an electronic sensor connected to the board.

    This class is used to check if a sensor is active or not, and send the
    associated request to Houdini.

    int pin: GPIO number where the positive wire of the sensor is connected
    str name_get: trailing part of the URL where an HTTP request is sent when
        the sensor is activated
    bool reverse: indicate if activated sensor makes GPIO.input() True
        (default) or False (reverse = True)

    """

    def __init__(self, pin, name_get, reverse=False):
        self.pin = pin
        self.name_get = name_get
        self.reverse = reverse
        self.activated = False
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def read(self):
        """Return the status of the sensor as True or False."""
        # Flip the result if the sensor is reversed
        return bool(GPIO.input(self.pin)) ^ self.reverse

    def get_request(self):
        """Send a signal to Houdini for this sensor."""
        LOG.debug("get request send: %s", self.name_get)
        subprocess.call([
            "curl", "-m", "1", "-X", "GET", "{}{}".format(
                constant.URL_DST, self.name_get)
        ])

    def check_run(self):
        """
        Check if the sensor is active, and send a request to Houdini.

        This method combines self.read and self.get_request in a simple
        one-shot method.

        """
        if self.read() and not self.activated:
            LOG.debug("Activate %s sensor.", self.name_get)
            self.activated = True
            self.get_request()


def init():
    GPIO.setmode(GPIO.BCM)

    global maya
    global console
    global usine

    maya = Sensor(constant.MAYA_GPIO, "maya", reverse=True)
    console = Sensor(constant.CONSOLE_GPIO, "console", reverse=True)
    usine = Sensor(constant.USINE_GPIO, "usine", reverse=True)


def wait_start():
    if listener.server_program() == "start":
        LOG.info("C'est parti !")
        subprocess.call(
            ["curl", "-X", "GET", "{}start".format(constant.URL_DST)])
        time.sleep(5)
        subprocess.call(
            ["curl", "-X", "GET", "{}intro".format(constant.URL_DST)])


def new_game():
    """
    Start a new game.

    Waits for the start signal, then listen for sensor update to trigger
    the associated action.

    """
    LOG.info("Start service.")
    try:
        LOG.debug("Initializing.")
        init()
        LOG.debug("Wait for game start.")
        wait_start()
        LOG.debug("Game started.")
        while True:
            LOG.debug("Check maya.")
            maya.check_run()
            LOG.debug("Check console.")
            console.check_run()
            LOG.debug("Check usine.")
            usine.check_run()
    finally:
        GPIO.cleanup()
        LOG.info("Stop service.")


if __name__ == "__main__":
    new_game()

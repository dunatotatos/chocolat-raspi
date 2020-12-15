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

    """

    def __init__(self, pin, name_get):
        self.pin = pin
        self.name_get = name_get
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def read(self):
        """Return the status of the sensor as True or False."""
        return GPIO.input(self.pin)

    def get_request(self):
        """Send a signal to Houdini for this sensor."""
        LOG.debug("get request send:{}".format(self.name_get))
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
        # not self.read because switches are the opposite.
        if not self.read() and not game_state[self.name_get]:
            LOG.debug(game_state)
            game_state[self.name_get] = True
            LOG.debug(game_state)
            self.get_request()


def init():
    GPIO.setmode(GPIO.BCM)

    global maya
    global console
    global usine
    global game_state

    game_state = {"maya": False, "console": False, "usine": False}
    maya = Sensor(constant.MAYA_GPIO, "maya")
    console = Sensor(constant.CONSOLE_GPIO, "console")
    usine = Sensor(constant.USINE_GPIO, "usine")


def wait_start():
    if listener.server_program() == "start":
        LOG.info("C'est parti !")
        subprocess.call(
            ["curl", "-X", "GET", "{}start".format(constant.URL_DST)])
        time.sleep(5)
        subprocess.call(
            ["curl", "-X", "GET", "{}intro".format(constant.URL_DST)])


def main():
    LOG.info("Start service.")
    try:
        LOG.debug("Initializing.")
        init()
        LOG.debug("Wait for game start.")
        wait_start()
        LOG.debug("Game started.")
        while (True):
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
    main()

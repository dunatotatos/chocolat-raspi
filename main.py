import RPi.GPIO as GPIO
import subprocess
import time
import logging

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


class Game:
    """
    One game instance.

    This class provides an interface to manage the logic of a game.
    Instanciate this class to create a new game instance, and run game.start
    to wait for the start button signal.

    """

    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        self.sensors = {
            'start': Sensor(constant.START_GPIO, "start", reverse=True),
            'maya': Sensor(constant.MAYA_GPIO, "maya", reverse=True),
            'console': Sensor(constant.CONSOLE_GPIO, "console", reverse=True),
            'usine': Sensor(constant.USINE_GPIO, "usine", reverse=True)
        }

    def wait_start(self):
        """Do nothing until the start button is pressed, then exit."""
        while not self.sensors['start'].read():
            time.sleep(0.1)

        self.sensors['start'].activated = True
        LOG.info("Start button pressed.")
        subprocess.call(
            ["curl", "-X", "GET", "{}start".format(constant.URL_DST)])
        time.sleep(5)
        subprocess.call(
            ["curl", "-X", "GET", "{}intro".format(constant.URL_DST)])

    def run(self):
        """Wait for events to send triggers."""
        while not self.is_complete():
            LOG.debug("Check maya.")
            self.sensors['maya'].check_run()
            LOG.debug("Check console.")
            self.sensors['console'].check_run()
            LOG.debug("Check usine.")
            self.sensors['usine'].check_run()
            time.sleep(0.1)

    def start(self):
        """
        Start a new game.

        Waits for the start signal, then listen for sensor update to trigger
        the associated action.

        """
        LOG.info("Start service.")

        try:
            LOG.debug("Wait for game start.")
            self.wait_start()
            LOG.debug("Game started.")
            self.run()
        finally:
            LOG.info("Stop service.")
            GPIO.cleanup()

    def is_complete(self):
        """
        Check if this Game instance still has something to do before next game.

        Return True is Game is complete. False otherwise.

        """
        return all([s.activated for s in self.sensors.values()])


if __name__ == "__main__":
    Game().start()

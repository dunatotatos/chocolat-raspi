import RPi.GPIO as GPIO
import subprocess
import time
import logging

import listener
import constant

LOG = logging.getLogger(__name__)


class Sensor:
    def __init__(self, pin, name_get):
        self.pin = pin
        self.name_get = name_get
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def read(self):
        return GPIO.input(self.pin)

    def get_request(self):
        LOG.debug("get request send:{}".format(self.name_get))
        subprocess.call([
            "curl", "-m", "1", "-X", "GET", "{}{}".format(
                constant.url, self.name_get)
        ])

    def check_run(self):
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
    maya = Sensor(11, "maya")
    console = Sensor(9, "console")
    usine = Sensor(5, "usine")


def wait_start():
    if listener.server_program() == "start":
        LOG.info("C'est parti !")
        subprocess.call(["curl", "-X", "GET", "{}start".format(constant.url)])
        time.sleep(5)
        subprocess.call(
            ["curl", "-X", "GET", "{}machine".format(constant.url)])


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

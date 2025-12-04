# speaker_controller.py

try:
    import RPi.GPIO as GPIO
    IS_RPI = True
except ImportError:
    IS_RPI = False

class SpeakerController:
    def __init__(self, pin=21, freq=440):
        self.pin = pin
        self.freq = freq
        self.pwm = None

    def initialize(self):
        if not IS_RPI:
            return

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT)
        self.pwm = GPIO.PWM(self.pin, self.freq)

    def alarm_on(self):
        if IS_RPI and self.pwm:
            print("[ALARM] Speaker ON")
            self.pwm.start(50)

    def alarm_off(self):
        if IS_RPI and self.pwm:
            print("[ALARM] Speaker OFF")
            self.pwm.stop()

    def cleanup(self):
        if IS_RPI:
            GPIO.cleanup()


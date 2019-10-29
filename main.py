# ////////////////////////////////////////////////////////////////
# //                     IMPORT STATEMENTS                      //
# ////////////////////////////////////////////////////////////////

import math
import sys
import time
import threading

from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import *
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.slider import Slider
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.clock import Clock
from kivy.animation import Animation
from functools import partial
from kivy.config import Config
from kivy.core.window import Window
from pidev.kivy import DPEAButton
from pidev.kivy import PauseScreen
from time import sleep
import RPi.GPIO as GPIO
from pidev.stepper import stepper
from pidev.Cyprus_Commands import Cyprus_Commands_RPi as cyprus
from kivy.properties import ObjectProperty

# ////////////////////////////////////////////////////////////////
# //                      GLOBAL VARIABLES                      //
# //                         CONSTANTS                          //
# ////////////////////////////////////////////////////////////////
ON = False
OFF = True
HOME = True
TOP = False
OPEN = False
CLOSE = True
YELLOW = .180, 0.188, 0.980, 1
BLUE = 0.917, 0.796, 0.380, 1
DEBOUNCE = 0.1
INIT_RAMP_SPEED = 10
RAMP_LENGTH = 725



# ////////////////////////////////////////////////////////////////
# //            DECLARE APP CLASS AND SCREENMANAGER             //
# //                     LOAD KIVY FILE                         //
# ////////////////////////////////////////////////////////////////
class MyApp(App):
    def build(self):
        self.title = "Perpetual Motion"
        return sm


Builder.load_file('main.kv')
Window.clearcolor = (.1, .1, .1, 1)  # (WHITE)

cyprus.open_spi()

# ////////////////////////////////////////////////////////////////
# //                    SLUSH/HARDWARE SETUP                    //
# ////////////////////////////////////////////////////////////////
sm = ScreenManager()
ramp = stepper(port=0, micro_steps=32, hold_current=20, run_current=20, accel_current=20, deaccel_current=20,
             steps_per_unit=25, speed=INIT_RAMP_SPEED)
ramp.go_until_press(0, 10000)
ramp.set_as_home()

cyprus.initialize()
cyprus.setup_servo(2)
cyprus.set_servo_position(2, 0)

cyprus.setup_servo(1)
cyprus.set_pwm_values(1, period_value=100000, compare_value=0, compare_mode=cyprus.LESS_THAN_OR_EQUAL)


# ////////////////////////////////////////////////////////////////
# //                       MAIN FUNCTIONS                       //
# //             SHOULD INTERACT DIRECTLY WITH HARDWARE         //
# ////////////////////////////////////////////////////////////////

# ////////////////////////////////////////////////////////////////
# //        DEFINE MAINSCREEN CLASS THAT KIVY RECOGNIZES        //
# //                                                            //
# //   KIVY UI CAN INTERACT DIRECTLY W/ THE FUNCTIONS DEFINED   //
# //     CORRESPONDS TO BUTTON/SLIDER/WIDGET "on_release"       //
# //                                                            //
# //   SHOULD REFERENCE MAIN FUNCTIONS WITHIN THESE FUNCTIONS   //
# //      SHOULD NOT INTERACT DIRECTLY WITH THE HARDWARE        //
# ////////////////////////////////////////////////////////////////
class MainScreen(Screen):
    version = cyprus.read_firmware_version()
    staircaseSpeedText = '0'
    rampSpeed = INIT_RAMP_SPEED
    staircaseSpeed = 40

    staircase = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        self.initialize()

    def toggleGate(self):
        print("Open and Close gate here")

        self.openGate()


    def openGate(self):
        global CLOSE

        if CLOSE:
            cyprus.set_servo_position(2, 0.5)
            CLOSE = False
        else:
            cyprus.set_servo_position(2, 0)
            CLOSE = True



    def toggleStaircase(self):
        print("Turn on and off staircase here")

        self.turnOnStaircase()

    def turnOnStaircase(self):
        global OFF

        if OFF:
            cyprus.set_pwm_values(1, period_value=100000, compare_value=50000, compare_mode=cyprus.LESS_THAN_OR_EQUAL)
            print("staircase moving")
            OFF = False
        else:
            cyprus.set_pwm_values(1, period_value=100000, compare_value=0, compare_mode=cyprus.LESS_THAN_OR_EQUAL)
            print("staircase stopped")
            # self.staircase.text = "Staircase Off"
            OFF = True
    def toggleRamp(self):
        print("Move ramp up and down here")
        self.moveRamp()
    def moveRamp(self):
        global HOME
        #global TOP
        if HOME:
            print(" ramp moving")
            ramp.start_relative_move(-228)
            print("at top")

            HOME = False
            #TOP = True
        else:
            ramp.goHome()
            print("at home")

    def auto(self):
        print("Run through one cycle of the perpetual motion machine")
        # NATALIE! I talked to harlow and he says we need to use the switch on the ramp to determine the home position,
        # aka set home when switch is pressed. something with the function: go_until_press(self, dir: int, speed: int)
        # didn't figure it out yet though
        self.toggleRamp()
        self.toggleStaircase()
        self.toggleGate()
    def setRampSpeed(self, speed):
        print("Set the ramp speed and update slider text")
        ramp.set_speed(self.rampSpeed.value)
    def setStaircaseSpeed(self, speed):
        print("Set the staircase speed and update slider text")

    def initialize(self):
        print("Close gate, stop staircase and home ramp here")

    def resetColors(self):
        self.ids.gate.color = YELLOW
        self.ids.staircase.color = YELLOW
        self.ids.ramp.color = YELLOW
        self.ids.auto.color = BLUE

    def quit(self):
        print("Exit")
        MyApp().stop()


sm.add_widget(MainScreen(name='main'))

# ////////////////////////////////////////////////////////////////
# //                          RUN APP                           //
# ////////////////////////////////////////////////////////////////

MyApp().run()
cyprus.close_spi()
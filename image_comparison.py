# Android environment
import csv
import os
from time import sleep
import unittest
import base64
from appium import webdriver
from appium.webdriver.extensions.android.gsm import GsmCallActions
import time
from appium.webdriver.appium_service import AppiumService


desired_caps = dict(
    platformName='Android',
    platformVersion='11',
    automationName='UiAutomator2',
    deviceName='appium_emu_0',
    avd='appium_emu_0',
    # avdArgs=['-wipe-data'],
    disableWindowAnimation=True
    # app=PATH('../../../apps/selendroid-test-app.apk')
)

driver = webdriver.Remote('http://localhost:4723/wd/hub', desired_caps)

package_name = 'org.mistergroup.shouldianswer'

full_screenshot = f"out/{package_name}/screenshots/+18666257291.png"
print(full_screenshot)

image_allowed_file = f"reference_images/{package_name}/allowed-part.png"
image_blocked_file = f"reference_images/{package_name}/blocked-part.png"

full_screenshot_base64 = base64.b64encode(open(full_screenshot, "rb").read())
partial_screenshot_allow = base64.b64encode(open(image_allowed_file, "rb").read())
partial_screenshot_block = base64.b64encode(open(image_blocked_file, "rb").read())

# print(driver.find_image_occurrence(full_screenshot_base64.decode(), partial_screenshot_allow.decode()))
print(driver.find_image_occurrence(full_screenshot_base64.decode(), partial_screenshot_block.decode()))


try:
    print(driver.find_image_occurrence(full_screenshot_base64, partial_screenshot_allow))
except:
    pass

try:
    print(driver.find_image_occurrence(full_screenshot_base64, partial_screenshot_block))
except:
    pass
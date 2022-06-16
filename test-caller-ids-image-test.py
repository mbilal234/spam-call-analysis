# Android environment
import csv
import os
from time import sleep
import unittest
import base64
from appium import webdriver
from appium.webdriver.extensions.android.gsm import GsmCallActions
from wand.image import Image
import time
from appium.webdriver.appium_service import AppiumService

appium_service = AppiumService()

appium_service.start()

desired_caps = dict(
    platformName='Android',
    platformVersion='12',
    automationName='uiautomator2',
    deviceName='Pixel_4_API_30',
    avd='Pixel_4_API_30',
    # isHeadless=True,
    disableWindowAnimation=True
    # app=PATH('../../../apps/selendroid-test-app.apk')
)
driver = webdriver.Remote('http://localhost:4723/wd/hub', desired_caps)

# CONFIG

current_app_name = "com.callerid.block"
numbers = ['+18009423767', '+16058844130', '+18666257291', '+18003535920', '+18888996650', 
           '+13132631171', '+18558440114', '+18882224227', '+18442069035', '+18665320423',
           '+18558953393', '+18003219637', '+18662507212', '+18889346489', '+18776478552', 
           '+17204563720', '+18442068573', '+18554197365', '+18669145806', '+18009460332']
# numbers = ['+31621326032','+16058844130','+18666257291']

output_file = f'out/{current_app_name}/results.csv'
os.makedirs(f'out/{current_app_name}/screenshots', exist_ok=True)
open(output_file, 'w').truncate(0) 

image_allowed_file = f"reference_images/{current_app_name}/allowed-part.png"
image_blocked_file = f"reference_images/{current_app_name}/blocked-part.png"

partial_screenshot_allow: bytes = base64.b64encode(open(image_allowed_file, "rb").read())
partial_screenshot_block: bytes = base64.b64encode(open(image_blocked_file, "rb").read())

# numbers = ['+17204563720']


for number in numbers:
    driver.lock()
    driver.make_gsm_call(number, GsmCallActions.CALL)
    # sleep(1)

    start = time.time()

    while True:
        print('.', end=' ')
        full_screenshot = driver.get_screenshot_as_base64()

        try: 
            el = driver.find_image_occurrence(full_screenshot, partial_screenshot_allow)
            status='allowed'
            
            break

        except: 
            # Do nothing
            pass

        try: 
            el = driver.find_image_occurrence(full_screenshot, partial_screenshot_block)
            status='blocked'

            break

        except: 
            # Do nothing
            pass

        sleep(0.01)

    print()

    end = time.time()
    delta = end - start

    driver.make_gsm_call(number, GsmCallActions.CANCEL)

    csv_line = f"{number},{status},{delta}"
    print(csv_line)
    with open(output_file, 'a') as fd:
        fd.write(f'{csv_line}\n')

    sleep(2)

# print(cancel_output)



appium_service.stop()

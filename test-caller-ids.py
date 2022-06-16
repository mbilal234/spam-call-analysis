# Android environment
import csv
import os
from time import sleep
import unittest
import base64
from appium import webdriver
from appium.webdriver.extensions.android.gsm import GsmCallActions
from wand.image import Image

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

current_app_name = "com.callapp.contacts"
numbers = ['+18009423767', '+16058844130', '+18666257291', '+18003535920', '+18888996650', 
           '+13132631171', '+18558440114', '+18882224227', '+18442069035', '+18665320423',
           '+18558953393', '+18003219637', '+18662507212', '+18889346489', '+18776478552', 
           '+17204563720', '+18442068573', '+18554197365', '+18669145806', '+18009460332']
# numbers = ['+31621326032','+16058844130','+18666257291']

image_allowed_file = f"reference_images/{current_app_name}/allowed.png"
ref_image_allowed = Image(filename=image_allowed_file)

image_blocked_file = f"reference_images/{current_app_name}/blocked.png"
ref_image_blocked = Image(filename=image_blocked_file)

output_file = f'out/{current_app_name}/results.csv'
os.makedirs(f'out/{current_app_name}/screenshots', exist_ok=True)
open(output_file, 'r+').truncate(0) 

driver.lock()


for number in numbers:
    driver.make_gsm_call(number, GsmCallActions.CALL)

    sleep(1)

    filename = f'out/{current_app_name}/screenshots/{number}.png'
    driver.get_screenshot_as_file(filename=filename)

    cancel_output = driver.make_gsm_call(number, GsmCallActions.CANCEL)
    # print(cancel_output)
    # print(filename)

    with Image(filename=filename) as img:
        result_image_allow, result_metric_allow = img.compare(
            ref_image_allowed, metric='absolute')
        result_image_block, result_metric_block = img.compare(
            ref_image_blocked, metric='absolute')

        if(result_metric_allow > result_metric_block):
            status = 'blocked'
        else:
            status = 'allowed'

    csv_line = f"{number},{status}"
    print(csv_line)
    with open(output_file, 'a') as fd:
        fd.write(f'\n{csv_line}')

    # sleep(1)


# screenshotBase64 = driver.get_screenshot_as_base64()

# imgdata = base64.b64decode(screenshotBase64)
# filename = 'some_image.png'  # I assume you have a way of picking unique filenames
# with open(filename, 'wb') as f:
#     f.write(imgdata)


# driver.make_gsm_call

from appium import webdriver
from appium.webdriver.appium_service import AppiumService

from appsetupscripts.setup import *

appium_service = AppiumService()

appium_service.start()

systemPort = 8201

desired_caps = dict(
    platformName='Android',
    platformVersion='11',
    automationName='UiAutomator2',
    deviceName='',
    avd='appium_emu_1',
    systemPort=systemPort,
    # isHeadless=True,
    disableWindowAnimation=True
    # app=PATH('../../../apps/selendroid-test-app.apk')
)
driver1 = webdriver.Remote('http://localhost:4723/wd/hub', desired_caps)

systemPort += 1

desired_caps = dict(
    platformName='Android',
    platformVersion='11',
    automationName='UiAutomator2',
    deviceName='',
    avd='appium_emu_2',
    systemPort=systemPort,
    # isHeadless=True,
    disableWindowAnimation=True
    # app=PATH('../../../apps/selendroid-test-app.apk')
)
driver2 = webdriver.Remote('http://localhost:4723/wd/hub', desired_caps)


print("started 2 emulators")

driver1.quit()
driver2.quit()

appium_service.stop()
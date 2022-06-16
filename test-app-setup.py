# Android environment
import inspect
import os
from appium import webdriver

import appsetupscripts
from appsetupscripts.setup import *
from appium.webdriver.appium_service import AppiumService

appium_service = AppiumService()
appium_service.start(args=['--allow-insecure=emulator_console'])

desired_caps = dict(
    platformName='Android',
    platformVersion='12',
    automationName='uiautomator2',
    deviceName='appium_emu_0',
    avd='appium_emu_0',
    # avdArgs=['-wipe-data'],
    # isHeadless=True,
    disableWindowAnimation=True
    # app=PATH('../../../apps/selendroid-test-app.apk')
)
driver = webdriver.Remote('http://localhost:4723/wd/hub', desired_caps)

current_directory = os.path.dirname(os.path.abspath(__file__));
apk_directory = current_directory + '/apks'


def find_subclasses(module, clazz):
    return [
        cls
        for name, cls in inspect.getmembers(module)
        if inspect.isclass(cls) and issubclass(cls, clazz) and (cls is not clazz)
    ]


driver.set_clipboard(bytes())
driver.set_clipboard_text('')

# for index, cls in enumerate(find_subclasses(appsetupscripts.setup, AnalyzedApp)):
#     app = cls(driver, apk_directory)
#     app.uninstall()


app = MglabScm(driver, apk_directory)

# app.install()

# app.setup()

numbers = ['+18009423767', '+16058844130', '+18666257291', '+18003535920', '+18888996650']
app.perform_analysis(numbers)


appium_service.stop()
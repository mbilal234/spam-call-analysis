from abc import ABC, abstractmethod
from time import sleep

from appium.webdriver.common.appiumby import AppiumBy
from appium.webdriver.webdriver import WebDriver
from appium.webdriver.extensions.android.gsm import GsmCallActions
import selenium

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.actions import interaction
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.actions.pointer_input import PointerInput
# Android environment
import inspect
import os
from appium import webdriver

from appium.webdriver.appium_service import AppiumService

class DriverManager:
    driver: WebDriver

    def __init__(self, thread_index: int, headless: bool):
        systemPort = 8200 + thread_index
        desired_caps = dict(
            platformName='Android',
            platformVersion='11',
            automationName='UiAutomator2',
            deviceName='appium_emu_' + str(thread_index),
            avd='appium_emu_' + str(thread_index),
            systemPort=systemPort,
            avdArgs=['-wipe-data'],
            isHeadless=headless,
            disableWindowAnimation=True
            # app=PATH('../../../apps/selendroid-test-app.apk')
        )
        # desired_caps = dict(
        #     platformName='Android',
        #     platformVersion='11',
        #     automationName='UiAutomator2',
        #     deviceName='Pixel_4_API_30',
        #     avd='Pixel_4_API_30',
        #     systemPort=systemPort,
        #     avdArgs=['-wipe-data'],
        #     # isHeadless=True,
        #     disableWindowAnimation=True
        #     # app=PATH('../../../apps/selendroid-test-app.apk')
        # )
        self.driver =  webdriver.Remote('http://localhost:4723/wd/hub', desired_caps)

    def log_in_with_google_2(self, username, password):
        self.driver.implicitly_wait(8)

        self.driver.activate_app('com.android.vending')

        el1 = self.driver.find_element(by=AppiumBy.CLASS_NAME, value="android.widget.Button")
        el1.click()

        sleep(4)

        el2 = self.driver.find_element(by=AppiumBy.XPATH, value='//android.widget.EditText[@resource-id="identifierId"]')
        el2.send_keys(username)
        el2.click()
        sleep(2)
        self.driver.press_keycode(66)
        
        sleep(4)

        el5 = self.driver.find_element(by=AppiumBy.XPATH, value='//android.view.View[@resource-id="password"]/android.view.View/android.view.View[1]/android.widget.EditText')
        el5.send_keys(password)
        el5.click()
        self.driver.press_keycode(66)

        # el6 = self.driver.find_element(by=AppiumBy.XPATH, value='//android.view.View[@resource-id="passwordNext"]')
        # el6.click()

        sleep(1)

        el7 = self.driver.find_element(by=AppiumBy.XPATH, value='//android.view.View[@resource-id="signinconsentNext"]')
        el7.click()

        sleep(3)

        try:
            el = self.driver.find_element(by=AppiumBy.XPATH, value='//android.widget.FrameLayout[@resource-id="com.google.android.gms:id/suc_layout_status"]/android.widget.LinearLayout/android.widget.LinearLayout/android.widget.Button')
            el.click()
            sleep(2)
        except:
            pass

        try:
            el8 = self.driver.find_element(by=AppiumBy.ID, value="com.google.android.gms:id/sud_items_switch")
            el8.click()
                
            actions = ActionChains(self.driver)
            actions.w3c_actions = ActionBuilder(self.driver, mouse=PointerInput(interaction.POINTER_TOUCH, "touch"))
            actions.w3c_actions.pointer_action.move_to_location(760, 1732)
            actions.w3c_actions.pointer_action.pointer_down()
            actions.w3c_actions.pointer_action.move_to_location(788, 865)
            actions.w3c_actions.pointer_action.release()
            actions.perform()

            el13 = self.driver.find_element(by=AppiumBy.XPATH, value='//android.widget.FrameLayout[@resource-id="com.google.android.gms:id/suc_layout_status"]/android.widget.LinearLayout/android.widget.LinearLayout/android.widget.Button')
            el13.click()

        except:
            pass

    
    def silence_ringer(self):
        self.driver.implicitly_wait(15)

        self.driver.activate_app('com.android.settings')

        sleep(5)

        actions = ActionChains(self.driver)
        actions.w3c_actions = ActionBuilder(self.driver, mouse=PointerInput(interaction.POINTER_TOUCH, "touch"))
        actions.w3c_actions.pointer_action.move_to_location(596, 181)
        actions.w3c_actions.pointer_action.pointer_down()
        actions.w3c_actions.pointer_action.move_to_location(544, 2028)
        actions.w3c_actions.pointer_action.release()
        actions.perform()
            

        el1 = self.driver.find_element(by=AppiumBy.XPATH, value='//androidx.recyclerview.widget.RecyclerView[@resource-id="com.android.settings:id/recycler_view"]/android.widget.LinearLayout[6]')
        el1.click()
        el2 = self.driver.find_element(by=AppiumBy.ACCESSIBILITY_ID, value="Ring & notification volume")
        coordinates = el2.location
        actions = ActionChains(self.driver)
        actions.w3c_actions = ActionBuilder(self.driver, mouse=PointerInput(interaction.POINTER_TOUCH, "touch"))
        actions.w3c_actions.pointer_action.move_to_location(coordinates['x'], coordinates['y'])
        actions.w3c_actions.pointer_action.pointer_down()
        actions.w3c_actions.pointer_action.pause(0.1)
        actions.w3c_actions.pointer_action.release()
        actions.perform()
    
    def set_swipe_lock_screen(self):
        self.driver.implicitly_wait(15)

        self.driver.activate_app('com.android.settings')

        sleep(5)

        actions = ActionChains(self.driver)
        actions.w3c_actions = ActionBuilder(self.driver, mouse=PointerInput(interaction.POINTER_TOUCH, "touch"))
        actions.w3c_actions.pointer_action.move_to_location(542, 2063)
        actions.w3c_actions.pointer_action.pointer_down()
        actions.w3c_actions.pointer_action.move_to_location(549, 276)
        actions.w3c_actions.pointer_action.release()
        actions.perform()
            
        el1 = self.driver.find_element(by=AppiumBy.XPATH, value='//androidx.recyclerview.widget.RecyclerView[@resource-id="com.android.settings:id/recycler_view"]/android.widget.LinearLayout[5]')
        el1.click()
        el2 = self.driver.find_element(by=AppiumBy.ANDROID_UIAUTOMATOR, value="new UiSelector().text(\"Screen lock\");")
        # el2 = self.driver.find_element(by=AppiumBy.XPATH, value='//androidx.recyclerview.widget.RecyclerView[@resource-id="com.android.settings:id/recycler_view"]/android.widget.LinearLayout[7]')
        el2.click()
        el3 = self.driver.find_element(by=AppiumBy.ANDROID_UIAUTOMATOR, value="new UiSelector().text(\"Swipe\");")
        # el3 = self.driver.find_element(by=AppiumBy.XPATH, value='//androidx.recyclerview.widget.RecyclerView[@resource-id="com.android.settings:id/recycler_view"]/android.widget.LinearLayout[2]')
        el3.click()


    def log_in_with_google(self, username, password):
        self.driver.implicitly_wait(15)

        self.driver.activate_app('com.android.settings')

        sleep(2)

        actions = ActionChains(self.driver)
        actions.w3c_actions = ActionBuilder(self.driver, mouse=PointerInput(interaction.POINTER_TOUCH, "touch"))
        actions.w3c_actions.pointer_action.move_to_location(665, 2105)
        actions.w3c_actions.pointer_action.pointer_down()
        actions.w3c_actions.pointer_action.move_to_location(648, 343)
        actions.w3c_actions.pointer_action.release()
        actions.perform()

        actions = ActionChains(self.driver)
        actions.w3c_actions = ActionBuilder(self.driver, mouse=PointerInput(interaction.POINTER_TOUCH, "touch"))
        actions.w3c_actions.pointer_action.move_to_location(665, 2105)
        actions.w3c_actions.pointer_action.pointer_down()
        actions.w3c_actions.pointer_action.move_to_location(648, 343)
        actions.w3c_actions.pointer_action.release()
        actions.perform()

        # //android.widget.EditText[@resource-id="identifierId"]
            
        el3 = self.driver.find_element(by=AppiumBy.XPATH, value='//androidx.recyclerview.widget.RecyclerView[@resource-id="com.android.settings:id/recycler_view"]/android.widget.LinearLayout[9]/android.widget.RelativeLayout')
        el3.click()

        try:
            el4 = self.driver.find_element(by=AppiumBy.ID, value="com.google.android.gms:id/action_chip")
        except selenium.common.exceptions.NoSuchElementException:
            el4 = self.driver.find_element(by=AppiumBy.ID, value="com.google.android.gms:id/clp_button")


        el4.click()

        sleep(1)

        # el2 = self.driver.find_element(by=AppiumBy.ID, value="com.google.android.gms:id/sud_layout_content")
        # el2.click()

        # el2 = self.driver.find_element(by=AppiumBy.CLASS_NAME, value='android.widget.EditText')
        
        el2 = self.driver.find_element(by=AppiumBy.XPATH, value='//android.widget.FrameLayout[@resource-id="com.google.android.gms:id/sud_layout_content"]/android.webkit.WebView/android.webkit.WebView/android.view.View[2]/android.view.View[3]/android.view.View/android.view.View[1]/android.view.View[1]/android.widget.EditText')
        # el2 = self.driver.find_element(by=AppiumBy.XPATH, value='//android.widget.EditText[@resource-id="identifierId"]')
        el2.send_keys(username)
        sleep(1)
        el3 = self.driver.find_element(by=AppiumBy.XPATH, value='//android.view.View[@resource-id="identifierNext"]')
        el3.click()

        sleep(1)

        el5 = self.driver.find_element(by=AppiumBy.XPATH, value='//android.view.View[@resource-id="password"]/android.view.View/android.view.View[1]/android.widget.EditText')
        el5.send_keys(password)
        el6 = self.driver.find_element(by=AppiumBy.XPATH, value='//android.view.View[@resource-id="passwordNext"]')
        el6.click()

        sleep(1)

        el7 = self.driver.find_element(by=AppiumBy.XPATH, value='//android.view.View[@resource-id="signinconsentNext"]')
        el7.click()

        sleep(3)

        try:
            el = self.driver.find_element(by=AppiumBy.XPATH, value='//android.widget.FrameLayout[@resource-id="com.google.android.gms:id/suc_layout_status"]/android.widget.LinearLayout/android.widget.LinearLayout/android.widget.Button')
            el.click()
            sleep(2)
        except:
            pass

        try:
            el8 = self.driver.find_element(by=AppiumBy.ID, value="com.google.android.gms:id/sud_items_switch")
            el8.click()
                
            actions = ActionChains(self.driver)
            actions.w3c_actions = ActionBuilder(self.driver, mouse=PointerInput(interaction.POINTER_TOUCH, "touch"))
            actions.w3c_actions.pointer_action.move_to_location(760, 1732)
            actions.w3c_actions.pointer_action.pointer_down()
            actions.w3c_actions.pointer_action.move_to_location(788, 865)
            actions.w3c_actions.pointer_action.release()
            actions.perform()

            el13 = self.driver.find_element(by=AppiumBy.XPATH, value='//android.widget.FrameLayout[@resource-id="com.google.android.gms:id/suc_layout_status"]/android.widget.LinearLayout/android.widget.LinearLayout/android.widget.Button')
            el13.click()

        except:
            pass

    def finish(self):
        self.driver.quit()
        # self.driver.execute_script("mobile: execEmuConsoleCommand", {'command': 'kill'})

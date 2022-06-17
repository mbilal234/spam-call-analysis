from abc import ABC, abstractmethod
import base64
import os
from time import sleep
import time

from appium.webdriver.common.appiumby import AppiumBy
from appium.webdriver.webdriver import WebDriver
from appium.webdriver.extensions.android.gsm import GsmCallActions

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.actions import interaction
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.actions.pointer_input import PointerInput

class AnalyzedApp(ABC):
    driver: WebDriver
    apk_directory: str
    app_terminates_blocked_calls: bool = False

    def __init__(self, driver, apk_directory):
        self.driver = driver
        self.apk_directory = apk_directory

    @property
    @abstractmethod
    def package_name(self) -> str:
        pass

    @property
    @abstractmethod
    def needs_google_account(self) -> bool:
        pass

    def install(self):
        self.driver.install_app(self.apk_directory + '/' + self.package_name + '.apk', grantPermissions=True)

    @abstractmethod
    def setup(self):
        pass

    def perform_analysis(self, numbers, output_file):
        
        accuracy = 0.95
        os.makedirs(f'out/{self.package_name}/screenshots', exist_ok=True)

        if not self.app_terminates_blocked_calls:
            image_allowed_file = f"reference_images/{self.package_name}/allowed-part.png"
            image_caution_file = f"reference_images/{self.package_name}/caution-part.png"
            image_blocked_file = f"reference_images/{self.package_name}/blocked-part.png"

            partial_screenshot_allow = base64.b64encode(open(image_allowed_file, "rb").read()).decode()
            partial_screenshot_block = base64.b64encode(open(image_blocked_file, "rb").read()).decode()

            check_caution = os.path.exists(image_caution_file)


            if(check_caution):
                partial_screenshot_cation = base64.b64encode(open(image_caution_file, "rb").read()).decode()


        for number in numbers:
            self.driver.lock()
            sleep(1)
            self.driver.make_gsm_call(number, GsmCallActions.CALL)
            # sleep(1)

            start = time.time()

            if self.app_terminates_blocked_calls:

                status = 'allowed'
                score = 1.0

                while (time.time() - start) < 2:
                    gsm_list: str = self.driver.execute_script("mobile: execEmuConsoleCommand", {'command': 'gsm list'})
                    if(gsm_list == ''):
                        status = 'blocked'
                        score = 1.0
                        break

            else:
        
                while True:
                    print('.', end=' ')
                    full_screenshot = self.driver.get_screenshot_as_base64()

                    try: 
                        el = self.driver.find_image_occurrence(full_screenshot, partial_screenshot_allow)
                        if(el['score'] > accuracy):
                            score = el['score']
                            status='allowed'
                            break

                    except: 
                        # Do nothing
                        pass

                    try: 
                        el = self.driver.find_image_occurrence(full_screenshot, partial_screenshot_block)
                        if(el['score'] > accuracy):
                            score = el['score']
                            status='blocked'
                            break

                    except: 
                        # Do nothing
                        pass

                    if(check_caution):
                        try: 
                            el = self.driver.find_image_occurrence(full_screenshot, partial_screenshot_cation)
                            if(el['score'] > accuracy):
                                status='caution'
                                score = el['score']
                                break

                        except: 
                            # Do nothing
                            pass

                    end = time.time()
                    delta = end - start

                    if delta > 10:
                        status='timeout'
                        score = 1.0
                        break

                    sleep(0.01)

            end = time.time()
            delta = end - start

            if(self.app_terminates_blocked_calls and status == 'allowed'):
                delta = 0.0

            print()
            filename = f'out/{self.package_name}/screenshots/{number}.png'
            self.driver.get_screenshot_as_file(filename=filename)

            self.driver.make_gsm_call(number, GsmCallActions.CANCEL)

            csv_line = f"{number},{self.package_name},{status},{delta},{score}"
            print(csv_line)
            with open(output_file, 'a') as fd:
                fd.write(f'{csv_line}\n')

            sleep(2)


    def uninstall(self):
        self.driver.remove_app(self.package_name)


class AllInOneCallerID(AnalyzedApp):
    package_name = 'com.allinone.callerid'
    needs_google_account = False

    def setup(self):
        self.driver.implicitly_wait(15)

        number: str = "+12025550103" # Fake, generated phone number
        self.driver.make_gsm_call(number, GsmCallActions.CALL)
        sleep(3)
        self.driver.make_gsm_call(number, GsmCallActions.CANCEL)

        sleep(2)

        self.driver.activate_app(self.package_name)

        sleep(5)

        el1 = self.driver.find_element(by=AppiumBy.ID, value="com.allinone.callerid:id/header_left")
        el1.click()
        el2 = self.driver.find_element(by=AppiumBy.ID, value="com.allinone.callerid:id/setting")
        el2.click()
        el3 = self.driver.find_element(by=AppiumBy.ID, value="com.allinone.callerid:id/country")
        el3.click()
        el4 = self.driver.find_element(by=AppiumBy.ID, value="com.allinone.callerid:id/et_search_country")
        el4.send_keys("Netherlands")
        el5 = self.driver.find_element(by=AppiumBy.XPATH, value='//android.widget.ListView[@resource-id="com.allinone.callerid:id/call_log_list"]/android.widget.LinearLayout[1]')
        el5.click()
        el6 = self.driver.find_element(by=AppiumBy.ACCESSIBILITY_ID, value="Back")
        el6.click()


        el7 = self.driver.find_element(by=AppiumBy.ACCESSIBILITY_ID, value="Grant permissions")
        el7.click()
        el8 = self.driver.find_element(by=AppiumBy.ID, value="com.allinone.callerid:id/fl_battery")
        el8.click()

        sleep(2)

        el9 = self.driver.find_element(by=AppiumBy.ID, value="android:id/button1")
        el9.click()


class CallAppContacts(AnalyzedApp):
    package_name = 'com.callapp.contacts'
    needs_google_account = True

    def setup(self):
        self.driver.activate_app('com.callapp.contacts')

        self.driver.implicitly_wait(6)

        sleep(5)

        el1 = self.driver.find_element(by=AppiumBy.XPATH,
                                       value='//android.widget.ListView[@resource-id="com.android.permissioncontroller:id/list"]/android.widget.LinearLayout[1]')
        el1.click()
        el2 = self.driver.find_element(by=AppiumBy.ID, value="android:id/button1")
        el2.click()

        sleep(1)

        el3 = self.driver.find_element(by=AppiumBy.XPATH,
                                       value='//android.widget.ListView[@resource-id="com.android.permissioncontroller:id/list"]/android.widget.LinearLayout[2]')
        el3.click()

        el4 = self.driver.find_element(by=AppiumBy.ID, value="android:id/button1")
        el4.click()

        sleep(2)

        el5 = self.driver.find_element(by=AppiumBy.ID, value="android:id/button1")
        el5.click()
        sleep(1)
        self.driver.hide_keyboard()
        el6 = self.driver.find_element(by=AppiumBy.ID, value="com.callapp.contacts:id/google_login_button_registration")
        el6.click()
        try:
            el7 = self.driver.find_element(by=AppiumBy.ID, value="com.google.android.gms:id/account_display_name")
            el7.click()
        except:
            pass

        try:
            el4 = self.driver.find_element(by=AppiumBy.ID, value="android:id/button1")
            el4.click()
            sleep(3)
        except:
            pass

        el8 = self.driver.find_element(by=AppiumBy.ID, value="com.callapp.contacts:id/btnLeft")
        el8.click()


class CallerIDBlock(AnalyzedApp):
    package_name = 'com.callerid.block'
    needs_google_account = False

    def setup(self):
        self.driver.activate_app('com.callerid.block')

        self.driver.implicitly_wait(15)

        el0 = self.driver.find_element(by=AppiumBy.ID, value="android:id/button1")
        el0.click()


        el1 = self.driver.find_element(by=AppiumBy.ACCESSIBILITY_ID, value="Learn more")
        el1.click()
        el2 = self.driver.find_element(by=AppiumBy.ID, value="com.callerid.block:id/setting")
        el2.click()
        el3 = self.driver.find_element(by=AppiumBy.ID, value="com.callerid.block:id/setting_bg")
        el3.click()

        els1 = self.driver.find_elements(by=AppiumBy.ANDROID_UIAUTOMATOR, value="new UiScrollable(new UiSelector().resourceId(\"com.callerid.block:id/call_log_list\")).scrollIntoView(new UiSelector().text(\"Netherlands\"));")
        el4 = self.driver.find_element(by=AppiumBy.ANDROID_UIAUTOMATOR, value="new UiSelector().text(\"Netherlands\");")
        el4.click()

        sleep(3)



class FlexAspectEveryCallControl(AnalyzedApp):
    package_name = 'com.flexaspect.android.everycallcontrol'
    needs_google_account = True

    def setup(self):
        self.driver.activate_app(self.package_name)

        self.driver.implicitly_wait(15)

        el1 = self.driver.find_element(by=AppiumBy.ID,
                                       value="com.flexaspect.android.everycallcontrol:id/first_start_wizard_next_btn")
        el1.click()
        el2 = self.driver.find_element(by=AppiumBy.ID,
                                       value="com.flexaspect.android.everycallcontrol:id/terms_checkbox")
        el2.click()
        el3 = self.driver.find_element(by=AppiumBy.ID,
                                       value="com.flexaspect.android.everycallcontrol:id/first_start_wizard_next_btn")
        el3.click()

        el4 = self.driver.find_element(by=AppiumBy.XPATH,
                                       value='//android.widget.ListView[@resource-id="com.android.permissioncontroller:id/list"]/android.widget.LinearLayout[2]')
        el4.click()

        el6 = self.driver.find_element(by=AppiumBy.ID, value="android:id/button1")
        el6.click()
        el7 = self.driver.find_element(by=AppiumBy.ACCESSIBILITY_ID, value="Google")
        el7.click()

        try:
            el8 = self.driver.find_element(by=AppiumBy.ID, value="com.google.android.gms:id/account_display_name")
            el8.click()
        except:
            pass

        el9 = self.driver.find_element(by=AppiumBy.ID, value="com.flexaspect.android.everycallcontrol:id/btnContinue")
        el9.click()

        el1 = self.driver.find_element(by=AppiumBy.ID,
                                       value="com.flexaspect.android.everycallcontrol:id/disable_hibernation_do_not_show")
        el1.click()
        el2 = self.driver.find_element(by=AppiumBy.ID, value="android:id/button1")
        el2.click()

        el14 = self.driver.find_element(by=AppiumBy.XPATH,
                                        value='//android.view.ViewGroup[@resource-id="com.flexaspect.android.everycallcontrol:id/bottom_app_bar"]/android.widget.HorizontalScrollView/android.widget.LinearLayout/android.widget.LinearLayout[5]')
        el14.click()

        el15 = self.driver.find_element(by=AppiumBy.ID,
                                        value="com.flexaspect.android.everycallcontrol:id/settings_battery_disable")
        el15.click()
        el16 = self.driver.find_element(by=AppiumBy.ID, value="android:id/button1")
        el16.click()


# Stop Calling Me - Call Blocker
class MglabScm(AnalyzedApp):
    package_name = 'com.mglab.scm'
    needs_google_account = False
    app_terminates_blocked_calls = True

    def setup(self):
        self.driver.activate_app(self.package_name)

        self.driver.implicitly_wait(15)

        el2 = self.driver.find_element(by=AppiumBy.ID, value="com.mglab.scm:id/next")
        el2.click()
        el2.click()
        el2.click()
        # Give time to download database
        sleep(5)
        el2.click()
        el2.click()



class Telguarder(AnalyzedApp):
    package_name = 'com.telguarder'
    needs_google_account = False

    def setup(self):
        self.driver.activate_app(self.package_name)

        self.driver.implicitly_wait(15)

        el1 = self.driver.find_element(by=AppiumBy.ID, value="com.telguarder:id/welcome_next_button")
        el1.click()
        el1.click()
        el1.click()
        el2 = self.driver.find_element(by=AppiumBy.ID, value="com.telguarder:id/welcome_next_button")
        el2.click()
        el3 = self.driver.find_element(by=AppiumBy.ID, value="com.telguarder:id/button_approve")
        el3.click()
        el4 = self.driver.find_element(by=AppiumBy.ID, value="com.telguarder:id/button_agree")
        el4.click()
        el5 = self.driver.find_element(by=AppiumBy.ID, value="android:id/button1")
        el5.click()
        el6 = self.driver.find_element(by=AppiumBy.ID, value="android:id/button1")
        el6.click()


class Truecaller(AnalyzedApp):

    package_name = 'com.truecaller'

    def setup(self):
        self.driver.activate_app(self.package_name)

        self.driver.implicitly_wait(15)


class WebascenderCallerID(AnalyzedApp):
    package_name = 'com.webascender.callerid'
    needs_google_account = False

    def setup(self):
        self.driver.activate_app(self.package_name)

        self.driver.implicitly_wait(8)

        el1 = self.driver.find_element(by=AppiumBy.ID, value="com.webascender.callerid:id/btn_get_started")
        el1.click()

        # //android.widget.ScrollView[@resource-id="com.webascender.callerid:id/scrollView"]/

        el2 = self.driver.find_element(by=AppiumBy.XPATH,
                                       value="//android.widget.ScrollView[@resource-id=\"com.webascender.callerid:id/scrollView\"]/android.widget.LinearLayout/android.widget.LinearLayout[3]/android.widget.LinearLayout/android.widget.Button")
        el2.click()
        el3 = self.driver.find_element(by=AppiumBy.ID, value="android:id/button1")
        el3.click()

        sleep(3)

        # el4a = self.driver.find_elements(by=AppiumBy.XPATH,
        #                                value="//android.widget.ScrollView[@resource-id=\"com.webascender.callerid:id/scrollView\"]/android.widget.LinearLayout/android.widget.LinearLayout[4]")

        el4 = self.driver.find_element(by=AppiumBy.XPATH,
                                       value="//android.widget.ScrollView[@resource-id=\"com.webascender.callerid:id/scrollView\"]/android.widget.LinearLayout/android.widget.LinearLayout[4]/android.widget.LinearLayout/android.widget.Button")
        el4.click()

        el5 = self.driver.find_element(by=AppiumBy.XPATH,
                                       value='//android.widget.ListView[@resource-id="com.android.permissioncontroller:id/list"]/android.widget.LinearLayout[2]')
        el5.click()
        el6 = self.driver.find_element(by=AppiumBy.ID, value="android:id/button1")
        el6.click()
        el7 = self.driver.find_element(by=AppiumBy.XPATH,
                                       value="//android.widget.FrameLayout[@resource-id=\"com.webascender.callerid:id/container\"]/android.widget.LinearLayout/android.widget.LinearLayout/android.widget.Button")
        el7.click()

        sleep(6)

        el8 = self.driver.find_element(by=AppiumBy.ID, value="com.webascender.callerid:id/bronzePriceTv")
        el8.click()
        el9 = self.driver.find_element(by=AppiumBy.ID, value="com.webascender.callerid:id/skipButton")
        el9.click()


class UnknownphoneCallblocker(AnalyzedApp):

    package_name = 'com.unknownphone.callblocker'
    needs_google_account = True

    def setup(self):
        self.driver.activate_app(self.package_name)
        self.driver.implicitly_wait(5)

        sleep(5)

        actions = ActionChains(self.driver)
        actions.w3c_actions = ActionBuilder(self.driver, mouse=PointerInput(interaction.POINTER_TOUCH, "touch"))
        actions.w3c_actions.pointer_action.move_to_location(1041, 1013)
        actions.w3c_actions.pointer_action.pointer_down()
        actions.w3c_actions.pointer_action.move_to_location(56, 1043)
        actions.w3c_actions.pointer_action.release()
        actions.perform()

        actions.w3c_actions = ActionBuilder(self.driver, mouse=PointerInput(interaction.POINTER_TOUCH, "touch"))
        actions.w3c_actions.pointer_action.move_to_location(1041, 1013)
        actions.w3c_actions.pointer_action.pointer_down()
        actions.w3c_actions.pointer_action.move_to_location(56, 1043)
        actions.w3c_actions.pointer_action.release()
        actions.perform()

        el1 = self.driver.find_element(by=AppiumBy.ID, value="com.unknownphone.callblocker:id/button")
        el1.click()
        el2 = self.driver.find_element(by=AppiumBy.ID, value="com.unknownphone.callblocker:id/notNowButton")
        el2.click()
        el3 = self.driver.find_element(by=AppiumBy.ID, value="com.unknownphone.callblocker:id/positiveButton")
        el3.click()
        el4 = self.driver.find_element(by=AppiumBy.ID, value="com.unknownphone.callblocker:id/button")
        el4.click()


class MistergroupShouldianswer(AnalyzedApp):

    package_name = 'org.mistergroup.shouldianswer'
    needs_google_account = False

    def setup(self):
        self.driver.activate_app(self.package_name)
        self.driver.implicitly_wait(5)

        sleep(10)

        el2 = self.driver.find_element(by=AppiumBy.ID, value="org.mistergroup.shouldianswer:id/butNext")
        el2.click()
        el2.click()
        el3 = self.driver.find_element(by=AppiumBy.ID, value="org.mistergroup.shouldianswer:id/checkReq1")
        el3.click()
        el5 = self.driver.find_element(by=AppiumBy.ID, value="org.mistergroup.shouldianswer:id/checkReq2")
        el5.click()
        el6 = self.driver.find_element(by=AppiumBy.ID, value="org.mistergroup.shouldianswer:id/butGetStarted")
        el6.click()
        el7 = self.driver.find_element(by=AppiumBy.ID, value="org.mistergroup.shouldianswer:id/butPassiveProtection")
        el7.click()
        sleep(2)
        el8 = self.driver.find_element(by=AppiumBy.ID, value="org.mistergroup.shouldianswer:id/butActionDefaultPhoneApp")
        el8.click()



import argparse
from ast import arg
import concurrent.futures
import multiprocessing
import inspect
import os
from queue import Queue
import threading
from time import sleep
import appsetupscripts
from appsetupscripts.driver_manager import DriverManager

from appsetupscripts.setup import AnalyzedApp
from appium import webdriver
from appium.webdriver.appium_service import AppiumService
from appsetupscripts.setup import *
from typing import Tuple


def find_subclasses(module, clazz):
    return [
        cls
        for name, cls in inspect.getmembers(module)
        if inspect.isclass(cls) and issubclass(cls, clazz) and (cls is not clazz)
    ]

def run_analysis_of_app(analyzed_app_cls: type, thread_index: int, apk_directory: str, output_file: str, args: argparse.Namespace):

    appium_service = AppiumService()
    appium_service.start(args=['--allow-insecure=emulator_console'])

    # Start driver
    print(analyzed_app_cls)
    
    driver_manager = DriverManager(thread_index, args.headless)

    app: AnalyzedApp = analyzed_app_cls(driver_manager.driver, apk_directory)

    if(app.needs_google_account):
        driver_manager.log_in_with_google_2(args.google_username, args.google_password) # TODO: Add real username + password
    
    driver_manager.set_swipe_lock_screen()
    driver_manager.silence_ringer()

    app.install()
    app.setup()

    sleep(3)

    app.perform_analysis(numbers, output_file)

    driver_manager.finish()

    appium_service.stop()
    print(appium_service.is_running)

    return f'Succesfully analyzed {analyzed_app_cls}'



if __name__ == '__main__':
    

    # Command Line Arguments
    parser = argparse.ArgumentParser(description='Test numbers on Android Spam Call Blocking Applications')
    parser.add_argument('--google_username', action='store', required=True, help="A google account's username")
    parser.add_argument('--google_password', action='store', required=True, help="A google account's password")
    parser.add_argument('--headless', action='store_true')
    args = parser.parse_args()

    # GENERAL CONSTANTS
    current_directory = os.path.dirname(os.path.abspath(__file__));
    apk_directory = current_directory + '/apks'

    time.strftime("%Y%m%d-%H%M%S")

    output_file = 'out/results'+time.strftime("%Y%m%d-%H%M%S")+'.csv'
    open(output_file, 'w').truncate(0) 

    numbers = ['+18009423767', '+16058844130', '+18666257291', '+18003535920', '+18888996650',
            '+13132631171', '+18558440114', '+18882224227', '+18442069035', '+18665320423',
            '+18558953393', '+18003219637', '+18662507212', '+18889346489', '+18776478552', 
            '+17204563720', '+18442068573', '+18554197365', '+18669145806', '+18009460332']


    # for cls in find_subclasses(appsetupscripts.setup, AnalyzedApp)[6:]:
    #     print(run_analysis_of_app(cls, 0, apk_directory, args))

    # run_analysis_of_app(CallAppContacts, 0, apk_directory, args)

    def worker(q, thread_index: int):
        while True:
            cls = q.get()
            run_analysis_of_app(cls, thread_index, apk_directory, output_file, args)
            q.task_done()

    q: Queue[type] = Queue()
    for i in range(1):
        t = threading.Thread(target=worker, args=[q, i])
        t.daemon = True
        t.start()


    for cls in find_subclasses(appsetupscripts.setup, AnalyzedApp):
        q.put( cls )

    q.join()       # block until all tasks are done






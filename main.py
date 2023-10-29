import logging
import subprocess
import argparse
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# Logger Konfiguration
logging.basicConfig(filename='reconnector.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Konstanten
SERVER_NAME = "google.com"
LOGOFF_URL = "http://logoff.now/"
LOGIN_URL = "https://wlan-login.oszimt.de/logon/cgi/index.cgi"


class DataInput:

    @staticmethod
    def get_arguments():
        """
        Function that parses arguments from the command line.
        :return: args: arguments from the command line
        """
        parser = argparse.ArgumentParser()
        parser.add_argument("-l", "--login", help="Login data username:password", required=True)
        args = parser.parse_args()
        return args

    def get_login_data(self):
        """
        Function that extracts login data from the command line arguments.
        :return: login_data: a list containing username and password
        """
        args = self.get_arguments()
        login_data = args.login.split(':')
        return login_data


class InternetConnectionChecker:

    def connection_to_server(self):
        """
        Function that checks the connection to a specific server.
        :return: boolean: True if connected, False otherwise
        """
        try:
            result = subprocess.run(['ping', '-c', '1', SERVER_NAME], stdout=subprocess.PIPE)
            return result.returncode == 0
        except Exception as e:
            logging.error(f"Error while trying to reach a server: {e}")
            return False


class AutoReconnect:

    def __init__(self, login_name: str, login_password: str):
        self.username = login_name
        self.password = login_password

    def reconnect_to_internet(self):
        """
        Function that manages the internet reconnection process.
        """
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        driver = webdriver.Chrome(options=chrome_options)
        try:
            if InternetConnectionChecker().connection_to_server():
                logging.info("[Reconnector]: Already connected to the internet.")
            else:
                driver.get(LOGOFF_URL)
                logging.info("[Reconnector]: You lost the connection to the Internet.")
                driver.get(LOGIN_URL)
                self.perform_login(driver)

        except Exception as e:
            logging.error(f"An error occurred while reconnecting to the internet: {e}")
        finally:
            driver.quit()

    def perform_login(self, driver):
        """
        Function that performs the login action on the webpage.
        """
        button = driver.find_element(By.CLASS_NAME, "ewc_s_button")
        name_field = driver.find_element(By.ID, "uid")
        pass_field = driver.find_element(By.ID, "pwd")

        name_field.send_keys(self.username)
        pass_field.send_keys(self.password)
        button.click()
        sleep(1)
        logging.info("[Reconnector]: Connection to the internet accomplished.")


if __name__ == "__main__":
    login_data = DataInput().get_login_data()
    reconnector = AutoReconnect(login_name=login_data[0], login_password=login_data[1])

    while True:
        reconnector.reconnect_to_internet()
        sleep(2)

import subprocess
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import argparse


class OszImtReconnector:
    def __init__(self):
        self.login_data = DataInput().get_login_data()
        self.login_name = self.login_data[0]
        self.login_password = self.login_data[1]

    def main(self):
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        driver = webdriver.Chrome(options=chrome_options)
        driver.quit()
        # Reconnect to the internet
        while True:
            AutoReconnect(self.login_name, self.login_password).reconnect_to_internet()
            sleep(2)


class DataInput:
    @staticmethod
    def get_arguments():
        """
        Function that gets the arguments from the command line.
        :return: args
        """
        try:
            parser = argparse.ArgumentParser()
            parser.add_argument("-l", "--login", help="Login data username:password", required=True)
            args = parser.parse_args()
            if args is not None:
                return args
            else:
                return None
        except Exception as e:
            print("An error occurred while parsing the arguments.", e)
            quit(-1)

    def get_login_data(self):
        """
        Function that gets the login_data from the args.
        :return: login_data
        """
        try:
            args = self.get_arguments()
            if args.login is not None:
                login_data = args.login
                login_data = str(login_data).split(':')
                return login_data
        except Exception as e:
            print("An error occurred while parsing the login_data.", e)
            quit(-1)


class InternetConnectionChecker:
    def __init__(self, server: str):
        self.server = server

    def connection_to_server(self):
        """
        Function which checks if a connection to a server is possible.
        :return: boolean
        """
        try:
            result = subprocess.run(['ping', '-c', '1', self.server], stdout=subprocess.PIPE)

            if result.returncode == 0:
                return True
            else:
                return False
        except Exception as e:
            print("An error occurred while trying to reach a server.", e)
            return False


class AutoReconnect:
    def __init__(self, login_name: str, login_password: str):
        self.username = login_name
        self.password = login_password
        self.internet_connection_checker = InternetConnectionChecker("google.com")

    def reconnect_to_internet(self):
        """
        Function which performs the reconnection process.
        """
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--disable-gpu')
            driver = webdriver.Chrome(options=chrome_options)

            if InternetConnectionChecker("google.com").connection_to_server():
                print("[Reconnector]: Already connected to the internet.")
            else:
                driver.get("http://logoff.now/")
                print("[Reconnector]: You lost the connection to the Internet.")
                driver.get("https://wlan-login.oszimt.de/logon/cgi/index.cgi")

                # search for the html elements.
                button = driver.find_element(By.CLASS_NAME, "ewc_s_button")
                name_filed = driver.find_element(By.ID, "uid")
                pass_field = driver.find_element(By.ID, "pwd")

                # Fill in the given information and click the button.
                name_filed.send_keys(self.username)
                pass_field.send_keys(self.password)
                button.click()
                sleep(1)
                print("[Reconnector]: Connection to the internet accomplished.")
        except KeyboardInterrupt as ke:
            print("Keyboard Interrupt the script will be stopped.", ke)
            quit(-1)
        except Exception as e:
            print("An error occurred while reconnecting to the internet.", e)
            quit(-1)


if __name__ == "__main__":
    app = OszImtReconnector()
    app.main()

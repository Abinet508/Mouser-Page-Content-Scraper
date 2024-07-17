import asyncio
import json
import os
import time
from requests_html import HTMLSession
import requests
import pandas as pd
import asyncio
import os
import time
from requests_html import HTMLSession
import pandas as pd
from multiprocessing import Pool
import urllib.parse
from speech_recognition.recognizers import google, whisper  
import speech_recognition as sr
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth
class FetchHTML:
    def __init__(self):
        self.session = HTMLSession()
        self.iteration = 0
        self.total = 0
        self.headless = False
        self.all_headers = {}
        self.cookies_dict = {"ASP.NET_SessionId": "", "CARTCOOKIEUUID": "", "akacd_Default_PR": "", "AKA_A2": "", "preferences": "", "__RequestVerificationToken": "", "LPVID": "", "LPSID-12757882": "", "enableFBPixel": "", "bm_mi": "", "ak_bmsc": "", "bm_sz": "", "OptanonAlertBoxClosed": "", "OptanonConsent": "", "__neoui": "", "datadome": "", "_abck": ""}
        self.url = "https://eu.mouser.com/ProductDetail/ABLIC/S-1112B18MC-L6DTFG?qs=9p6Jm05S21rEKVCeVDCHow%3D%3D"
        self.base_url = "https://eu.mouser.com/"
        self.current_path = os.path.abspath(os.path.dirname(__file__))
        
    def setup_env(self):
        try:
            with sync_playwright() as paywright:
                browser = paywright.firefox.launch(headless = self.headless ,devtools =False,firefox_user_prefs={'intl.accept_languages': 'en-US'})
                if os.path.exists(os.path.join(self.current_path,"firefox_storage_state.json")):
                    context = browser.new_context(storage_state= os.path.join(self.current_path,"firefox_storage_state.json"),java_script_enabled=True,locale="en-US")
                else:
                    context = browser.new_context(java_script_enabled=True,locale="en-US")
                page = context.new_page()
                stealth.stealth_sync((page))
                response = None
                while True:
                    try:
                        with page.expect_event("load", timeout=200000):
                            response = page.goto(self.base_url, wait_until='load', timeout=200000)
                            page.wait_for_load_state("networkidle")
                            self.all_headers = response.request.all_headers()
                            time.sleep(2)
                            page.wait_for_load_state("domcontentloaded")
                            currency_menue = page.wait_for_selector('[id="ddlCurrencyMenuButton"]', state='attached')
                            if currency_menue:
                                pass
                            else:
                                page.wait_for_selector('[sandbox="allow-scripts allow-same-origin allow-forms"]', state='attached')
                                
                                iframe = page.frame_locator('[sandbox="allow-scripts allow-same-origin allow-forms"]')
                                iframe.locator('//*[@id="captcha__audio__button"]').click()
                                input("Please login to the website and press Enter to continue...")
                        break
                    except Exception as e:
                        print(e)
                        time.sleep(5)
                        print("Retrying...")
                          
                page.screenshot(path=os.path.join(self.current_path,"firefox_screenshot.png"))
                print("Screenshot captured successfully.")
                
                locator = page.locator('[id="lnkAccntsOrds"]').all()
                
                if locator:
                    SelectedCurrencyId = page.locator('[id="SelectedCurrencyId"] >button').all_inner_texts()
                    if '$ USD' not in SelectedCurrencyId:
                        usd = page.get_by_role("link", name="$ USD").all()
                        while not usd:
                            page.get_by_role("button", name="€ EUR ").click()
                            usd = page.get_by_role("link", name="$ USD").all()
                        page.get_by_role("link", name="$ USD").click()
                        page.get_by_label("USD").click()
                        page.wait_for_load_state("domcontentloaded")
                    context.storage_state(path=os.path.join(self.current_path,"firefox_storage_state.json"))
                else:
                    try:
                        os.remove(os.path.join(self.current_path,"firefox_storage_state.json"))
                    except:
                        pass
                browser.close()

            return True
        except Exception as e:
            return False
        
    def progress_bar(self, iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
            """
            This function is used to display the progress bar

            Args:
                iteration (int): iteration number
                total (int): total number
                prefix (str): prefix string
                suffix (str): suffix string
                decimals (int): number of decimals
                length (int): length of the progress bar
                fill (str): fill character
                printEnd (str): print end character

            Returns:
                None
            """
            
            fill = '\033[92m█\033[0m'
            percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
            filledLength = int(length * iteration // total)
            bar = fill * filledLength + '-' * (length - filledLength)
            print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
            if iteration == total: 
                print(flush=True)
                
    async def save_html(self, response, PartNumber):
        """
        This function is used to save the html files

        Args:
            response (requests.models.Response): response object
            PartNumber (str): PartNumber of the product

        Returns:
            bool: True if the file is saved successfully, False otherwise
        """
        try:
            current_path = os.path.join(os.path.dirname(__file__), "html_files")
            os.makedirs(current_path, exist_ok=True)
            with open(f"{current_path}/{PartNumber}.html", "w", encoding="utf-8") as f:
                print(f"Downloading {PartNumber}...", end = "\r")
                f.write(response.text)
                return True
        except Exception as e:
            return False
        
    def fetch_url(self, url, params, PartNumber):
        """
        This function is used to fetch the url and save the html file

        Args:
            url (str): url of the product
            params (str): url of the product
            PartNumber (str): url of the product
        """
        headers = self.all_headers
        cookies = self.cookies_dict
        response = requests.get(url, headers=headers, params=params, cookies=cookies)
        if response.status_code == 200:
            asyncio.run(self.save_html(response, PartNumber))
        else:
            print(f"Failed to download {PartNumber} with status code {response.status_code}")

    async def main(self):
        """
        This function is used to read the list of urls and download the html files
        """
        df = pd.read_excel(os.path.join(self.current_path,"list_of_urls.xlsx"))
        self.total = len(df)
        urls = []
        params_list = []
        PartNumber_list = []
        for index, row in df.iterrows():
            PartNumber = row['PartNumber']
            url = row['URL']
            qs = urllib.parse.unquote(urllib.parse.urlparse(url).query)
            params = {
                'qs': qs.split("qs=")[1],
            }
            url = url.split("?qs=")[0]
            url = url.replace("https://www", "https://eu")
            urls.append(url)
            params_list.append(params)
            PartNumber_list.append(PartNumber)
            
        print("Downloading HTML files...")            
        with Pool(processes=50) as pool:
            pool.starmap(self.fetch_url, zip(urls, params_list, PartNumber_list))
        

    def get_cookies_from_storage(self, storage_state_path: str):
        """
        This function is used to get the cookies from the storage state file

        Args:
            storage_state_path (str): path of the storage state file
        """
        cookies = []
        with open(storage_state_path, "r") as f:
            storage_state = json.load(f)
            cookies = storage_state["cookies"]
        for cookie in cookies:
            if cookie["name"] in self.cookies_dict:
                self.cookies_dict[cookie["name"]] = cookie["value"]
    
if __name__ == "__main__":
    fetch_html = FetchHTML()
    result =fetch_html.setup_env()
    
    while not result:
        fetch_html.headless = False
        result =fetch_html.setup_env()
    fetch_html.get_cookies_from_storage(os.path.join(fetch_html.current_path,"firefox_storage_state.json"))
    asyncio.run(fetch_html.main())
    
    

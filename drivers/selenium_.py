import windscribe

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

windscribe.login('dimkov', 'Uiop1973')
windscribe.connect()
windscribe.logout()

options = webdriver.ChromeOptions()
options.add_argument('--no-sandbox')
options.add_argument('--headless')
options.add_argument('--disable-dev-shm-usage')
#options.add_argument('--proxy-server=82.33.214.117:8080')

driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
driver.get('https://sinonim.org/as/привет')
print(driver.page_source)
driver.quit()

'''
sudo apt install firefox chromium-browser
wget https://chromedriver.storage.googleapis.com/76.0.3809.68/chromedriver_linux64.zip
unzip chromedriver_linux64.zip
sudo mv chromedriver /usr/local/bin/chromedriver
sudo chown root:root /usr/local/bin/chromedriver
sudo chmod +x /usr/local/bin/chromedriver
'''
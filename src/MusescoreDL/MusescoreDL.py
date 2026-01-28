from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import os
import typer
from typing_extensions import Annotated

MAXWAITTIME = 30

def DownloadScore(url: Annotated[str, typer.Argument(help="The URL to the score you want to download")], folder_path: Annotated[str, typer.Option(help="The complete path to the folder you want the scores to be put in")] = os.getcwd()):
    driver = webdriver.Firefox()
    driver.minimize_window()
    driver.get(url)

    WebDriverWait(driver, MAXWAITTIME).until(EC.presence_of_element_located((By.ID, "jmuse-scroller-component")))
    pages = driver.find_elements(By.CLASS_NAME, "A8huy")
    for i in range(len(pages)):
        page = pages[len(pages)-i-1]
        driver.execute_script("arguments[0].scrollIntoView(true);", page)
        WebDriverWait(driver, MAXWAITTIME).until(EC.presence_of_element_located((By.XPATH, f"/html/body/div[2]/div[1]/section/main/div/div[3]/div/div/div[{len(pages)-i}]/img")))
        img = driver.find_element(By.XPATH, f"/html/body/div[2]/div[1]/section/main/div/div[3]/div/div/div[{len(pages)-i}]/img")
        WebDriverWait(driver, MAXWAITTIME).until(lambda _: img.get_attribute("src") != None)
        src = img.get_attribute("src")
        assert src != None
        with open(os.path.join(folder_path,f"score_{len(pages)-i-1}.svg"), "x+") as f:
            if len(pages)-i > 1:
                response = requests.get(src)
                if response.status_code != 200:
                    raise ConnectionError(f"Something went wrong while downloading sheet {len(pages)-i}")
                f.write(response.text)
            else:
                driver.get(src)
                f.write(driver.page_source)
    driver.close()
    
if __name__ == "__main__":
    DownloadScore(input("Musescore URL:    "))
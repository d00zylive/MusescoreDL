from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common import exceptions as selenium_exceptions
import requests
import os
import typer
from typing_extensions import Annotated
from tqdm import tqdm
import re
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF
from reportlab.graphics.shapes import Drawing
from pypdf import PdfWriter

def MergeSvgs(folder_path: str, file_name: str, cleanup: bool = True) -> None:
    score_pattern = re.compile(r"score_\d\.svg")
    for file in os.listdir(folder_path):
        if score_pattern.match(file):
            svg = svg2rlg(file)
            assert type(svg) == Drawing
            renderPDF.drawToFile(svg, f"{file[:-4]}.pdf")

    pdf_pattern = re.compile(r"score_\d\.pdf")
    pdf_writer = PdfWriter()
    for file in os.listdir(folder_path):
        if pdf_pattern.match(file):
            pdf_writer.append(file)
    pdf_writer.write(os.path.join(folder_path, file_name))
    
    delete_pattern = re.compile(r"score_\d\.(pdf|svg)")
    
    if cleanup:
        for file in os.listdir(folder_path):
                if delete_pattern.match(file):
                    os.remove(file)

def DownloadScore(url: Annotated[str, typer.Argument(help="The URL to the score you want to download")], folder_path: Annotated[str, typer.Option(help="The complete path to the folder you want the scores to be put in")] = os.getcwd(), max_wait_timeout: Annotated[int, typer.Option(help="The amount of time to wait for a page to load before concluding something has failed (Only change when wifi is slow)")] = 30, cleanup: Annotated[bool, typer.Option(help="Whether it should clean up all the files it creates. Only turn this off if you need singular sheets")] = True):
    score_pattern = re.compile(r"score_\d\.svg")
    if any([score_pattern.match(file) for file in os.listdir(folder_path)]):
        if input("Found a score in the folder, the program will not be able to run unless this is either moved or deleted.\nDo you want to delete all the scores in the folder? (y/n)    ").lower() == "y":
            
            for file in os.listdir(folder_path):
                if score_pattern.match(file):
                    os.remove(file)
    
    firefox_options = webdriver.FirefoxOptions()
    firefox_options.add_argument("--headless")
    driver = webdriver.Firefox(options=firefox_options)
    driver.get(url)
    try:
        WebDriverWait(driver, max_wait_timeout).until(EC.presence_of_element_located((By.ID, "jmuse-scroller-component")))
        pages = driver.find_elements(By.CLASS_NAME, "A8huy")
        
        for i in tqdm(range(len(pages)), unit="page"):
            page = pages[len(pages)-i-1]
            driver.execute_script("arguments[0].scrollIntoView(true);", page)
            WebDriverWait(driver, max_wait_timeout).until(EC.presence_of_element_located((By.XPATH, f"/html/body/div[2]/div[1]/section/main/div/div[3]/div/div/div[{len(pages)-i}]/img")))
            img = driver.find_element(By.XPATH, f"/html/body/div[2]/div[1]/section/main/div/div[3]/div/div/div[{len(pages)-i}]/img")
            WebDriverWait(driver, max_wait_timeout).until(lambda _: img.get_attribute("src") != None)
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
    except selenium_exceptions.TimeoutException:
        driver.close()
        raise TimeoutError("The page took too long to load. If nothing went wrong, try again with a higher max_wait_timeout")
    MergeSvgs(folder_path, "score.pdf", cleanup)
    
if __name__ == "__main__":
    DownloadScore(input("Musescore URL:    "))
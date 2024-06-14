
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.chrome.options import Options


import undetected_chromedriver as uc_orig
from selenium import webdriver
import time
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC



import json
import requests

import csv

# Make a new class from uc_orig.Chrome and redefine quit() function to suppress OSError
class Chrome(uc_orig.Chrome):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def quit(self):
        try:
            super().quit()
        except OSError:
            pass

if __name__ == "__main__":

    # Function to initialize the webdriver
    def init_driver():
        driver = Chrome(headless=False, use_subprocess=False)
        return driver

    def get_course_links(driver, page_number):
        url = f'https://www.udemy.com/topic/blender/?p={page_number}&sort=newest'
        driver.get(url)
        time.sleep(3)  # Adjust based on your internet speed
        links = driver.find_elements(By.CSS_SELECTOR, "div.course-list_container__6VTg9 div.course-card_main-content__aceQ0.course-card_has-price-text__KS6c_ > div:nth-child(1) > div > h3 > a")
        return [link.get_attribute('href') for link in links]

    def scrape_course_details(driver, link):
        driver.get(link)
        time.sleep(3)  # Adjust based on your internet speed

        def get_element_text(selector):
            try:
                return driver.find_element(By.CSS_SELECTOR, selector).text
            except:
                return "N/A"
            
        title = get_element_text("#main-content-anchor > div.top-container.dark-background > div > div > div:nth-child(3) > div > h1")
        author = get_element_text("#main-content-anchor > div.top-container.dark-background > div > div > div:nth-child(3) > div > div.clp-lead__element-item > div > span")
        course_id = driver.find_element(By.CSS_SELECTOR, "body").get_attribute("data-clp-course-id")
        description = get_element_text("div.ud-text-md.clp-lead__headline")
        badge = get_element_text("div.clp-lead__badge-ratings-enrollment > div:nth-child(1) > div")
        ratings_average = get_element_text("div.clp-lead__badge-ratings-enrollment .star-rating-module--rating-number--2-qA2")
        reviews = get_element_text("div.clp-lead__badge-ratings-enrollment .clp-lead__element-item--row > a > span:nth-child(2)")
        enrolled = get_element_text("div.clp-lead__badge-ratings-enrollment div.clp-lead__element-item.clp-lead__element-item--row > div")
        last_updated = get_element_text("#main-content-anchor div.clp-lead__element-meta > div:nth-child(1) > div > span")
        current_price = get_element_text("div.sidebar-container--purchase-section--XWCM- div.generic-purchase-section--buy-box-main--W9rN0 > div > div:nth-child(2)")
        total_length = get_element_text("#main-content-anchor div.curriculum--curriculum-sub-header--QqY6d > div > span > span > span")
        stats = get_element_text("#main-content-anchor div.curriculum--curriculum-sub-header--QqY6d > div > span")

        created_at = get_course_created_at(course_id) if course_id != "N/A" else "N/A"
        
        return {
            'title': title,
            'author': author,
            'course_id': course_id,
            'description': description,
            'badge': badge,
            'ratings_average': ratings_average,
            'reviews': reviews,
            'enrolled': enrolled,
            'last_updated': last_updated,
            'current_price': current_price,
            'total_length': total_length,
            'stats': stats,
            'created_at': created_at
        }
    
    def get_course_created_at(course_id):
        url = f"https://www.udemy.com/api-2.0/courses/{course_id}/?fields[course]=created"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            return data.get('created', 'N/A')
        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch creation date for course {course_id}: {e}")
            return "N/A"

    def scrape_website(max_pages):
        driver = init_driver()

        all_courses = []

        for page in range(1, max_pages + 1):
            print(f"Scraping page {page}")
            links = get_course_links(driver, page)
            for link in links:
                course_details = scrape_course_details(driver, link)
                all_courses.append(course_details)
                print(course_details)

        driver.quit()
        return all_courses

    max_pages = 1  # Change this to the number of pages you want to scrape
    courses = scrape_website(max_pages)
    # print(f"Scraped {len(courses)} courses")

    # Write data to CSV file
    with open('udemy_courses.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'title', 'author', 'course_id', 'description', 'badge', 
            'ratings_average', 'reviews', 'enrolled', 'last_updated', 
            'current_price', 'total_length', 'stats', 'created_at'
        ])
        writer.writeheader()
        writer.writerows(courses)

import undetected_chromedriver as uc_orig
import time
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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
    driver = Chrome(headless=False, use_subprocess=False)

    url = 'https://www.udemy.com/topic/blender/?sort=newest'
    # url = 'https://www.udemy.com/topic/blender'

    max_pages = 1

    def scrape_current_page():
        names, authors, descriptions, durations, lectures, difficulties, badges, original_prices, current_prices = ([] for _ in range(9))

        try:
            name_elements = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.course-list_container__6VTg9 div.course-card_main-content__aceQ0.course-card_has-price-text__KS6c_ > div:nth-child(1) > div > h3 > a'))
            )
            author_elements = driver.find_elements(By.CSS_SELECTOR, 'div.course-list_container__6VTg9 div.course-card_main-content__aceQ0.course-card_has-price-text__KS6c_ > div.ud-text-xs > div')
            description_elements = driver.find_elements(By.CSS_SELECTOR, 'div.course-list_container__6VTg9 div.course-card_main-content__aceQ0.course-card_has-price-text__KS6c_ > p')
            duration_elements = driver.find_elements(By.CSS_SELECTOR, 'div.course-list_container__6VTg9 div.course-card_main-content__aceQ0.course-card_has-price-text__KS6c_ > div.course-card-details_row__sWQ8g > div > span:nth-child(1)')
            lecture_elements = driver.find_elements(By.CSS_SELECTOR, 'div.course-list_container__6VTg9 div.course-card_main-content__aceQ0.course-card_has-price-text__KS6c_ > div.course-card-details_row__sWQ8g > div > span:nth-child(2)')
            difficulty_elements = driver.find_elements(By.CSS_SELECTOR, 'div.course-list_container__6VTg9 div.course-card_main-content__aceQ0.course-card_has-price-text__KS6c_ > div.course-card-details_row__sWQ8g > div > span:nth-child(3)')
            badge_elements = driver.find_elements(By.CSS_SELECTOR, 'div.course-list_container__6VTg9 div.course-card_main-content__aceQ0.course-card_has-price-text__KS6c_ > div.course-card_badges-container__UlZrV > div > div > div')
            original_price_elements = driver.find_elements(By.CSS_SELECTOR, 'div.course-list_container__6VTg9 .course-card_price-text-base-price-text-component-list-price__oJPz4.ud-text-sm > div > span:nth-child(2) > s > span')
            current_price_elements = driver.find_elements(By.CSS_SELECTOR, 'div.course-list_container__6VTg9 .course-card_price-text-base-price-text-component-discount-price__cZo6B.ud-heading-md > span:nth-child(2) > span')

            for i in range(len(name_elements)):
                names.append(name_elements[i].text if i < len(name_elements) else "")
                authors.append(author_elements[i].text if i < len(author_elements) else "")
                descriptions.append(description_elements[i].text if i < len(description_elements) else "")
                durations.append(duration_elements[i].text if i < len(duration_elements) else "")
                lectures.append(lecture_elements[i].text if i < len(lecture_elements) else "")
                difficulties.append(difficulty_elements[i].text if i < len(difficulty_elements) else "")
                badges.append(badge_elements[i].text if i < len(badge_elements) else "")
                original_prices.append(original_price_elements[i].text if i < len(original_price_elements) else "")
                current_prices.append(current_price_elements[i].text if i < len(current_price_elements) else "")

            df = pd.DataFrame({
                'Name': names,
                'Author': authors,
                'Description': descriptions,
                'Duration': durations,
                'Lectures': lectures,
                'Difficulty': difficulties,
                'Badge': badges,
                'Original Price': original_prices,
                'Current Price': current_prices
            })

            # Save the DataFrame to a CSV file, appending to the existing file
            df.to_csv('scraped_data.csv', mode='a', header=False, index=False)

        except Exception as e:
            print(f"An error occurred: {e}")

    driver.get(url)
    time.sleep(5)  # Wait for the page to load

    page_count = 1
    while page_count <= max_pages:
        scrape_current_page()

        try:
            next_button = driver.find_element(By.CSS_SELECTOR, '.pagination_next__aBqfT')
            next_button.click()
            time.sleep(5)  # Wait for the next page to load
            page_count += 1
        except Exception as e:
            print(f"Could not find the next button: {e}")
            break

    driver.quit()

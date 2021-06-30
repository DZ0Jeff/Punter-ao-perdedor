from logging import Handler
from time import sleep


def switch_ad_installation_popup(driver):
    handlers = driver.window_handles
    driver.switch_to_window(handlers[-1])


def remove_popup_odds(driver):
    ad_url = driver.current_url.split('#')

    if ad_url[-1] == "google_vignette":
        print('> Anúncio detectado! a tentar tirar-lo')
        ad_url.pop()
        driver.get(ad_url[0])


def scroll(driver):
    SCROLL_PAUSE_TIME = 20

    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page and increments one more second
        SCROLL_PAUSE_TIME += 1
        sleep(SCROLL_PAUSE_TIME)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height


def dynamic_page(driver):
    html = driver.find_element_by_tag_name('html')
    return html.get_attribute('outerHTML')


def check_tag(tag):
    try:
        handler = tag
        return handler

    except Exception as error:
        print('Error')
        return 'Não localizado...'

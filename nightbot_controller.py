from seleniumwire import webdriver
from os import path
import pickle
import asyncio

# driver = webdriver.Chrome(executable_path='resource/chromedriver')
async def initialize():
    return
    cookie_matters()
    driver.get('https://nightbot.tv/song_requests')
    driver.implicitly_wait(time_to_wait=5)
    login_with_twitch = driver.find_element_by_xpath('/html/body/div[2]/div/div[1]/div[2]/div/p[3]/button')
    login_with_twitch.click()
    driver.implicitly_wait(time_to_wait=5)
    auth_btn = driver.find_element_by_xpath('//*[@id="authorize_form"]/fieldset/button[1]')
    auth_btn.click()
    driver.implicitly_wait(time_to_wait=5)
    while True:
        await asyncio.sleep(10)

async def music_player_wrapper(session_length):
    # session_length in seconds
    return
    play_btn = driver.find_element_by_xpath('//*[@id="page-wrapper"]/div[2]/ui-view/player-controls/div/div/div[1]/button[1]')
    play_btn.click()
    await asyncio.sleep(session_length - 1)
    play_btn.click()


def cookie_matters(loadonly=True):
    return
    driver.get('https://twitch.tv/404')
    if path.isfile('log/twitch_cookie.dat'):
        f = open('log/twitch_cookie.dat', 'rb')
        cookies = pickle.load(f)
        f.close()
        for c in cookies:
            driver.add_cookie(c)
    driver.get('https://nightbot.tv/404')
    if path.isfile('log/nb_cookie.dat'):
        f = open('log/nb_cookie.dat', 'rb')
        cookies = pickle.load(f)
        f.close()
        for c in cookies:
            driver.add_cookie(c)
    if loadonly:
        return
    driver.get('https://nightbot.tv/dashboard')
    driver.get('https://twitch.tv/404')
    c = driver.get_cookies()
    with open('log/twitch_cookie.dat', 'wb+') as f:
        pickle.dump(c, f)
    driver.get('https://nightbot.tv/404')
    c = driver.get_cookies()
    with open('log/nb_cookie.dat', 'wb+') as f:
        pickle.dump(c, f)

if __name__ == '__main__':
    initialize()

import os.path
import random
import time
from contextlib import contextmanager
from typing import Generator, Tuple, Set

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from tqdm import tqdm

api_user = 'https://space.bilibili.com/{}/video'
api_profile = 'https://space.bilibili.com/{}'


@contextmanager
def make_chrome_browser(executable_path=None, headless=True):
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument('--headless')
        options.add_argument('--window-size=1920,1080')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
    options.add_experimental_option('useAutomationExtension', False)
    
    # Add additional options for Docker/Linux environment
    options.add_argument('--disable-setuid-sandbox')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-images')
    
    if executable_path:
        service = Service(executable_path=executable_path)
        browser = webdriver.Chrome(options=options, service=service)
    else:
        browser = webdriver.Chrome(options=options)
    
    try:
        yield browser
    finally:
        browser.quit()


def get_user_videos(browser, mid: int, max_pages: int = None, progress_callback=None) -> Generator[Tuple[str, str, str, str, str, str, str], None, None]:
    browser.get(api_user.format(mid))
    
    try:
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "bili-video-card"))
        )
    except TimeoutException:
        print("Timeout waiting for page to load")
        time.sleep(5)
    
    user_name = get_username(browser, mid)
    total_pages = get_total_pages(browser)
    
    if max_pages:
        total_pages = min(total_pages, max_pages)
    
    print(f"Found {total_pages} pages for user {user_name}")
    
    processed_bvids = set()
    
    # Use progress callback if provided, otherwise use tqdm
    if not progress_callback:
        p_bar = tqdm(total=total_pages, desc=f"Grabbing videos for {user_name}")
    
    current_page = 1
    while current_page <= total_pages:
        if progress_callback:
            progress_callback(current_page, total_pages, f"正在读取第 {current_page}/{total_pages} 页")
        else:
            p_bar.set_postfix(page=current_page)
        
        videos = parse_videos_on_page(browser, user_name)
        
        for video in videos:
            bvid = video[1]
            if bvid not in processed_bvids:
                processed_bvids.add(bvid)
                yield video
        
        if current_page < total_pages:
            if not click_next_page(browser):
                print(f"Failed to navigate to page {current_page + 1}")
                break
            time.sleep(2 + random.random())
        
        current_page += 1
        if not progress_callback:
            p_bar.update(1)
    
    if not progress_callback:
        p_bar.close()


def get_username(browser, mid):
    try:
        title = browser.title
        if '投稿视频' in title:
            return title.split('投稿视频')[0].strip()
        elif '的' in title:
            return title.split('的')[0].strip()
    except:
        pass
    
    return f"User_{mid}"


def get_user_nickname(mid: int, executable_path=None):
    """Fetch user nickname from their profile page"""
    with make_chrome_browser(executable_path=executable_path, headless=True) as browser:
        browser.get(api_profile.format(mid))
        
        try:
            # Wait for the page to load
            WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".nickname, .h-name, #h-name"))
            )
            
            # Try multiple selectors
            nickname_selectors = [
                ".nickname",
                ".h-name", 
                "#h-name",
                "[class*='nickname']",
                "[class*='name']"
            ]
            
            for selector in nickname_selectors:
                try:
                    elem = browser.find_element(By.CSS_SELECTOR, selector)
                    if elem and elem.text.strip():
                        return elem.text.strip()
                except:
                    continue
            
            # Fallback: try to get from page title
            title = browser.title
            if '的个人空间' in title:
                return title.split('的个人空间')[0].strip()
            
        except Exception as e:
            print(f"Error fetching nickname: {e}")
        
        return f"User_{mid}"


def get_total_pages(browser):
    try:
        # Try multiple selectors for pagination
        selectors = [
            "div.vui_pagenation",
            "div[class*='page']",
            ".be-pager",
            ".pagination-btn"
        ]
        
        for selector in selectors:
            try:
                pagination_elems = browser.find_elements(By.CSS_SELECTOR, selector)
                for elem in pagination_elems:
                    text = elem.text
                    import re
                    # Try different patterns
                    patterns = [
                        r'共\s*(\d+)\s*页',
                        r'(\d+)\s*页',
                        r'/\s*(\d+)',
                    ]
                    for pattern in patterns:
                        match = re.search(pattern, text)
                        if match:
                            pages = int(match.group(1))
                            print(f"Found {pages} total pages")
                            return pages
            except:
                continue
                
        # Fallback: try to find the last page number button
        try:
            page_buttons = browser.find_elements(By.CSS_SELECTOR, "button.be-pager-item, button[class*='page-item'], a.be-pager-item")
            page_numbers = []
            for btn in page_buttons:
                try:
                    num = int(btn.text.strip())
                    page_numbers.append(num)
                except:
                    continue
            if page_numbers:
                pages = max(page_numbers)
                print(f"Found {pages} pages from buttons")
                return pages
        except:
            pass
            
    except Exception as e:
        print(f"Error getting total pages: {e}")
    
    print("Could not determine total pages, defaulting to 1")
    return 1


def parse_videos_on_page(browser, user_name):
    videos = []
    html = BeautifulSoup(browser.page_source, "html.parser")
    video_cards = html.find_all('div', class_='bili-video-card')
    
    for card in video_cards:
        try:
            link_elem = card.find('a')
            if not link_elem or not link_elem.get('href'):
                continue
            
            url = link_elem['href']
            if not url.startswith('http'):
                url = 'https:' + url
            
            url = url.split('?')[0]
            bvid = url.strip("/").split("/")[-1]
            
            title = "Unknown"
            title_elem = card.find('div', class_='bili-video-card__title')
            if title_elem and title_elem.find('a'):
                title = title_elem.find('a').text.strip()
            elif link_elem.text:
                title = link_elem.text.strip()
            
            play_count = "0"
            duration = "00:00"
            
            cover_elem = card.find('div', class_='bili-video-card__cover')
            if cover_elem:
                spans = cover_elem.find_all('span')
                if len(spans) >= 1:
                    play_count = spans[0].text.strip()
                for span in spans:
                    if ':' in span.text:
                        duration = span.text.strip()
                        break
            
            pub_date = "Unknown"
            subtitle_elem = card.find('div', class_='bili-video-card__subtitle')
            if subtitle_elem:
                pub_date = subtitle_elem.text.strip()
            
            videos.append((url, bvid, user_name, title, play_count, pub_date, duration))
            
        except Exception as e:
            print(f"Error parsing video card: {e}")
            continue
    
    return videos


def click_next_page(browser):
    try:
        try:
            close_buttons = browser.find_elements(By.CSS_SELECTOR, "[class*='close'], [class*='Close'], .lt-icon-close")
            for btn in close_buttons:
                if btn.is_displayed():
                    btn.click()
                    time.sleep(0.5)
        except:
            pass
        
        next_button = None
        
        try:
            buttons = browser.find_elements(By.CSS_SELECTOR, "button.vui_pagenation--btn-side")
            for btn in buttons:
                if '下一页' in btn.text and 'disabled' not in btn.get_attribute('class'):
                    next_button = btn
                    break
        except:
            pass
        
        if not next_button:
            try:
                next_button = browser.find_element(By.XPATH, "//button[contains(text(), '下一页') and not(contains(@class, 'disabled'))]")
            except:
                pass
        
        if next_button:
            browser.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_button)
            time.sleep(0.5)
            
            try:
                next_button.click()
            except:
                try:
                    browser.execute_script("arguments[0].click();", next_button)
                except:
                    from selenium.webdriver import ActionChains
                    ActionChains(browser).move_to_element(next_button).click().perform()
            
            time.sleep(2)
            return True
        else:
            print("Next button not found or disabled")
            return False
            
    except Exception as e:
        print(f"Error clicking next page: {e}")
        try:
            browser.execute_script("""
                var buttons = document.querySelectorAll('button');
                for (var i = 0; i < buttons.length; i++) {
                    if (buttons[i].textContent.includes('下一页') && !buttons[i].disabled) {
                        buttons[i].click();
                        break;
                    }
                }
            """)
            time.sleep(2)
            return True
        except:
            return False
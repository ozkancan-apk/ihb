import random
import re
import asyncio
import requests
import io
import time
from faker import Faker
from account_generator_helper import CaptchaSolver, InboxKitten, TempMailPlus, GmailNator, TempMailLol, TempMail
import undetected_playwright as upw
from rich.console import Console
from rich.progress import track
from playwright.sync_api import BrowserContext

API_KEY = 'CMfXNtmJzpcjZRxCUCzEszLkQkJTeSEHcvDTrM98Lwnw'

fake = Faker()
captcha_solver = CaptchaSolver(API_KEY)
email_service = InboxKitten()
console = Console()

captcha_img_selector = "body .gform_wrapper .gform_body .gform_fields .gfield .gfield_captcha_container .gfield_captcha"
captcha_input_selector = "body .gform_wrapper .gform_body .gform_fields .gfield .gfield_captcha_container .gfield_captcha_input_container input"

def fetch_random_user_data():
    url = "https://randomuser.me/api/"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()["results"][0]
    else:
        console.print("API'den veri alınamadı.", style="bold red")
        return None

def generate_random_profile():
    user_data = fetch_random_user_data()
    if user_data:
        profile = {
            "gender": user_data["gender"],
            "name": f"{user_data['name']['first']} {user_data['name']['last']}",
            "location": user_data["location"],
            "email": user_data["email"],
            "username": user_data["login"]["username"],
            "password": user_data["login"]["password"],
            "dob": user_data["dob"]["date"],
            "phone": user_data["phone"],
            "picture": user_data["picture"]["large"],
            "nat": user_data["nat"]
        }
        return profile
    else:
        console.print("Random User Data API'sinden veri alınamadı.", style="bold red")
        return None

async def solve_captcha_and_continue(page):
    captcha_img_element = await page.query_selector(captcha_img_selector)
    if captcha_img_element:
        screenshot = await captcha_img_element.screenshot()
        captcha_solution = captcha_solver.solve(io.BytesIO(screenshot))
        if captcha_solution:
            await page.fill(captcha_input_selector, captcha_solution)
        else:
            console.print("Captcha çözülemiyor!", style="bold red")

async def get_random_coordinates():
    # Burada rastgele bir konum oluşturabilirsiniz.
    latitude = random.uniform(-90, 90)
    longitude = random.uniform(-180, 180)
    return latitude, longitude

async def run_instagram_signup():
    browser_type = upw.chromium
    browser = await browser_type.launch(headless=False)
    latitude, longitude = await get_random_coordinates()
    context = await browser.new_context(
        locale="en-US",
        geolocation={"longitude": longitude, "latitude": latitude},
        viewport={"width": 1170, "height": 2532}  # <-- Değişiklik burada
    )
    page = await context.new_page()

    profile = generate_random_profile()
    if not profile:
        return

    email = profile["email"]
    console.print(f"Kullanılacak e-posta: {email}")

    await page.goto("https://www.instagram.com/")
    time.sleep(5)
    await page.click('text="sign up"')
    time.sleep(2)
    await page.click('text="Email"')
    time.sleep(2)
    await page.fill('input[type="email"]', email)
    time.sleep(2)
    await page.click('text="Next"')
    print("Doğrulama kodu alınıyor...")

    await solve_captcha_and_continue(page)

    for _ in track(range(10), description="Waiting for verification email..."):
        if email_service.get_inbox():
            break
        await asyncio.sleep(1.5)

    for mail in email_service.get_inbox():
        content = mail.body
        code = re.findall(r'\b\d{6}\b', content)[0]
        console.print(f"Alınan doğrulama kodu: {code}")
        await page.fill('input[placeholder="Confirmation Code"]', code)
        await page.click('text="Next"')

    await page.fill('input[placeholder="Full Name"]', profile["name"])
    await page.fill('input[placeholder="Password"]', profile["password"])
    await page.click('text="Next"')
    await asyncio.sleep(30)
    await browser.close()

headless = True

def run(context: BrowserContext):
    page = context.new_page()
    page.goto("https://bot.sannysoft.com/")
    
    _suffix = "-headless" if headless else "-headful"
    page.screenshot(path=f"result/sannysoft{_suffix}.png", full_page=True)

def bytedance():
    browser = upw.chromium.launch(headless=headless)
    context = browser.new_context()
    upw.stealth_sync(context)  # Anti-bot tespitinden kaçınma için
    run(context)
    browser.close()

if __name__ == "__main__":
    choice = input("Hangi işlemi yapmak istersiniz? (1: Sannysoft Testi, 2: Instagram Kayıt): ").strip()
    
    if choice == "1":
        bytedance()
    elif choice == "2":
        asyncio.run(run_instagram_signup())
    else:
        console.print("Geçersiz seçim!", style="bold red")

import random
import time
import json
from faker import Faker
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from account_generator_helper import CaptchaSolver, InboxKitten, Proxies
from rich.progress import track
from rich.console import Console

# Configurations
API_KEY = 'CMfXNtmJzpcjZRxCUCzEszLkQkJTeSEHcvDTrM98Lwnw'

# Initialize
fake = Faker()
captcha_solver = CaptchaSolver(API_KEY)
email_service = InboxKitten()
console = Console()
proxy_helper = Proxies()

profiles = []

def get_new_proxy():
    proxy_helper.parse_proxies()
    proxy = proxy_helper.pop()
    return proxy.strfproxy()

def generate_random_profile():
    profile = {
        "username": fake.user_name(),
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "email": email_service.set_email(fake.user_name()),
        "password": fake.password(length=10)
    }
    gender = fake.random_element(elements=('male', 'female'))
    profiles.append({"profile": profile, "gender": gender})
    return profile, gender

def fill_instagram_signup_form(driver, profile):
    try:
        driver.find_element_by_name("emailOrPhone").send_keys(profile["email"])
        driver.find_element_by_name("fullName").send_keys(profile["first_name"] + " " + profile["last_name"])
        driver.find_element_by_name("username").send_keys(profile["username"])
        driver.find_element_by_name("password").send_keys(profile["password"])
    except Exception as e:
        console.print(f"[red]Error while filling form: {e}[/red]")
        console.print("[yellow]Please provide the required info.[/yellow]")

def solve_captcha(driver):
    try:
        captcha_image_element = driver.find_element_by_css_selector("YOUR_CAPTCHA_IMAGE_CSS_SELECTOR")
        captcha_image = captcha_image_element.screenshot_as_png
        captcha_solution = captcha_solver.solve(captcha_image)
        driver.find_element_by_css_selector("YOUR_CAPTCHA_INPUT_CSS_SELECTOR").send_keys(captcha_solution)
    except:
        console.print("[red]Couldn't solve the captcha![/red]")

def create_and_verify_account(driver):
    try:
        driver.find_element_by_xpath("//button[text()='Sign up']").click()
        for _ in track(range(10), description="Waiting for verification email..."):
            letters = email_service.get_inbox()
            for letter in letters:
                if "Instagram" in letter.sender:
                    code = "EXTRACT_CODE_FROM_LETTER"  # Email içeriğinden gerçek kodu çıkarın
                    driver.find_element_by_css_selector("YOUR_VERIFICATION_CODE_INPUT_CSS_SELECTOR").send_keys(code)
                    return
            time.sleep(10)
    except:
        console.print("[red]Couldn't create or verify the account![/red]")

def interact_with_other_profiles(driver, profiles):
    for profile_data in profiles:
        profile = profile_data["profile"]
        # Etkileşime girecek diğer profilleri seç
        target_profile = random.choice(profiles)["profile"]
        if profile_data['gender'] == 'female' and random.random() < 0.7:  # kadınların %70 olasılıkla mesaj atmasını simüle ediyoruz
            # Mesaj gönderme simülasyonu
            driver.get(f"https://www.instagram.com/{target_profile['username']}/")
            message_button = driver.find_element_by_css_selector("YOUR_MESSAGE_BUTTON_CSS_SELECTOR")
            message_button.click()
            message_input = driver.find_element_by_css_selector("YOUR_MESSAGE_INPUT_CSS_SELECTOR")
            message_input.send_keys(fake.sentence())
            send_button = driver.find_element_by_css_selector("YOUR_SEND_BUTTON_CSS_SELECTOR")
            send_button.click()
        else:
            # Beğeni yapma simülasyonu
            driver.get(f"https://www.instagram.com/{target_profile['username']}/")
            like_button = driver.find_element_by_css_selector("YOUR_LIKE_BUTTON_CSS_SELECTOR")
            like_button.click()

def run(mode, proxy=None):
    PROXY = proxy if proxy else get_new_proxy()
    chrome_options = Options()
    chrome_options.add_argument(f'--proxy-server={PROXY}')
    chrome_options.add_argument("--timeout=300")
    
    with webdriver.Chrome(options=chrome_options, executable_path="C:\\chromedriver.exe") as driver:
        if mode == "Human-like":
            # İnsan benzeri modda işlemleri gerçekleştirin
            pass  # Burada insana benzer davranışları simüle eden kodları ekleyebilirsiniz.
        else:
            for step in track(range(5), description="Creating Instagram Account..."):
                # Her adımda yapılacak şeyler...
                if step == 0:
                    # Instagram'a git
                    driver.get("https://www.instagram.com/accounts/emailsignup/")
                elif step == 1:
                    # Formu doldur
                    profile, gender = generate_random_profile()
                    fill_instagram_signup_form(driver, profile)
                elif step == 2:
                    # Captcha çözümle
                    solve_captcha(driver)
                elif step == 3:
                    # Hesap oluştur ve doğrula
                    create_and_verify_account(driver)
                elif step == 4:
                    # Diğer profillerle etkileşime gir
                    interact_with_other_profiles(driver, profiles)
                # Profil bilgilerini JSON'a kaydedin
                save_profile_to_json(profile, gender)

if __name__ == "__main__":
    main()






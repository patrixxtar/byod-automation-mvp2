from selenium.webdriver.common.by import By

CONFIG = {
    "target_url": "https://www.bell.ca/",
    "username": "baddaline1",
    "password": "Azul1234$",
    "plan_name": "Ultra",
    "upc_code": "UPC1",
    "esim_imei": "357498198275732",
    "first_name": "Bqat",
    "last_name": "Testing",
    "email": "test@yopmail.com",
    "phone": "4167020880",
    "address": "5115 creekbank",
    "card_number": "41111111111111111",
    "cvv": "233",
    "birthday": "01/01/1991",
    "review_url": "https://bell.ca/Order/Index#/OrderReview",
}

SELECTORS = {

    "popups": {
        "close": (By.ID, "close-lightbox"),
        "cookie_banner": (By.ID, "onetrust-accept-btn-handler"),
        "chat_minimize": (By.CLASS_NAME, "ujet-minimize"),
        "chat_close": (By.XPATH, "//div[@class='home_foot']//button[text()='No']")
    },

    "nav": {
        "mobile_menu": (By.ID, "mobileBarNavBtnG"),
        "mobility_btn": (By.XPATH, "//button[contains(., 'Mobility')]"),
        "plans_link": (By.XPATH, "//a[contains(@href, '/Mobility/Cell_phone_plans')]"),
    },

    "login": {
        "login_cta": (By.ID, "desktopLoginLink"),
        "username_input": (By.ID, "username"),
        "username_cta": (By.XPATH, "//button[contains(text(), 'Continue')]"),
        "password_input": (By.ID, "password"),
        "password_cta": (By.XPATH, "//button[contains(text(), 'Log in')]"),

    },

    "ciam": {
        "ciam_page": (By.XPATH, "//h1[contains(text(), 'Confirm your identity')]"),
        "otp_input": (By.ID, "code"),
        "otp_submit": (By.XPATH, "//button[contains(text(), 'Submit')]"),

    },

    "plans": {
        "plan_card": (By.XPATH, f"//h3[contains(text(), '{CONFIG['plan_name']}')]/ancestor::div[contains(@class,'card-plan')]"),
        "plan_button": (By.XPATH, ".//button[contains(text(),'Bring your own phone')]"),
        "carousel_next": (By.XPATH, "//button[contains(@class, 'slick-next')]"),
        "carousel_prev": (By.XPATH, "//buton[contains(@class, 'slick-prev')]"),
        "slick_dots": (By. CLASS_NAME, "slick-dots"),
    },

    "modals": {
        "new_customer_btn": (By.ID, "newCustomerButton"),
        "mobility_only_btn": (By.ID, "btnMobilityOnly"),
    },

    "plan_config": {
        "edit_btn": (By.ID, "editBtnRatePlanSection_SBPage"),
        "plan_tab": (By.ID, "tabpanel-pills-data-allotment"),
        "alt_plan": (By.XPATH, "//div[@id='tabpanel-pills-data-allotment']//h3[not(contains(text(), 'Ultra'))]/ancestor::div[contains(@class, 'graphical_ctrl_container')]"),
        "ultra_plan": (By.XPATH, "//div[@id='tabpanel-pills-data-allotment']//h3[contains(text(), 'Ultra')]/ancestor::div[contains(@class, 'graphical_ctrl_container')]"),
        "next_step": (By.ID, "next-step-button-1"),
    },

    "upc": {
        "upc_cta": (By.ID, "enterPromoCodeCTA"),
        "upc_input": (By.ID, "modal-enter-code"),
        "upc_submit": (By.ID, "submitbtn"),
        "accordion_container": (By.ID, "promoCode-accordion"),
        "accordions": (By.CSS_SELECTOR, "#promoCode-accordion .collapse-trigger"),
        "continue_btn": (By.ID, "promoCodeContinueBtn"),
        "add_ons_btn": (By.ID, "next-step-button-2"),
        
    },

    "device": {
        "imei_input": (By.ID, "imei-number"),
        "find_imei_link": (By.ID, "whereToFindImeiInfo"),
        "android_tab": (By.ID, "android"),
        "ios_tab": (By.ID, "iOS"),
        "close_imei_modal": (By.ID, "closeIMEIModalButton"),
        "success_icon": (By.CLASS_NAME, "icon-checkmark"),
        "add_to_cart": (By.ID, "addToCartCTA"),
        "psim_add_to_cart": (By.ID, "next-step-button-3"),
        "psim_option": (By.XPATH, "//label[@for='multiSimCard']"),
    },

    "cart": {
        "continue_btn": (By.XPATH, "//button[contains(text(), 'Continue to cart')]"),
        "offer_modal_title": (By.ID, "modal-addition-offers-title"),
        "offer_modal_close": (By.ID, "eligible_offers_lightbox"),
        "cart_confirmation": (By.XPATH, "//*[contains(text(), 'Order summary') or contains(text(), 'Cart')]"),
        "footer": (By.XPATH, "//nav[@aria-label='Privacy, security and legal'] | //nav[contains(@class, 'legal-links')]"),
        "checkout_btn": (By.ID, "next-step-button-undefined"),
    },
}

DEVICE_PROFILES = {
    "desktop": {
        "display_size": (2560, 1440),
        "mobile_emulation": None,
        "folder": "desktop-views"
    },

    "mobile": {
        "iphone_15_pro_max": {
            "display_size": (394, 852),
            "mobile_emulation": {
                "deviceMetrics": {"width": 394, "height": 852, "pixelRatio": 3.0, "touch": True},
                "userAgent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1"
            },
            "folder": "mobile-views"
        },
        "galaxy_s24_fe": {
            "display_size": (360, 780),
            "mobile_emulation": {
                "deviceMetrics": {"width": 360, "height": 780, "pixelRatio": 3.0, "touch": True},
                "userAgent": "Mozilla/5.0 (Linux; Android 14; SM-S721B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Mobile Safari/537.36"
            },
            "folder": "mobile-views"
        }
    },

    "tablet": {
        "tablet_mobile_ui": {
            "display_size": (820, 1180),
            "mobile_emulation": {
                "deviceMetrics": {"width": 820, "height": 1180, "pixelRatio": 2.0, "touch": True},
                "userAgent": "Mozilla/5.0 (iPad; CPU OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1"
            },
            "folder": "tablet-views"
        },
        "tablet_desktop_ui": {
            "display_size": (1366, 1024),
            "mobile_emulation": {
                "deviceMetrics": {"width": 1366, "height": 1024, "pixelRatio": 2.0, "touch": True},
                "userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15"
            },
            "folder": "tablet-views"
        }
    }
}
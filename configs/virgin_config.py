from selenium.webdriver.common.by import By

CONFIG = {
    "target_url": "https://www.virginplus.ca/",
    "plan_name": "60GB data, talk & text",
    "esim_imei": "357498198275732",
    "first_name": "Bqat",
    "last_name": "Testing",
    "email": "test@yopmail.com",
    "phone": "4167020880",
    "address": "5115 creekbank",
    "card_number": "4111111111111111",
    "cvv": "625",
    "birthday": "01/01/1991",
    "review_url": "https://myaccount.virginplus.ca/Eshop/Checkout#/OrderReview"
}

SELECTORS = {
    "popups": {
        "close": (By.XPATH, "//*[@id='close-lightbox'] | //a[contains(@class,'closeBtn')]"),
        "cookie_banner": (By.ID, "onetrust-accept-btn-handler"),
    },

    "nav": {
        "mobile_menu": (By.XPATH, "//a[contains(@class, 'accss-mobile-menu-button')]"),
        "login_cta": (By.XPATH, "//a[contains(@href, '/en/members-lounge/login.html')]"),
        "mobility_btn": (By.XPATH, "//div[@role='button' and contains(., 'Mobile')]"),
        "plans_link": (By.XPATH, "//a[contains(@href, '/en/hot-offers/byop.html')]"),
        "activate_now": (By.XPATH, "//a[text()='Select a plan' or text()='Activate now']")
    },

    "plans": {
        "plan_container": (By.XPATH, "//plan-container"),
        "dynamic_plan_container": (By.XPATH, f"//div[contains(@class, 'planHeading') and contains(., '{CONFIG['plan_name']}')]/ancestor::plan-container"),
        "plan_button": (By.XPATH, ".//a[@role='button' and contains(., 'Select plan')]")
    },

    "modals": {
        "new_customer_btn": (By.ID, "addaline-newline-heading-link2"),
        "loading_overlay1": (By.XPATH, "//div[contains(text(), 'Determining')]"),
        "loading_overlay2": (By.XPATH, "//div[contains(text(), 'Loading')]")
    },

    "plan_config": {
        "next_step": (By.ID, "next-step-button-1"),
        "edit_btn": (By.ID, "edit-rateplan-link"),
        "plan_tab": (By.ID, "tab-0"),
        "carousel_dots": (By.XPATH, "//ul[@id='radioCard-carousel-1-pagination']//button"),
        "plan_radios": (By.XPATH, "//input[@type='radio' and @name='rate-plan']")
    },

    "device": {
        "psim_option": (By.XPATH, "//input[@id='order-selection-radio']/parent::div"),
        "imei_input": (By.ID, "esim-number-input"),
        "loader": (By.XPATH, "//*[@aria-busy='true' and @role='alert']"),
        "find_imei_link": (By.ID, "find-esim-num-link"),
        "android_tab": (By.ID, "tab-Android-IMEI"),
        "ios_tab": (By.ID, "tab-iOS-IMEI"),
        "close_imei_modal": (By.ID, "modal-IMEI-Header-close-button"),
        "add_to_cart": (By.ID, "add-to-cart-button-1"),
    },

    "cart": {
        "checkout_btn": (By.ID, "proceed-to-checkout-button"),
        "footer": (By.XPATH, "//nav[@aria-label='Privacy, security and legal'] | //nav[contains(@class, 'legal-links')]")
    }
}
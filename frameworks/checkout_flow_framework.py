import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException

class CheckoutFlowFramework:
    def __init__(self, utils, config):
        self.utils = utils
        self.driver = utils.driver
        self.wait = utils.wait
        self.config = config

        self.locators = {
            "personal": {
                "first_name": (By.ID, "PersonalInformation_CustomerInformationViewModel_FirstName"),
                "last_name": (By.ID, "PersonalInformation_CustomerInformationViewModel_LastName"),
                "email": (By.ID, "PersonalInformation_CustomerInformationViewModel_EmailAddress"),
                "confirm_email": (By.ID, "PersonalInformation_CustomerInformationViewModel_ConfirmEmailAddress"),
                "phone": (By.ID, "PersonalInformation_BillingInformationViewModel_PhoneNumber"),
                "address": (By.ID, "PersonalInformation_BillingInformationViewModel_StreetAddress"),
                "address_dropdown": (By.CSS_SELECTOR, ".pca.pcalist .pcaitem"),
                "continue_btn": (By.ID, "id_SHIPPINGBILLING_CUSTOMERINFO_NEXT_LABEL"),
                "confirm_modal_title": (By.XPATH, "//*[@id='modal-confirm-information-title'] | //h2[contains(text(), 'Confirm information')]"),
                "confirm_btn": (By.XPATH, "//button[@data-dtname='Confirm information button on Checkout Personal Info step'] | //button[@id='confirm-billing-info-button']")
            },
            "number": {
                "new_number_label": (By.XPATH, "//*[contains(text(), 'Select a new number')]"),
                "first_phone_option": (By.XPATH, "//label[@for='current-option2-0'] | //label[@for='phoneNumber-1']"),
                "virgin_continue": (By.ID, "new-number-continue-button"),
                "bell_continue": (By.XPATH, "//*[@id='ContinueToPaymentInfo'] | //*[@id='linkToContinue']")
            },
            "shipping": {
                "container": (By.ID, "standardShipping-shipping-container"),
                "continue_btn": (By.XPATH, "//div[@id='shippingAddress']//button[contains(@data-dtname, 'Continue button')]")
            },
            "credit": {
                "payment_info_container": (By.XPATH, "//*[@id='paymentInfo'] | //*[@id='paymentDetails']"),
                
                # Mobile Accordions & Modals
                "mobile_summary_btn": (By.CSS_SELECTOR, 'a[data-target="#summary-view-details"], button#view-details-button'),
                "bell_price_accordion": (By.ID, "price-summary-accordion-button-1"),
                "bell_purchase_accordion": (By.ID, "purchase-accordion-button-2"),
                "why_purchase_mobile": (By.ID, "whyPurchaseOnlineBtnMobile"),
                "close_why_purchase_mobile": (By.CSS_SELECTOR, '#closeBtn-why-purchase-online-mobile, button#modal-title1-close-button'),
                
                # Desktop Modals
                "why_purchase_desktop": (By.ID, "whyPurchaseOnlineBtn"),
                "close_why_purchase_desktop": (By.ID, "closeBtn-why-purchase-online"),
                
                # Security Tooltips
                "tooltip_trigger_1": (By.ID, "cardNumberWhyModalTrigger"),
                "tooltip_close_1": (By.XPATH, "//*[@id='whyCreditCardClose'] | //button[contains(@id, '-close-button')]"),
                "tooltip_trigger_2": (By.XPATH, '//*[@aria-label="tooltip security code info"] | //a[@id="securityCodeModalTrigger"]'),
                "tooltip_close_2": (By.XPATH, "//*[@id='security-code-closeCTA'] | //*[@id='security-code-modal-close-button']"),
                
                # Card Details
                "card_number": (By.ID, "CreditCard_CardNumber"),
                "exp_month": (By.ID, "CreditCard_ExpirationDataMM"),
                "exp_month_target": (By.ID, "CreditCard_ExpirationDataMM-12"),
                "exp_year": (By.ID, "CreditCard_ExpirationDateYY"),
                "exp_year_target": (By.ID, "CreditCard_ExpirationDateYY-2035"),
                "cvv": (By.ID, "CreditCard_SecurityCode"),
                "dob": (By.XPATH, "//*[@id='PersonalInformation_CreditInformationViewModel_DateOfBirth'] | //input[@placeholder='MM/DD/YYYY']"),
                "continue_btn": (By.ID, "idhdnSHIPPINGBILLING_CUSTOMERINFO_NEXT_LABEL"),
                "error_banner_standard": (By.CLASS_NAME, "form-validation-errors"),
                "error_banner_pink": (By.CLASS_NAME, "vrui-bg-pink")
            },
            "review": {
                "submit_btn": (By.XPATH, "//*[@id='LinkToPlaceOrder'] | //*[@id='place-order-button']")
            }
        }

    # ==========================================
    # 🚀 MAIN FLOW EXECUTORS
    # ==========================================

    def esim_checkout_flow(self):
        self.fill_personal_info()
        self.setup_number()
        self.process_credit_check()
        self.review_page()

    def psim_checkout_flow(self):
        self.fill_personal_info()
        self.setup_number()
        self.shipping()
        self.process_credit_check()
        self.review_page()

    # ==========================================
    # 🧩 STEP IMPLEMENTATIONS
    # ==========================================

    def fill_personal_info(self):
        self.utils.wait_for_ready()
        print("--- CHECKOUT STEP 1: PERSONAL INFORMATION ---")
        locs = self.locators["personal"]

        def fill_field(locator, value):
            element = self.wait.until(EC.visibility_of_element_located(locator))
            element.clear()
            element.send_keys(value)
            self.driver.execute_script("arguments[0].dispatchEvent(new Event('blur'));", element)
            time.sleep(0.5)

        fill_field(locs["first_name"], self.config["first_name"])
        fill_field(locs["last_name"], self.config["last_name"])
        fill_field(locs["email"], self.config["email"])
        fill_field(locs["confirm_email"], self.config["email"])
        fill_field(locs["phone"], self.config["phone"])

        # Address Handling
        print("Entering address...")
        address_input = self.driver.find_element(*locs["address"])
        address_input.clear()
        address_input.send_keys(self.config["address"])

        self.wait.until(EC.visibility_of_element_located(locs["address_dropdown"]))
        time.sleep(1) 
        address_input.send_keys(Keys.ENTER)
        print("Address autocomplete triggered.")
        time.sleep(2)

        # Continue and Modal Handling
        self.utils.stable_click(locs["continue_btn"])

        try:
            self.wait.until(EC.visibility_of_element_located(locs["confirm_modal_title"]))
            self.utils.stable_click(locs["confirm_btn"])
            self.wait.until(EC.invisibility_of_element_located(locs["confirm_modal_title"]))
            print("Confirmed information modal.")
        except TimeoutException:
            print("No confirmation modal appeared.")

    def setup_number(self):
        self.utils.wait_for_ready()
        print("--- CHECKOUT STEP 2: NUMBER SETUP ---")
        locs = self.locators["number"]

        self.utils.stable_click(locs["new_number_label"])
        print("Waiting for numbers to populate...")
        time.sleep(2) 

        self.utils.stable_click(locs["first_phone_option"])
        print("Selected the first available phone number.")

        current_url = self.driver.current_url.lower()
        first_continue = None 

        if "virgin" in current_url or "virginplus" in current_url:
            try:
                time.sleep(1.5)
                first_continue = self.wait.until(EC.element_to_be_clickable(locs["virgin_continue"]))
            except Exception:
                pass
        elif "bell" in current_url:
            try:
                time.sleep(1.5)
                first_continue = self.wait.until(EC.element_to_be_clickable(locs["bell_continue"]))
            except Exception:
                pass

        if first_continue:
            self.utils.stable_click(first_continue)

        self.utils.stable_click(locs["bell_continue"]) 
        print("Clicked 'Continue' to move to Payment.")

    def shipping(self):
        self.utils.wait_for_ready()
        print("--- CHECKOUT STEP: SHIPPING ---")
        locs = self.locators["shipping"]
        self.wait.until(EC.presence_of_element_located(locs["container"]))
        try:
            self.utils.stable_click(locs["continue_btn"])
            print("Verifying navigation to Credit Check page...")
            self.wait.until(
                EC.presence_of_element_located(self.locators["credit"]["payment_info_container"]) 
            )
            print("✅ Successfully navigated to Credit Check.")
            
        except TimeoutException:
            raise Exception("❌ Shipping Continue failed: Navigation to Credit Check timed out.")
        except Exception as e:
            raise Exception(f"❌ Unexpected Shipping failure: {e}")

    def process_credit_check(self):
        self.utils.wait_for_ready()
        print("--- CHECKOUT STEP 3: CREDIT CHECK & ID IDENTIFICATION ---")
        locs = self.locators["credit"]
        self.wait.until(EC.presence_of_element_located(locs["payment_info_container"]))
        time.sleep(3)

        window_width = self.driver.execute_script("return window.innerWidth;")
        current_url = self.driver.current_url.lower()

        # Handle Viewport Specific Modals & Accordions
        if window_width < 768:
            print("Mobile context detected: Attempting summary and accordion steps.")
            try:
                self.utils.stable_click(locs["mobile_summary_btn"], timeout=5)
                if "bell" in current_url:
                    self.utils.stable_click(locs["bell_price_accordion"], timeout=5)
                    self.utils.stable_click(locs["bell_purchase_accordion"], timeout=5)
                    self.utils.stable_click(locs["why_purchase_mobile"], timeout=5)
                self.utils.stable_click(locs["close_why_purchase_mobile"], timeout=5)
            except Exception as e:
                print("Mobile accordions not found. Skipping section.")
        else:
            print("Desktop context detected: Attempting 'Why Purchase Online' check.")
            try:
                self.utils.stable_click(locs["why_purchase_desktop"])
                self.utils.stable_click(locs["close_why_purchase_desktop"])
            except Exception as e:
                print("Desktop 'Why Purchase Online' button not found. Skipping.")

        # Handle optional informational tooltips safely
        print("Handling optional security tooltips...")
        try:
            self.utils.stable_click(locs["tooltip_trigger_1"], timeout=2)
            self.utils.stable_click(locs["tooltip_close_1"], timeout=2)
            self.utils.stable_click(locs["tooltip_trigger_2"], timeout=2)
            self.utils.stable_click(locs["tooltip_close_2"], timeout=2)
        except Exception as e:
            print("Security tooltips skipped or not found.")

        time.sleep(2)
        
        # Card Details
        card_input = self.wait.until(EC.element_to_be_clickable(locs["card_number"]))
        card_input.clear()
        card_input.send_keys(self.config["card_number"])
        time.sleep(2)

        # Month Dropdown (With ActionChains Fallback)
        month_element = self.driver.find_element(*locs["exp_month"])
        if month_element.tag_name == "select":
            Select(month_element).select_by_index(len(Select(month_element).options) - 1)
        else:
            actions = ActionChains(self.driver)
            actions.move_to_element(month_element).click().perform()
            time.sleep(1)
            target_month = self.wait.until(EC.presence_of_element_located(locs["exp_month_target"]))
            try:
                actions.reset_actions()
                actions.move_to_element(target_month).click().perform()
            except Exception:
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'}); arguments[0].click();", target_month)

        time.sleep(1.5)

        # Year Dropdown
        year_element = self.driver.find_element(*locs["exp_year"])
        if year_element.tag_name == "select":
            Select(year_element).select_by_index(len(Select(year_element).options) - 1)
        else:
            actions = ActionChains(self.driver)
            actions.move_to_element(year_element).click().perform()
            time.sleep(1)
            target_year = self.wait.until(EC.visibility_of_element_located(locs["exp_year_target"]))
            actions.reset_actions()
            actions.move_to_element(target_year).click().perform()
                
        time.sleep(2)

        # CVV and DOB
        self.driver.find_element(*locs["cvv"]).send_keys(self.config["cvv"])
        self.driver.find_element(*locs["dob"]).send_keys(self.config["birthday"])
        time.sleep(3)

        self.utils.stable_click(locs["continue_btn"])

        # Validate Error Banner
        print("--- CHECKOUT STEP 3: VALIDATING CREDIT CHECK ---")
        try:
            error_banner = self.wait.until(
                EC.any_of(
                    EC.visibility_of_element_located(locs["error_banner_standard"]),
                    EC.visibility_of_element_located(locs["error_banner_pink"])
                )
            )
            print("✅ Success: Validation error detected as expected.")
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", error_banner)
            self.utils.flash_element(error_banner)
        except TimeoutException:
            print("⚠️ Warning: Credit check did not trigger the expected error banner.")

    def review_page(self):
        self.utils.wait_for_ready()
        print("--- CHECKOUT STEP 4: FINAL ORDER SUMMARY REVIEW ---")
        locs = self.locators["review"]

        target_url = self.config.get("review_url")
        if target_url:
            self.driver.get(target_url)
        else:
            print("Review page url not configured.")
            return
        
        self.utils.wait_for_ready()
        self.wait.until(EC.url_contains("OrderReview"))
        self.wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
        time.sleep(5) 

        submit_btn = self.wait.until(EC.element_to_be_clickable(locs["submit_btn"]))
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", submit_btn)
        time.sleep(2) 

        self.utils.stable_click(submit_btn)
        time.sleep(5)
        print("✅ E2E flow is completed successfully !")
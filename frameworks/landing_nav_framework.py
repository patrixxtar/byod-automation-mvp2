import time
from datetime import datetime, timezone, timedelta
from selenium.webdriver.support import expected_conditions as EC

class LandingNavigationFramework:
    def __init__(self, utils, config, selectors):
        self.utils = utils
        self.driver = utils.driver
        self.wait = utils.wait
        self.config = config
        self.s = selectors

    def open_site(self):
        print(f"Website: {self.config['target_url']}")
        
        # Ensure page is fully loaded
        self.wait.until(lambda d: d.execute_script("return document.readyState") == "complete")

        # Dismiss popups immediately
        self.utils.popup_handler.dismiss(self.s["popups"]["close"])
        self.utils.popup_handler.dismiss(self.s["popups"]["cookie_banner"])

    def login_flow(self):
        mobile_menu = self.driver.find_element(*self.s["nav"]["mobile_menu"])
        if mobile_menu.is_displayed():
            self.utils.stable_click(mobile_menu)
            self.utils.stable_click(self.s["login"]["mobile_login_cta"])
        else:
            self.utils.stable_click(self.s["login"]["desktop_login_cta"], scroll=False)
        
        username_input = self.wait.until(EC.visibility_of_element_located(self.s["login"]["username_input"]))
        username_input.clear()
        time.sleep(1)
        username_input.send_keys(self.config["username"])
        self.utils.bypass_captcha()
        username_cta = self.wait.until(EC.element_to_be_clickable(self.s["login"]["username_cta"]))
        self.utils.stable_click(username_cta)
        
        
        password_input = self.wait.until(EC.visibility_of_element_located(self.s["login"]["password_input"]))
        password_input.clear()
        password_input.send_keys(self.config["password"])
        password_cta = self.wait.until(EC.element_to_be_clickable(self.s["login"]["password_cta"]))
        self.utils.stable_click(password_cta)


    def complete_2fa(self):
        print("Detecting if CIAM is needed...")
        
        # Using find_elements prevents a sudden exception if the page hasn't fully loaded
        ciam_page_elements = self.driver.find_elements(*self.s["ciam"]["ciam_page"])
        
        if ciam_page_elements and ciam_page_elements[0].is_displayed():
            print("Executing CIAM 2FA process...")

            self.utils.stable_click(self.s["ciam"]["another_contact"])
            self.wait.until(EC.visibility_of_element_located(self.s["ciam"]["another_contact_option"]))

            email_option = self.wait.until(EC.element_to_be_clickable(self.s["ciam"]["email_option"]))
            self.utils.stable_click(email_option)
            time.sleep(2)

            self.wait.until(EC.visibility_of_element_located(self.s["ciam"]["otp_input"]))


            original_window = self.driver.current_window_handle
            self.driver.switch_to.new_window('tab')

            try:
                # Call the helper method to do the heavy lifting
                otp_code = self._fetch_otp()
                print(f"✅ Successfully retrieved OTP: {otp_code}")

            except Exception as e:
                print(f"⚠️ Failed to fetch OTP from ssqa.digital: {e}")
                self.driver.close()
                self.driver.switch_to.window(original_window)
                raise
                
            # Close the ssqa.digital tab and switch back to the CIAM tab
            self.driver.close()
            self.driver.switch_to.window(original_window)
            
            # Input the OTP into the CIAM page
            otp_input = self.wait.until(EC.visibility_of_element_located(self.s["ciam"]["otp_input"]))
            otp_input.clear()
            otp_input.send_keys(otp_code)
            
            # Submit the 2FA form
            self.utils.stable_click(self.s["ciam"]["otp_submit"])
            print("✅ 2FA submission complete.")

        else:
            print(f"CIAM page not displayed, skipping...")

    def navigate_byod(self):
        try:
            offer_close = self.driver.find_element(*self.s["modals"]["offer_close"])
            if offer_close.is_displayed():
                self.utils.stable_click(offer_close)
        except:
            pass

        mobile_menu = self.driver.find_element(*self.s["nav"]["mobile_menu"])
        if mobile_menu.is_displayed():
            self.utils.stable_click(mobile_menu)

        try:
            logout_cta = self.driver.find_element(*self.s["login"]["logout_cta"])
            if logout_cta.is_displayed():
                self.utils.stable_click(self.s["nav"]["mobility_btn"])
        except:
            pass

        self.utils.stable_click(self.s["nav"]["mobility_btn"])
        self.utils.stable_click(self.s["nav"]["plans_link"])

    def bell_navigate_device(self):
        mobile_menu = self.driver.find_element(*self.s["nav"]["mobile_menu"])
        if mobile_menu.is_displayed():
            self.utils.stable_click(mobile_menu)

        try:
            logout_cta = self.driver.find_element(*self.s["login"]["logout_cta"])
            if logout_cta.is_displayed():
                self.utils.stable_click(self.s["nav"]["mobility_btn"])
        except:
            pass

        self.utils.stable_click(self.s["nav"]["mobility_btn"])
        self.utils.stable_click(self.s["nav"]["device_link"])

    def bell_device_sb(self, has_upc=False):
        self._bell_select_device()
        self._bell_handle_modals()
        self.utils.wait_for_ready()
        self.utils.popup_handler.start_background_monitor()
        self.wait.until(EC.visibility_of_element_located(self.s["byod"]["imei_input"]))

    def bell_byod_sb(self, sim_type="esim", has_upc=False):
        self._bell_select_byod_plan()
        self._bell_handle_modals()
        self.utils.wait_for_ready()
        self.utils.popup_handler.start_background_monitor()
        self.wait.until(EC.visibility_of_element_located(self.s["byod"]["imei_input"]))
        if has_upc:
            self._bell_process_upc()
            self._bell_dynamic_byod_plan()
            self._bell_add_ons_step()
        else:
            self._bell_dynamic_byod_plan()
        
        self._bell_configure_sim(sim_type)
        self._bell_enter_cart()
        self.utils.popup_handler.stop_background_monitor()

    def virgin_byod_sb(self,sim_type="esim", is_mobile=False):
        self._virgin_select_byod_plan()
        self._virgin_handle_modals()
        self.utils.wait_for_ready()
        self.utils.popup_handler.start_background_monitor()
        
        is_mobile = self.driver.execute_script("return window.innerWidth;") < 768

        self.wait.until(EC.visibility_of_element_located(self.s["plan_config"]["next_step"]))
        self._virgin_dynamic_byod_plan(is_mobile)
        self._virgin_configure_sim(sim_type)
        self.utils.popup_handler.stop_background_monitor()

    def enter_checkout(self):
        self.utils.wait_for_ready()
        
        try:
            footer = self.driver.find_element(self.s["cart"]["footer"])
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'end'});", footer)
        except Exception:
            self.driver.execute_script("window.scrollTo({top: document.body.scrollHeight, behavior: 'smooth'});")

        time.sleep(3)
        self.utils.stable_click(self.s["cart"]["checkout_btn"])

    def _fetch_otp(self):
        self.driver.get("https://ssqa.digital")
        email_input = self.wait.until(EC.visibility_of_element_located(self.s["ciam"]["email_input"]))
        email_input.clear()
        email_input.send_keys(self.config["username"])
        self.utils.stable_click(self.s["ciam"]["open_inbox"])
        self.wait.until(EC.presence_of_element_located(self.s["ciam"]["inbox_container"]))
        time.sleep(1.5) 
        
        now_utc = datetime.now(timezone.utc)
        
        for attempt in range(3):
            email_rows = self.driver.find_elements(*self.s["ciam"]["email_rows"])
            
            for row in email_rows:
                try:
                    # Extract the ISO date string
                    date_el = row.find_element(*self.s["ciam"]["datetime"])
                    email_date_str = date_el.get_attribute("data-date")
                    email_time = datetime.fromisoformat(email_date_str)
                    if now_utc - email_time <= timedelta(minutes=5):
                        copy_btns = row.find_elements(*self.s["ciam"]["copy_code"])
                        
                        if copy_btns:
                            copy_btn = copy_btns[0]
                            self.utils.stable_click(copy_btn)
                            return copy_btn.get_attribute("data-code")
                except Exception:
                    pass
            
            if attempt < 2:
                print("Waiting for new email to arrive...")
                time.sleep(5)
                try:
                    refresh_btn = self.driver.find_element(By.ID, "refreshBtn")
                    self.utils.stable_click(refresh_btn)
                    time.sleep(2)
                except Exception:
                    self.driver.refresh()
                    self.wait.until(EC.presence_of_element_located(self.s["ciam"]["inbox_container"]))

        raise Exception("No Verification Code email found within the last 5 minutes after polling.")

        

# BELL SPECIFIC HELPER FUNCTIONS

    def _bell_select_byod_plan(self):
        plan_card = self.s["plans"]["plan_card"] 
        carousel_next_locator = self.s["plans"]["carousel_next"]
        carousel_prev = self.driver.find_element(*self.s["plans"]["carousel_prev"])

        if carousel_prev and carousel_prev.is_displayed():
            carousel_next = self.wait.until(EC.presence_of_element_located(carousel_next_locator))
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", carousel_next)
            time.sleep(1)
        
        for attempt in range(6):
            try:
                plan_cards = self.driver.find_elements(*plan_card)
                if plan_cards and plan_cards[0].is_displayed():
                    print(f"Found plan '{self.config['plan_name']}'!")
                    self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", plan_cards[0])
                    time.sleep(2)
                    cta = plan_cards[0].find_element(*self.s["plans"]["plan_button"])
                    self.utils.stable_click(cta)
                    return
            except Exception as e:
                print(f"Plan search attempt {attempt} failed: {e}")
            
            carousel_next = self.wait.until(EC.element_to_be_clickable(carousel_next_locator))
            if carousel_next.get_attribute("aria-disabled") == "true":
                break
            self.utils.stable_click(carousel_next, scroll=False)
            time.sleep(1.5)
                
        raise Exception(f"Failed to find plan: {self.config['plan_name']}")

    def _bell_handle_modals(self):
        # Ensure modal buttons are visible before interacting
        print("Handling setup modals...")
        self.wait.until(EC.element_to_be_clickable(self.s["modals"]["new_customer_btn"]))
        self.utils.stable_click(self.s["modals"]["new_customer_btn"])
        
        self.wait.until(EC.element_to_be_clickable(self.s["modals"]["mobility_only_btn"]))
        self.utils.stable_click(self.s["modals"]["mobility_only_btn"])

    def _bell_process_upc(self):
        self.utils.wait_for_ready()
        self.wait.until(EC.visibility_of_element_located(self.s["byod"]["imei_input"]))
        print("--- PROCESSING UPC CODE ---")
        if "upc_code" not in self.config:
            raise ValueError("UPC code missing from configuration.")

        self.utils.stable_click(self.s["upc"]["upc_cta"])
        upc_input = self.wait.until(EC.visibility_of_element_located(self.s["upc"]["upc_input"]))
        upc_input.clear()
        upc_input.send_keys(self.config["upc_code"])
        self.driver.execute_script("arguments[0].dispatchEvent(new Event('blur'));", upc_input)
        self.utils.stable_click(self.s["upc"]["upc_submit"])
        
        self.utils.wait_for_ready()
        self.wait.until(EC.visibility_of_element_located(self.s["upc"]["accordion_container"]))
        accordions = self.driver.find_elements(*self.s["upc"]["accordions"])
        for btn in accordions:
            # stable_click handles the scroll, visibility, and native click interaction
            self.utils.stable_click(btn)
            
            # Brief pause to allow the native UI animation to complete
            time.sleep(0.5)
        
        self.utils.wait_for_ready()
        self.utils.stable_click(self.s["upc"]["continue_btn"])
        self.utils.wait_for_ready(wait_for_modals=True)

    def _bell_dynamic_byod_plan(self):
        self.utils.wait_for_ready()
        print("--- PERFORMING DYNAMIC PLAN RE-SELECTION ---")
        try:
            plan_tab_elements = self.driver.find_elements(*self.s["plan_config"]["plan_tab"])

            if not plan_tab_elements or not plan_tab_elements[0].is_displayed():
                self.utils.stable_click(self.s["plan_config"]["edit_btn"])


            self.wait.until(EC.visibility_of_element_located(self.s["plan_config"]["plan_tab"]))
            self.utils.wait_for_ready()
            time.sleep(1.5)

            self.utils.stable_click(self.s["plan_config"]["alt_plan"])
            self.utils.wait_for_ready()
            time.sleep(2.0)
            
            self.utils.stable_click(self.s["plan_config"]["ultra_plan"])
            self.utils.wait_for_ready()
            time.sleep(2.0)

            next_btn = self.wait.until(EC.element_to_be_clickable(self.s["plan_config"]["next_step"]))
            self.utils.stable_click(next_btn)
            
            self.utils.wait_for_ready()
            print("✅ Plan re-selection completed.")
        except Exception as e:
            print(f"⚠️ Plan re-selection skipped or failed: {e}")

    def _bell_add_ons_step(self):
        self.utils.wait_for_ready()
        try:
            print("--- PROCEEDING PAST ADD-ONS ---")
            add_ons_btn = self.wait.until(EC.element_to_be_clickable(self.s["upc"]["add_ons_btn"]))
            self.utils.stable_click(add_ons_btn)
            self.utils.wait_for_ready()
            print("✅ Successfully advanced past Add-ons.")
        except Exception as e:
            print(f"⚠️ Failed to click add_ons_btn: {e}")

    def _bell_configure_sim(self, sim_type="esim"):
        print(f"--- CONFIGURING SIM / IMEI FOR: {sim_type.upper()} ---")
        self.utils.wait_for_ready()
        self.wait.until(EC.visibility_of_element_located(self.s["byod"]["imei_input"]))

        try:
            find_imei = self.driver.find_element(*self.s["byod"]["find_imei_link"])
            if find_imei.is_displayed():
                self.utils.stable_click(find_imei)
                time.sleep(1)
                
                try:
                    self.utils.stable_click(self.s["byod"]["android_tab"], timeout=2)
                    time.sleep(1)
                    self.utils.stable_click(self.s["byod"]["ios_tab"], timeout=2)
                    time.sleep(1)
                except Exception:
                    pass

                self.utils.stable_click(self.s["byod"]["close_imei_modal"])
        except Exception:
            pass

        self.utils.wait_for_ready()
        self.wait.until(EC.invisibility_of_element_located(self.s["byod"]["close_imei_modal"]))

        imei = self.wait.until(EC.visibility_of_element_located(self.s["byod"]["imei_input"]))
        imei.clear()
        
        if sim_type == "psim":
            self.utils.stable_click(self.s["byod"]["psim_option"])
            self.utils.wait_for_ready()
            self.utils.stable_click(self.s["byod"]["psim_add_to_cart"])
        else:
            imei.send_keys(self.config["esim_imei"])
            self.driver.execute_script("arguments[0].dispatchEvent(new Event('blur'));", imei)

            print("Waiting for IMEI validation...")
            self.wait.until(EC.visibility_of_element_located(self.s["byod"]["success_icon"]))
            print("✅ IMEI validated!")
            self.utils.wait_for_ready()
            self.utils.stable_click(self.s["byod"]["add_to_cart"])
        
    def _bell_enter_cart(self):
        self.utils.wait_for_ready()
        print("Transitioning to cart...")

        try:
            print("Checking for potential offers lightbox...")
            self.wait.until(EC.visibility_of_element_located(self.s["cart"]["offer_modal_title"]))
            self.utils.stable_click(self.s["cart"]["offer_modal_close"])
            print("Offers lightbox dismissed.")
        except:
            print("No offers lightbox detected. Proceeding.")
            try:
                self.utils.stable_click(self.s["cart"]["continue_btn"])
            except Exception as e:
                print(f"⚠️ Cart continue button failed: {e}")

        try:
            self.wait.until(EC.presence_of_element_located(self.s["cart"]["cart_confirmation"]))
            print("✅ Successfully reached final Cart page.")
        except Exception as e:
            print(f"⚠️ Could not confirm reach of final cart: {e}")


# VIRGIN SPECIFIC FUNCTIONS

    def _virgin_select_byod_plan(self):
        self.utils.stable_click(self.s["nav"]["activate_now"])
        time.sleep(3)

        dynamic_plan_locator = self.s["plans"]["dynamic_plan_container"]
        plan_card = self.wait.until(EC.presence_of_element_located(dynamic_plan_locator))
        

        for attempt in range(6):
            try:
                if plan_card.is_displayed():
                    print(f"Found plan '{self.config['plan_name']}'!")
                    break
            except Exception:
                pass

        all_plans = self.driver.find_elements(*self.s["plans"]["plan_container"])
        try:
            self.virgin_plan_index = [i for i, el in enumerate(all_plans, 1) if el.id == plan_card.id][0]
        except:
            self.virgin_plan_index = 1

        # FIX 4: Unpack the tuple using the * operator
        plan_button = plan_card.find_element(*self.s["plans"]["plan_button"])
        self.utils.stable_click(plan_button)

    def _virgin_handle_modals(self):
        self.wait.until(EC.element_to_be_clickable(self.s["modals"]["new_customer_btn"]))
        self.utils.stable_click(self.s["modals"]["new_customer_btn"])
        
        # Wait for loading screens to clear
        try:
            self.wait.until(EC.invisibility_of_element_located(self.s["modals"]["loading_overlay1"]))
            self.wait.until(EC.invisibility_of_element_located(self.s["modals"]["loading_overlay2"]))
        except:
            pass

    def _virgin_dynamic_byod_plan(self, is_mobile=False):
        self.utils.wait_for_ready()
        print("--- PERFORMING DYNAMIC PLAN RE-SELECTION ---")
        self.utils.stable_click(self.s["plan_config"]["next_step"])

        try:
            self.wait.until(EC.invisibility_of_element_located(self.s["device"]["loader"]))
        except:
            pass
        
        self.wait.until(EC.visibility_of_element_located(self.s["device"]["imei_input"]))
        self.utils.stable_click(self.s["plan_config"]["edit_btn"])
        self.wait.until(EC.visibility_of_element_located(self.s["plan_config"]["plan_tab"]))
        
        try:
            if is_mobile:
                dots = self.driver.find_elements(*self.s["plan_config"]["carousel_dots"])
                for dot in dots[1:]:
                    self.utils.stable_click(dot)
                    time.sleep(1.2)
                if dots:
                    self.utils.stable_click(dots[0])

            # Radio Toggle Logic
            plan_radios = self.wait.until(EC.presence_of_all_elements_located(self.s["plan_config"]["plan_radios"]))
            target_index = getattr(self, "virgin_plan_index", 1)
            alt_index = 0 if target_index != 1 else 1
            self.utils.stable_click(plan_radios[alt_index])
            time.sleep(2)
            
            plan_radios = self.wait.until(EC.presence_of_all_elements_located(self.s["plan_config"]["plan_radios"]))
            self.utils.stable_click(plan_radios[getattr(self, "virgin_plan_index", 1)])
            time.sleep(2)
            self.utils.stable_click(self.s["plan_config"]["next_step"])

            self.utils.wait_for_ready()
            print("✅ Plan re-selection completed.")
        except Exception as e:
            print(f"⚠️ Plan re-selection skipped or failed: {e}")

    def _virgin_configure_sim(self, sim_type="esim"):
        print(f"--- CONFIGURING SIM / IMEI FOR: {sim_type.upper()} ---")
        self.utils.wait_for_ready()
        self.wait.until(EC.visibility_of_element_located(self.s["device"]["imei_input"]))
        try:
            self.wait.until(EC.invisibility_of_element_located(self.s["device"]["loader"]))
        except:
            pass

        try:
            find_imei = self.driver.find_element(*self.s["device"]["find_imei_link"])
            if find_imei.is_displayed():
                self.utils.stable_click(find_imei)
                time.sleep(1)

                try:
                    self.utils.stable_click(self.s["device"]["android_tab"], timeout=2)
                    time.sleep(1)
                    self.utils.stable_click(self.s["device"]["ios_tab"], timeout=2)
                    time.sleep(1)
                except Exception:
                    pass

                self.utils.stable_click(self.s["device"]["close_imei_modal"])
        except:
            pass

        self.wait.until(EC.invisibility_of_element_located(self.s["device"]["close_imei_modal"]))
        self.utils.wait_for_ready()

        if sim_type == "psim":
            # Logic for Physical SIM
            self.utils.stable_click(self.s["device"]["psim_option"])
        else:
            # Logic for eSIM
            imei_input = self.driver.find_element(*self.s["device"]["imei_input"])
            imei_input.clear()
            imei_input.send_keys(self.config["esim_imei"])
            # Trigger validation event
            self.driver.execute_script("arguments[0].dispatchEvent(new Event('blur'));", imei_input)
            print("✅ IMEI validated!")
        
        self.utils.wait_for_ready()
        self.utils.stable_click(self.s["device"]["add_to_cart"])
        

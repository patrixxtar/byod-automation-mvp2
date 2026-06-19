import time
import threading
import subprocess
import glob
import os
from pathlib import Path
from typing import Callable, Optional, List, Union, Tuple
from pyvirtualdisplay import Display

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    StaleElementReferenceException,
    TimeoutException,
)


class BrowserContext:
    def __init__(self, display_size=(2560, 1440), mobile_emulation=None, target_url=None):
        self.display_size = display_size
        self.mobile_emulation = mobile_emulation
        self.target_url = target_url
        self.display = None
        self.driver = None

    def start(self):
        self.display = Display(visible=0, size=self.display_size)
        self.display.start()

        options = Options()

        if self.mobile_emulation:
            options.add_experimental_option("mobileEmulation", self.mobile_emulation)
            args = [
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-features=WebPayments",
                f"--app={self.target_url}",
                f"--window-size={self.display_size[0]},{self.display_size[1]}"
            ]
        else:
            args = [
                "--no-sandbox",
                "--disable-dev-shm-usage",
                f"--window-size={self.display_size[0]},{self.display_size[1]}",
                "--start-maximized",
                "--disable-features=WebPayments"
            ]

        # Explicitly bind Chromium to the PyVirtualDisplay display server port
        if self.display.display is not None:
            args.append(f"--display=:{self.display.display}")

        for a in args:
            options.add_argument(a)

        prefs = {
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False,
            "autofill.credit_card_enabled": False,
            "autofill.profile_enabled": False,
        }

        options.add_experimental_option("prefs", prefs)
        
        # Modern approach to hide the "Chrome is being controlled by automated software" banner
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 15)

        if self.mobile_emulation is None and self.target_url:
            self.driver.get(self.target_url)

        return self


    def stop(self):
        if self.driver:
            self.driver.quit()
        if self.display:
            self.display.stop()


# =========================================================
# 🎥 SCREEN RECORDING MODULE
# =========================================================


class ScreenRecorder:

    def __init__(self):
        self.video_recorder: Optional[subprocess.Popen] = None
        self.current_recording_file: Optional[str] = None

    def start(self, display_num: int, display_size: tuple, file_name: str):

        Path(file_name).parent.mkdir(parents=True, exist_ok=True)
        self.current_recording_file = file_name

        ffmpeg_cmd = [
            "ffmpeg", "-y",
            "-f", "x11grab",
            "-draw_mouse", "0",
            "-video_size", f"{display_size[0]}x{display_size[1]}",
            "-i", f":{display_num}.0+0,0",
            "-codec:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-r", "24",
            "-preset", "ultrafast",
            "-tune", "zerolatency",
            file_name
        ]

        self.video_recorder = subprocess.Popen(
            ffmpeg_cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        print("🎥 Recording started...")
   
    def stop(self):

        if getattr(self, "video_recorder", None):
            self.video_recorder.terminate()

            try:
                self.video_recorder.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.video_recorder.kill()
                self.video_recorder.wait()

        self._compress()
        print("🎥 Recording stopped safely")

    def _compress(self):
        if hasattr(self, 'current_recording_file'):
            input_path = Path(self.current_recording_file)
            if input_path.exists():
                compressed_path = input_path.with_name(f"compressed_{input_path.name}")
                    
                print(f"🤐 Compressing recording... {input_path.name}")
                    
                # -crf 23 to 28 is the sweet spot for great compression vs quality
                compress_cmd = [
                    "ffmpeg", "-y", "-i", str(input_path),
                    "-codec:v", "libx264", "-preset", "medium", "-crf", "24",
                    "-codec:a", "copy", str(compressed_path)
                ]
                    
                # Run synchronously (or thread/process it if you don't want to block)
                subprocess.run(compress_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    
                # Replace the giant original with the small compressed file
                input_path.unlink()  
                compressed_path.rename(input_path)  
                print(f"✅ Compression complete! File shrunk drastically.")


# =========================================================
# 🧠 POPUP FRAMEWORK (PLUGGABLE)
# =========================================================
class PopupHandler:
    def __init__(self, driver, framework):
        self.driver = driver
        self.framework = framework
        self._stop_flag = False
        self.thread = None

    # =====================================================
    # 🎯 DIRECT DISMISS (locator OR WebElement)
    # =====================================================
    def dismiss(self, target):
        try:
            # locator tuple -> resolve via stable_click
            if isinstance(target, tuple):
                self.framework.stable_click(target, timeout=5, scroll=False)

            # WebElement -> click directly via stable_click
            else:
                self.framework.stable_click(target, timeout=5, scroll=False)

            print("💥 Popup dismissed")
            return True

        except Exception as e:
            print(f"❌ Popup dismiss failed: {e}")
            return False

    def start_background_monitor(self):
        self._stop_flag = False
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()

    def stop_background_monitor(self):
        self._stop_flag = True
        if self.thread:
            self.thread.join(timeout=2)

    def _monitor_loop(self):
        while not self._stop_flag:
            try:
                # 1. Handle Shadow DOM Chat Widget (The persistent issue)
                chat_widgets = self.driver.find_elements(By.ID, "ujet-widget")
                for widget in chat_widgets:
                    try:
                        # Pierce the Shadow DOM
                        shadow_root = widget.shadow_root
                        # Look for common close/minimize selectors
                        close_btn = shadow_root.find_element(By.CSS_SELECTOR, ".icon-close")
                        if close_btn and close_btn.is_displayed():
                            self.driver.execute_script("arguments[0].click();", close_btn)
                            print("✅ Automatically closed chat widget (Shadow DOM).")
                    except Exception:
                        pass # Widget might not be fully loaded or isn't the one we need

                # 2. Handle Standard Modals/Popups
                popups = self.driver.find_elements(By.ID, "close-lightbox")
                for p in popups:
                    if p.is_displayed():
                        p.click()
                        print("✅ Closed standard lightbox.")

            except Exception as e:
                # Keep the thread alive even if a lookup fails
                pass
            
            time.sleep(2) # Poll every 2 seconds


# =========================================================
# ⚙️ CORE SELENIUM FRAMEWORK
# =========================================================

class SeleniumFramework:
    def __init__(self, driver):
        self.driver = driver

        self.wait = WebDriverWait(
            driver,
            timeout=15,
            poll_frequency=0.5,
            ignored_exceptions=[
                ElementClickInterceptedException,
                StaleElementReferenceException
            ],
        )
    
        self.recorder = ScreenRecorder()
        self.popup_handler = PopupHandler(self.driver, self)


    # -----------------------------------------------------
    # CLICK SYSTEM
    # -----------------------------------------------------
    def stable_click(self, locator_or_element, timeout=15, scroll=True):
        start = time.time()
        print(f"Clicking element at: {locator_or_element}")
        
        while True:
            try:
                # 1. Resolve Element
                if isinstance(locator_or_element, WebElement):
                    element = locator_or_element
                else:
                    element = self.wait.until(EC.element_to_be_clickable(locator_or_element))

                if scroll:
                    self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
                    time.sleep(2)
                
                self.flash_element(element)

                # Tiered Click Strategy
                try:
                    # Attempt 1: Native Click
                    element.click()
                    return
                except Exception as native_err:
                    # Attempt 2: ActionChains (Simulates user mouse movement)
                    try:
                        print(f"Native click failed, using ActionChains: {locator_or_element}")
                        ActionChains(self.driver).move_to_element(element).click().perform()
                        return
                    except Exception:
                        # Attempt 3: JavaScript Fallback (Executes immediately if Attempt 2 fails)
                        try:
                            print(f"ActionChains failed, forcing JS click: {locator_or_element}")
                            self.driver.execute_script("arguments[0].click();", element)
                            return
                        except Exception:
                            pass # Silently pass to let the while loop retry
            
            except Exception as e:
                if time.time() - start > timeout:
                    raise Exception(f"Action failed after {timeout}s: {e}")
                
                # Prevent CPU spiking while looping
                time.sleep(1)
    
    def wait_for_ready(self, timeout=15, stabilize_time=1.0, wait_for_modals=False):
        end_time = time.time() + timeout
        
        time.sleep(0.5)
        
        while time.time() < end_time:
            try:
                if wait_for_modals:
                    self.wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "modal-backdrop")))

                self.wait.until(EC.invisibility_of_element_located((By.ID, "brfLoadingIndicator")))
                self.wait.until(lambda d: d.execute_script("return document.readyState === 'complete'"))
                time.sleep(stabilize_time)
                
                loader = self.driver.find_elements(By.ID, "brfLoadingIndicator")
                if not loader or not loader[0].is_displayed():
                    return  
            
            except Exception:
                pass
                
        print(f"⚠️ Page stabilization timed out after {timeout} seconds.")


    def flash_element(self, element):
        """Creates a temporary visual ripple effect on the element being clicked."""
        try:
            # Injects CSS for a heartbeat pulse animation and applies it temporarily
            self.driver.execute_script("""
                var el = arguments[0];
                var originalOutline = el.style.outline;
                var originalTransition = el.style.transition;
                
                // Apply a distinct visual highlight
                el.style.transition = 'all 0.2s ease';
                el.style.outline = '4px solid #ef4444'; // Tailwind Red-500
                el.style.outlineOffset = '2px';
                
                // Revert it back after a brief moment
                setTimeout(function() {
                    el.style.outline = originalOutline;
                    el.style.transition = originalTransition;
                }, 400);
            """, element)
        except Exception:
            pass # Never let visual debugging break a test run

    # -----------------------------------------------------
    # RECORDING API
    # -----------------------------------------------------

    def start_recording(self, display_num: int, size: tuple, file_name: str):
        self.recorder.start(display_num, size, file_name)

    def stop_recording(self):
        self.recorder.stop()

        
def set_file_name(request, device_key: str, folder_name: str, has_upc: bool = False) -> str:
    test_file_name = Path(request.node.fspath).stem 

    sim_type_suffix = ""
    upc_suffix = ""
    
    if hasattr(request.node, "callspec"):
        params = request.node.callspec.params
        if "sim_type" in params:
            sim_type_suffix = f"_{params['sim_type']}"
            
    if has_upc:
        upc_suffix = "_UPC"
            
    device_suffix = f"_{device_key}"
    
    # Construct the file name
    file_name = f"{test_file_name}{device_suffix}{sim_type_suffix}{upc_suffix}({time.strftime('%m-%d')}).mp4"
    
    return str(Path(__file__).parent / folder_name / file_name)


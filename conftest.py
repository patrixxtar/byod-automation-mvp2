import pytest
from pathlib import Path
import time
from datetime import datetime
from utils.shared_utils import BrowserContext, SeleniumFramework, set_file_name
from configs.bell_config import DEVICE_PROFILES 


def pytest_addoption(parser):
    parser.addoption("--device", action="store", default="desktop", help="Device profile to use")
    parser.addoption("--upc", action="store", default="false", help="Run with UPC enabled/disabled")

def get_device_config(device_key):
    if device_key in ["mobile", "tablet"]:
        category_dict = DEVICE_PROFILES.get(device_key, {})
        if category_dict:
            first_device_name = list(category_dict.keys())[0]
            print(f"\n📱 Category '{device_key}' selected. Using: {first_device_name}")
            return category_dict[first_device_name]

    if device_key in DEVICE_PROFILES:
        print(f"\n✅ Device '{device_key}' selected.")
        return DEVICE_PROFILES[device_key]

    for category in ["mobile", "tablet"]:
        if device_key in DEVICE_PROFILES.get(category, {}):
            print(f"\n✅ Device '{device_key}' selected (found in {category}).")
            return DEVICE_PROFILES[category][device_key]


    print(f"\n⚠️ Device '{device_key}' not found. Falling back to default desktop.")
    return DEVICE_PROFILES.get("desktop")

@pytest.fixture
def has_upc(request):
    option = request.config.getoption("--upc")
    return str(option).lower() == "true"

@pytest.fixture(scope="function")
def automation_env(request, has_upc):
    device_key = request.config.getoption("--device")
    device = get_device_config(device_key)
    
    try:
        test_module_config = getattr(request.module, "CONFIG")
        target_url = test_module_config.get("target_url")
    except AttributeError:
        # Fallback if the test file forgot to import CONFIG
        raise Exception("The test file must import 'CONFIG' for the fixture to work.")

    display_size = device["display_size"]
    
    file_name = set_file_name(request, device_key, device.get("folder"), has_upc=has_upc)
    
    # Setup
    ctx = BrowserContext(
        display_size=display_size, 
        mobile_emulation=device.get("mobile_emulation"), 
        target_url=target_url, 
        )
    ctx.start()
    utils = SeleniumFramework(ctx.driver)

    request.node.driver = ctx.driver
    
    # Start Recording
    utils.start_recording(
        display_num=int(ctx.display.display),
        size=display_size,
        file_name=file_name
    )
    
    yield utils 
    
    # Teardown
    utils.stop_recording()
    ctx.stop()

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        driver = getattr(item, "driver", None)
        
        screenshot_dir = Path.cwd() / "failures"
        screenshot_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        file_base = f"{item.name}_{timestamp}"
        
        if driver:
            png_path = screenshot_dir / f"{file_base}.png"
            driver.save_screenshot(str(png_path))
            
        txt_path = screenshot_dir / f"{file_base}.txt"
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(report.longreprtext)
            
        print(f"\n📸 Failure detected! Screenshot & Traceback saved to: {screenshot_dir}")
        session_timestamp = datetime.now().strftime("%Y-%m-%d")
        consolidated_log_path = screenshot_dir / f"failures_summary_{session_timestamp}.log"
        
        test_name = item.name
        class_name = item.cls.__name__ if item.cls else item.module.__name__
        message = str(report.longrepr.reprcrash.message) if hasattr(report.longrepr, 'reprcrash') else "No message provided."
        details = report.longreprtext or "No traceback available."

        log_entry = (
            f"Test: {class_name}::{test_name} [FAILURE]\n"
            f"Message: {message}\n"
            f"Details:\n{details.strip()}\n"
            f"{'-'*60}\n"
        )

        with open(consolidated_log_path, "a", encoding="utf-8") as log_file:
            if consolidated_log_path.stat().st_size == 0:
                log_file.write(f"=== PYTEST FAILURES LOG ({session_timestamp}) ===\n\n")
            log_file.write(log_entry)
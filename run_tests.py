import subprocess
import sys
import os
import xml.etree.ElementTree as ET
from datetime import datetime 

def run_tests():
    print("=== Test Automation Runner ===")
    
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    valid_brands = ["bell", "virgin"]
    while True:
        brand = input("Which brand (bell/virgin)? ").strip().lower()
        if brand in valid_brands:
            break
        print(f"❌ Invalid brand! Please choose either: {', '.join(valid_brands)}")

    valid_devices = ["desktop", "mobile", "tablet", "galaxy_s24_fe", "iphone_15_pro_max", "tablet_mobile_ui", "tablet_desktop_ui"]
    while True:
        device = input(f"Which device ({', '.join(valid_devices)})? ").strip().lower()
        if device in valid_devices:
            break
        print(f"❌ Invalid device! Please choose from: {', '.join(valid_devices)}")

    if brand == "bell":
        valid_upc = ["true", "false"]
        while True:
            upc_choice = input("Do you want UPC enabled? (true/false): ").strip().lower()
            if upc_choice in valid_upc:
                break
            print("❌ Invalid choice! Please enter 'true' or 'false'.")
    else:
        upc_choice = "false"

    test_file = os.path.join("tests", f"test_{brand}_byod.py")
    
    os.chdir(project_root)
    
    xml_report = os.path.join(project_root, "temp_results.xml")
    
    cmd = [
        sys.executable, "-m", "pytest", 
        test_file, 
        "--device", device, 
        "--upc", upc_choice,
        "-s", "-v",
        f"--junitxml={xml_report}"
    ]

    print(f"\n🚀 Executing: {' '.join(cmd)}\n")
    print(f"📁 Running from: {os.getcwd()}")
    
    try:
        subprocess.run(cmd, check=True)
        print("\n✅ All tests passed!")
    except subprocess.CalledProcessError:
        print("\n❌ Test execution encountered failures.")
    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {e}")
    finally:
        if os.path.exists(xml_report):
            logs_dir = os.path.join(project_root, "logs")
            generate_failure_log(xml_report, output_dir=logs_dir)
            os.remove(xml_report)

def generate_failure_log(xml_path, output_dir="logs"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    log_path = os.path.join(output_dir, f"failures_{timestamp}.log")
    
    failures = []
    
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        
        for testcase in root.iter('testcase'):
            test_name = testcase.get('name', 'Unknown Test')
            class_name = testcase.get('classname', '')
            
            for issue in testcase.findall('failure') + testcase.findall('error'):
                issue_type = issue.tag.upper() 
                message = issue.get('message', 'No message provided.')
                details = issue.text or 'No traceback available.'
                
                failures.append(
                    f"Test: {class_name}::{test_name} [{issue_type}]\n"
                    f"Message: {message}\n"
                    f"Details:\n{details.strip()}\n"
                    f"{'-'*60}\n"
                )
        
        if failures:
            with open(log_path, "w", encoding="utf-8") as f:
                f.write(f"=== PYTEST FAILURES LOG ({timestamp}) ===\n\n")
                f.writelines(failures)
            print(f"📄 New unique log created: {log_path}")
        else:
            print("✅ No failures found. No log file created.")
                
    except Exception as e:
        print(f"⚠️ Could not parse the test report: {e}")

if __name__ == "__main__":
    run_tests()
from utils.gmail_api_util import get_oauth_gmail_service

print("🚀 Starting Headless Gmail OAuth setup...")
try:
    service = get_oauth_gmail_service()
    print("✅ Success! Your token.json has been generated in the utils/ folder.")
except Exception as e:
    print(f"❌ Authentication failed: {e}")

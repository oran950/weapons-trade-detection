#!/usr/bin/env python3
"""
Telegram Authentication Script
Run this once to authenticate with Telegram and create a session file.
After authentication, the session file will be used for subsequent API calls.
"""
import os
import sys
import asyncio
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


async def authenticate():
    """Authenticate with Telegram and create session file"""
    
    # Get credentials from environment
    api_id = os.getenv('TELEGRAM_API_ID')
    api_hash = os.getenv('TELEGRAM_API_HASH')
    session_name = os.getenv('TELEGRAM_SESSION_NAME', 'weapons_detection_session')
    
    if not api_id or not api_hash:
        print("=" * 60)
        print("TELEGRAM API CREDENTIALS NOT FOUND")
        print("=" * 60)
        print("\nTo get your credentials:")
        print("1. Go to https://my.telegram.org")
        print("2. Log in with your phone number")
        print("3. Click 'API development tools'")
        print("4. Create a new application (any name/description)")
        print("5. Copy the API ID and API Hash")
        print("\nThen add to your .env file:")
        print("TELEGRAM_API_ID=your_api_id")
        print("TELEGRAM_API_HASH=your_api_hash")
        print("=" * 60)
        
        # Ask for manual input
        print("\nOr enter them now:")
        api_id = input("API ID: ").strip()
        api_hash = input("API Hash: ").strip()
        
        if not api_id or not api_hash:
            print("Credentials required. Exiting.")
            return False
    
    try:
        from telethon import TelegramClient
        from telethon.errors import SessionPasswordNeededError
        
        print(f"\nConnecting to Telegram...")
        print(f"Session name: {session_name}")
        
        # Create client
        client = TelegramClient(session_name, int(api_id), api_hash)
        
        # Connect and authenticate
        await client.connect()
        
        if not await client.is_user_authorized():
            print("\nYou need to authenticate with your phone number.")
            phone = input("Enter your phone number (with country code, e.g., +1234567890): ").strip()
            
            await client.send_code_request(phone)
            code = input("Enter the code you received: ").strip()
            
            try:
                await client.sign_in(phone, code)
            except SessionPasswordNeededError:
                password = input("Two-factor authentication enabled. Enter your password: ").strip()
                await client.sign_in(password=password)
        
        # Get user info
        me = await client.get_me()
        print(f"\n✓ Successfully authenticated as: {me.first_name} (@{me.username})")
        print(f"✓ Session file created: {session_name}.session")
        
        # Test by listing some dialogs
        print("\nTesting connection by listing your recent chats:")
        async for dialog in client.iter_dialogs(limit=5):
            print(f"  - {dialog.name}")
        
        print("\n" + "=" * 60)
        print("AUTHENTICATION SUCCESSFUL!")
        print("=" * 60)
        print("\nYou can now use Telegram collection in the dashboard.")
        print("The session file will be reused for future connections.")
        
        await client.disconnect()
        return True
        
    except ImportError:
        print("Telethon not installed. Run: pip install telethon")
        return False
    except Exception as e:
        print(f"Authentication failed: {e}")
        return False


async def test_channel_access(channel_username: str = "telegram"):
    """Test access to a public channel"""
    
    api_id = os.getenv('TELEGRAM_API_ID')
    api_hash = os.getenv('TELEGRAM_API_HASH')
    session_name = os.getenv('TELEGRAM_SESSION_NAME', 'weapons_detection_session')
    
    if not api_id or not api_hash:
        print("API credentials not configured. Run authentication first.")
        return
    
    try:
        from telethon import TelegramClient
        
        client = TelegramClient(session_name, int(api_id), api_hash)
        await client.connect()
        
        if not await client.is_user_authorized():
            print("Not authorized. Run authentication first.")
            await client.disconnect()
            return
        
        print(f"\nTesting access to @{channel_username}...")
        
        # Get channel
        channel = await client.get_entity(channel_username)
        print(f"✓ Channel found: {channel.title}")
        
        # Get recent messages
        print(f"\nRecent messages from @{channel_username}:")
        count = 0
        async for message in client.iter_messages(channel, limit=5):
            if message.text:
                preview = message.text[:100] + "..." if len(message.text) > 100 else message.text
                print(f"  [{message.date.strftime('%Y-%m-%d %H:%M')}] {preview}")
                count += 1
        
        print(f"\n✓ Successfully retrieved {count} messages")
        await client.disconnect()
        
    except Exception as e:
        print(f"Error accessing channel: {e}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Telegram Authentication")
    parser.add_argument("--test", type=str, help="Test access to a channel (e.g., --test warmonitors)")
    args = parser.parse_args()
    
    if args.test:
        asyncio.run(test_channel_access(args.test))
    else:
        asyncio.run(authenticate())


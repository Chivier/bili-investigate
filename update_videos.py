#!/usr/bin/env python3
import json
import os
import sys
from bili_spider.updater import update_all_users

if __name__ == '__main__':
    if os.path.exists('data/following.json'):
        with open('data/following.json', 'r', encoding='utf-8') as f:
            following_users = json.load(f)
        
        if following_users:
            print("Starting video update for all following users...")
            update_all_users(following_users)
            print("Update completed!")
        else:
            print("No users in following list.")
    else:
        print("No following.json file found. Please add users through the web interface first.")

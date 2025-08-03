import os
import pandas as pd
from datetime import datetime
import json
from .spider import make_chrome_browser, get_user_videos


def update_user_videos(user_id, user_name, chromedriver_path=None, progress_callback=None):
    csv_file = f"data/{user_id}.csv"
    existing_bvids = set()
    
    if os.path.exists(csv_file):
        df_existing = pd.read_csv(csv_file)
        existing_bvids = set(df_existing['bvid'].tolist())
        print(f"Found {len(existing_bvids)} existing videos for {user_name}")
    
    new_videos = []
    duplicate_count = 0
    consecutive_duplicates = 0
    
    with make_chrome_browser(executable_path=chromedriver_path, headless=True) as browser:
        # Don't limit pages - get all videos
        for video_data in get_user_videos(browser, int(user_id), progress_callback=progress_callback):
            url, bvid, _, title, play_count, pub_date, duration = video_data
            
            if bvid in existing_bvids:
                duplicate_count += 1
                consecutive_duplicates += 1
                
                if consecutive_duplicates >= 10:
                    print(f"Found 10 consecutive duplicates, stopping early")
                    break
            else:
                consecutive_duplicates = 0
                new_videos.append({
                    'url': url,
                    'bvid': bvid,
                    'user_name': user_name,
                    'title': title,
                    'play_count': play_count,
                    'pub_date': pub_date,
                    'duration': duration,
                    'fetched_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
    
    if new_videos:
        df_new = pd.DataFrame(new_videos)
        
        if os.path.exists(csv_file):
            df_existing = pd.read_csv(csv_file)
            df_combined = pd.concat([df_new, df_existing], ignore_index=True)
            
            df_combined = df_combined.drop_duplicates(subset=['bvid'], keep='first')
        else:
            df_combined = df_new
        
        df_combined.to_csv(csv_file, index=False, encoding='utf-8')
        print(f"Added {len(new_videos)} new videos for {user_name}")
    else:
        print(f"No new videos found for {user_name}")
    
    return len(new_videos)


def update_all_users(following_users, chromedriver_path=None):
    for user_id, user_info in following_users.items():
        print(f"\nUpdating videos for {user_info['name']} (ID: {user_id})")
        try:
            new_count = update_user_videos(user_id, user_info['name'], chromedriver_path)
            
            user_info['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            with open('data/following.json', 'w', encoding='utf-8') as f:
                json.dump(following_users, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"Error updating {user_info['name']}: {e}")
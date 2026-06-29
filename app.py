import streamlit as st
import pandas as pd
import os
from datetime import datetime
import json
import time

st.set_page_config(
    page_title="Bilibili Video Tracker",
    page_icon="📺",
    layout="wide"
)

if 'following_users' not in st.session_state:
    if os.path.exists('data/following.json'):
        with open('data/following.json', 'r', encoding='utf-8') as f:
            st.session_state.following_users = json.load(f)
    else:
        st.session_state.following_users = {}

def save_following():
    os.makedirs('data', exist_ok=True)
    with open('data/following.json', 'w', encoding='utf-8') as f:
        json.dump(st.session_state.following_users, f, ensure_ascii=False, indent=2)

page = st.sidebar.selectbox("选择页面", ["关注列表", "视频浏览"])

if page == "关注列表":
    st.title("🌟 我的关注列表")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader("添加新用户")
        with st.form("add_user"):
            new_user_id = st.text_input("用户ID (mid)", placeholder="例如: 927587 或 700380991")
            submitted = st.form_submit_button("添加")
            
            if submitted:
                if new_user_id:
                    if new_user_id not in st.session_state.following_users:
                        with st.spinner(f"正在获取用户 {new_user_id} 的信息..."):
                            from bili_spider.spider import get_user_nickname
                            # Try to get chromedriver path
                            chromedriver_path = "./chromedriver" if os.path.exists("./chromedriver") else None
                            nickname = get_user_nickname(int(new_user_id), executable_path=chromedriver_path)
                        
                        st.session_state.following_users[new_user_id] = {
                            "name": nickname,
                            "added_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "last_updated": None
                        }
                        save_following()
                        st.success(f"已添加用户: {nickname} (ID: {new_user_id})")
                        st.rerun()
                    else:
                        st.warning("该用户已在关注列表中")
                else:
                    st.error("请输入用户ID")
    
    st.divider()
    
    st.subheader("📋 当前关注列表")

    # Initialize session state for tracking update
    if 'updating_user' not in st.session_state:
        st.session_state.updating_user = None

    if st.session_state.following_users:
        # Create table header
        header_cols = st.columns([2, 3, 2, 2, 1, 1])
        with header_cols[0]:
            st.markdown("**用户ID**")
        with header_cols[1]:
            st.markdown("**昵称**")
        with header_cols[2]:
            st.markdown("**视频数**")
        with header_cols[3]:
            st.markdown("**最后更新**")
        with header_cols[4]:
            st.markdown("**操作**")

        st.divider()

        # Display user rows
        for user_id, user_info in st.session_state.following_users.items():
            col1, col2, col3, col4, col5, col6 = st.columns([2, 3, 2, 2, 1, 1])

            with col1:
                st.text(f"{user_id}")

            with col2:
                st.text(f"{user_info['name']}")

            with col3:
                csv_file = f"data/{user_id}.csv"
                if os.path.exists(csv_file):
                    df = pd.read_csv(csv_file)
                    st.text(f"{len(df)}")
                else:
                    st.text("未同步")

            with col4:
                if user_info.get('last_updated'):
                    st.text(f"{user_info['last_updated'][:10]}")
                else:
                    st.text("从未")

            with col5:
                if st.button("🔄", key=f"update_{user_id}", help="更新该用户"):
                    st.session_state.updating_user = user_id

            with col6:
                if st.button("🗑", key=f"del_{user_id}", help="删除该用户"):
                    del st.session_state.following_users[user_id]
                    save_following()
                    if os.path.exists(f"data/{user_id}.csv"):
                        os.remove(f"data/{user_id}.csv")
                    st.rerun()

        # Update status area below the table
        if st.session_state.updating_user:
            st.divider()
            user_id = st.session_state.updating_user
            user_info = st.session_state.following_users[user_id]

            # Create a container for update status
            status_container = st.container()
            with status_container:
                st.info(f"🔄 正在更新: {user_info['name']} (ID: {user_id})")
                progress_bar = st.progress(0)
                status_text = st.empty()

                from bili_spider.updater import update_user_videos
                chromedriver_path = "./chromedriver" if os.path.exists("./chromedriver") else None

                def progress_callback(current_page, total_pages, message):
                    progress = current_page / total_pages if total_pages > 0 else 0
                    progress_bar.progress(progress)
                    status_text.text(f"{message}")

                try:
                    new_count = update_user_videos(
                        user_id,
                        user_info['name'],
                        chromedriver_path=chromedriver_path,
                        progress_callback=progress_callback
                    )
                    user_info['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    save_following()
                    st.success(f"✅ {user_info['name']} 更新完成，新增 {new_count} 个视频")
                    st.session_state.updating_user = None
                    time.sleep(2)
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ 更新失败: {str(e)}")
                    st.session_state.updating_user = None
                    time.sleep(3)
                    st.rerun()
    else:
        st.info("还没有关注任何用户，请在上方添加")
    
    st.divider()

    # Initialize session state for batch update
    if 'updating_all' not in st.session_state:
        st.session_state.updating_all = False

    if st.button("🔄 更新所有用户视频", type="primary", disabled=st.session_state.updating_all or bool(st.session_state.get('updating_user'))):
        st.session_state.updating_all = True
        st.rerun()

    # Batch update progress area
    if st.session_state.updating_all:
        st.divider()

        # Create a clean progress display area
        with st.container():
            st.markdown("### 📊 批量更新进度")

            from bili_spider.updater import update_user_videos
            total_users = len(st.session_state.following_users)
            chromedriver_path = "./chromedriver" if os.path.exists("./chromedriver") else None

            # Overall progress
            overall_progress = st.progress(0)
            overall_status = st.empty()

            # Current user progress
            with st.expander("当前用户进度", expanded=True):
                current_user_info = st.empty()
                user_progress = st.progress(0)
                user_status = st.empty()

            # Results summary
            results_container = st.container()
            success_count = 0
            failed_users = []

            for idx, (user_id, user_info) in enumerate(st.session_state.following_users.items()):
                # Update overall progress
                overall_progress.progress((idx) / total_users)
                overall_status.text(f"总进度: {idx + 1}/{total_users} 用户")
                current_user_info.info(f"🔄 正在更新: {user_info['name']} (ID: {user_id})")

                def progress_callback(current_page, total_pages, message):
                    progress = current_page / total_pages if total_pages > 0 else 0
                    user_progress.progress(progress)
                    user_status.text(f"{message}")

                try:
                    new_count = update_user_videos(
                        user_id,
                        user_info['name'],
                        chromedriver_path=chromedriver_path,
                        progress_callback=progress_callback
                    )

                    user_info['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    save_following()

                    with results_container:
                        st.success(f"✅ {user_info['name']}: 新增 {new_count} 个视频")
                    success_count += 1

                except Exception as e:
                    with results_container:
                        st.error(f"❌ {user_info['name']}: {str(e)}")
                    failed_users.append(user_info['name'])

                # Reset current user progress
                user_progress.progress(0)
                user_status.text("")

            # Final summary
            overall_progress.progress(1.0)
            overall_status.text(f"✅ 更新完成！成功: {success_count}/{total_users}")

            if failed_users:
                st.warning(f"以下用户更新失败: {', '.join(failed_users)}")

            st.session_state.updating_all = False
            time.sleep(3)
            st.rerun()

else:
    st.title("📺 视频浏览")
    
    if not st.session_state.following_users:
        st.warning("请先在关注列表页面添加用户")
    else:
        selected_user_id = st.selectbox(
            "选择用户",
            options=list(st.session_state.following_users.keys()),
            format_func=lambda x: f"{st.session_state.following_users[x]['name']} (ID: {x})"
        )
        
        if selected_user_id:
            user_info = st.session_state.following_users[selected_user_id]
            st.subheader(f"🎬 {user_info['name']} 的视频列表")
            
            csv_file = f"data/{selected_user_id}.csv"
            
            if os.path.exists(csv_file):
                df = pd.read_csv(csv_file)
                
                col1, col2, col3 = st.columns([1, 1, 1])
                with col1:
                    st.metric("视频总数", len(df))
                with col2:
                    if 'pub_date' in df.columns:
                        try:
                            # Parse dates with current year for MM-DD format
                            current_year = datetime.now().year
                            df['pub_date_parsed'] = df['pub_date'].apply(lambda x: 
                                pd.to_datetime(f"{current_year}-{x}" if '-' in str(x) and len(str(x).split('-')[0]) <= 2 else x, errors='coerce')
                            )
                            valid_dates = df['pub_date_parsed'].dropna()
                            if len(valid_dates) > 0:
                                latest_date = valid_dates.max()
                                # If the date is in the future (due to MM-DD assumption), use previous year
                                if latest_date > datetime.now():
                                    latest_date = latest_date.replace(year=current_year - 1)
                                st.metric("最新视频", latest_date.strftime("%Y-%m-%d"))
                            else:
                                st.metric("最新视频", "暂无数据")
                        except Exception as e:
                            st.metric("最新视频", "日期解析失败")
                with col3:
                    if user_info.get('last_updated'):
                        st.metric("上次更新", user_info['last_updated'][:10])
                
                st.divider()
                
                search_term = st.text_input("🔍 搜索视频标题", placeholder="输入关键词...")
                
                filtered_df = df.copy()
                if search_term:
                    filtered_df = filtered_df[filtered_df['title'].str.contains(search_term, case=False, na=False)]
                
                sort_by = st.selectbox("排序方式", ["发布时间(新到旧)", "发布时间(旧到新)", "播放量(高到低)", "播放量(低到高)"])
                
                if sort_by == "发布时间(新到旧)":
                    # Parse dates with current year for MM-DD format
                    current_year = datetime.now().year
                    filtered_df['pub_date_parsed'] = filtered_df['pub_date'].apply(lambda x: 
                        pd.to_datetime(f"{current_year}-{x}" if '-' in str(x) and len(str(x).split('-')[0]) <= 2 else x, errors='coerce')
                    )
                    filtered_df = filtered_df.sort_values('pub_date_parsed', ascending=False)
                elif sort_by == "发布时间(旧到新)":
                    # Parse dates with current year for MM-DD format
                    current_year = datetime.now().year
                    filtered_df['pub_date_parsed'] = filtered_df['pub_date'].apply(lambda x: 
                        pd.to_datetime(f"{current_year}-{x}" if '-' in str(x) and len(str(x).split('-')[0]) <= 2 else x, errors='coerce')
                    )
                    filtered_df = filtered_df.sort_values('pub_date_parsed', ascending=True)
                elif sort_by == "播放量(高到低)":
                    def parse_play_count(x):
                        x_str = str(x)
                        if '充电专属' in x_str or '专属' in x_str:
                            return 0  # Special content, treat as 0
                        try:
                            if '万' in x_str:
                                return float(x_str.replace('万', '').replace('-', '0')) * 10000
                            else:
                                return float(x_str.replace('-', '0'))
                        except:
                            return 0  # If parsing fails, treat as 0
                    
                    filtered_df['play_count_num'] = filtered_df['play_count'].apply(parse_play_count)
                    filtered_df = filtered_df.sort_values('play_count_num', ascending=False)
                elif sort_by == "播放量(低到高)":
                    def parse_play_count(x):
                        x_str = str(x)
                        if '充电专属' in x_str or '专属' in x_str:
                            return 0  # Special content, treat as 0
                        try:
                            if '万' in x_str:
                                return float(x_str.replace('万', '').replace('-', '0')) * 10000
                            else:
                                return float(x_str.replace('-', '0'))
                        except:
                            return 0  # If parsing fails, treat as 0
                    
                    filtered_df['play_count_num'] = filtered_df['play_count'].apply(parse_play_count)
                    filtered_df = filtered_df.sort_values('play_count_num', ascending=True)
                
                st.divider()
                
                if len(filtered_df) > 0:
                    st.text(f"找到 {len(filtered_df)} 个视频")
                    
                    for idx, row in filtered_df.iterrows():
                        with st.container():
                            col1, col2, col3, col4 = st.columns([5, 2, 2, 1])
                            
                            with col1:
                                st.markdown(f"**[{row['title']}]({row['url']})**")
                            
                            with col2:
                                st.text(f"播放: {row['play_count']}")
                            
                            with col3:
                                st.text(f"时长: {row['duration']}")
                            
                            with col4:
                                st.text(row['pub_date'])
                            
                            st.divider()
                else:
                    st.info("没有找到匹配的视频")
                
            else:
                st.warning(f"用户 {user_info['name']} 的视频数据尚未同步")
                if st.button("立即同步该用户"):
                    from bili_spider.updater import update_user_videos
                    with st.spinner("正在获取视频数据..."):
                        update_user_videos(selected_user_id, user_info['name'])
                        user_info['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        save_following()
                    st.success("同步完成！")
                    st.rerun()
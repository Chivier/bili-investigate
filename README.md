# Bilibili Video Tracker / B站视频追踪器

[English](#english) | [中文](#中文)

## English

A Streamlit-based web application for tracking Bilibili content creators' video updates with smart incremental fetching.

### ✨ Features

- 📋 **Following Management**: Add and manage your favorite content creators
- 📺 **Video Browser**: View all videos from followed creators
- 🔄 **Smart Updates**: Only fetch new videos, avoiding duplicate crawling
- 🔍 **Search & Sort**: Search videos by title, sort by date or view count
- 🐳 **Docker Support**: Easy deployment with Docker
- 🌍 **Cross-Platform**: Works on macOS and Linux

### 🚀 Quick Start

#### Easiest Way

Use the auto-start script (auto-detects environment):
```bash
./start.sh
```

#### Local Installation (macOS/Linux)

1. Install dependencies:
```bash
./install.sh
```

2. Run the application:
```bash
./run.sh
```

#### Docker Deployment

##### Quick Version (Recommended)
Uses slim Docker config for faster builds:
```bash
docker-compose -f docker-compose.slim.yml up -d
```

##### Full Version
Multi-architecture support:
```bash
docker-compose up -d
```

Access the application at http://localhost:8501

### 📖 Usage

1. **Add Users**: Go to "Following List" page, enter user ID (mid) and nickname
2. **Update Videos**: Click "Update All Users' Videos" to fetch latest videos
3. **Browse Videos**: Go to "Video Browser" page to view and search videos

### 🛠 ChromeDriver Setup

If you encounter ChromeDriver issues when running locally:
```bash
./setup_chromedriver.sh
```

This script automatically downloads the ChromeDriver matching your Chrome version.

### 📁 Data Storage

- User following list: `data/following.json`
- Video data: `data/{user_id}.csv`

### 🔧 Command Line Update

Update videos via command line:
```bash
source venv/bin/activate
python update_videos.py
```

### 📋 Requirements

- Python 3.7+
- Google Chrome or Chromium
- ChromeDriver (auto-downloaded by setup script)

---

## 中文

一个基于 Streamlit 的 Web 应用，用于追踪 B站 UP主的视频更新，支持智能增量获取。

### ✨ 功能特性

- 📋 **关注列表管理**：添加和管理你喜欢的UP主
- 📺 **视频浏览器**：查看关注UP主的所有视频
- 🔄 **智能更新**：只获取新视频，避免重复爬取
- 🔍 **搜索排序**：按标题搜索，按时间或播放量排序
- 🐳 **Docker 支持**：使用 Docker 轻松部署
- 🌍 **跨平台**：支持 macOS 和 Linux

### 🚀 快速开始

#### 最简单的方式

使用自动启动脚本（自动检测环境）：
```bash
./start.sh
```

#### 本地安装（macOS/Linux）

1. 安装依赖：
```bash
./install.sh
```

2. 运行应用：
```bash
./run.sh
```

#### Docker 部署

##### 快速版本（推荐）
使用精简版 Docker 配置，构建速度更快：
```bash
docker-compose -f docker-compose.slim.yml up -d
```

##### 完整版本
支持多架构的完整版本：
```bash
docker-compose up -d
```

访问应用：http://localhost:8501

### 📖 使用说明

1. **添加用户**：在"关注列表"页面输入UP主的用户ID（mid）和昵称
2. **更新视频**：点击"更新所有用户视频"获取最新视频
3. **浏览视频**：在"视频浏览"页面查看和搜索视频

### 🛠 ChromeDriver 设置

如果在本地运行时遇到 ChromeDriver 问题：
```bash
./setup_chromedriver.sh
```

该脚本会自动下载与您的 Chrome 版本匹配的 ChromeDriver。

### 📁 数据存储

- 用户关注列表：`data/following.json`
- 视频数据：`data/{user_id}.csv`

### 🔧 命令行更新

通过命令行更新视频：
```bash
source venv/bin/activate
python update_videos.py
```

### 📋 系统要求

- Python 3.7+
- Google Chrome 或 Chromium
- ChromeDriver（安装脚本会自动下载）

### 🔄 更新策略

- 首次获取用户视频时会爬取最多5页
- 后续更新只获取新视频
- 遇到连续10个重复视频时自动停止
- 建议合理设置更新频率，避免频繁请求

### 🐳 Docker 镜像说明

提供两个 Docker 镜像版本：

1. **精简版** (`Dockerfile.slim`)：
   - 只安装 Chromium，构建速度快
   - 适合大多数使用场景
   - 镜像体积更小

2. **完整版** (`Dockerfile`)：
   - 自动检测架构（x86_64/ARM64）
   - x86_64 使用 Google Chrome
   - ARM64 使用 Chromium
   - 适合需要最大兼容性的场景

### 📝 项目结构

```
bili-investigate/
├── app.py                    # Streamlit 主应用
├── bili_spider/             # 爬虫模块
│   ├── spider.py           # 核心爬虫逻辑
│   └── updater.py          # 智能更新逻辑
├── data/                    # 数据存储目录
├── requirements.txt         # Python 依赖
├── install.sh              # 安装脚本
├── start.sh                # 智能启动脚本
├── setup_chromedriver.sh   # ChromeDriver 设置
├── Dockerfile              # 完整版 Docker 镜像
├── Dockerfile.slim         # 精简版 Docker 镜像
├── docker-compose.yml      # Docker Compose 配置
└── docker-compose.slim.yml # 精简版 Docker Compose

```

### ⚠️ 注意事项

- 请遵守 Bilibili 的使用条款
- 避免过于频繁的请求
- 本项目仅供学习和个人使用
- 不要用于商业目的

### 🤝 贡献

欢迎提交 Issue 和 Pull Request！

### 📄 许可证

MIT License
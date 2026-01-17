# 📈 NSE MTF Update Bot

An automated Python bot that fetches Margin Trading Funding (MTF) data from the NSE website, generates a visual dashboard, and posts insights to Twitter (X) daily.

FEATURES
Automated: Runs automatically every morning at 8:56 AM IST via GitHub Actions
Visualizer: Creates a professional dark-mode dashboard image using matplotlib
Smart Fetching: Automatically retries and fetches the latest available MTF data from NSE archives
Twitter Integration: Posts the dashboard image along with key MTF statistics directly to X (Twitter)

SETUP & USAGE

Prerequisites
Python 3.10+
A Twitter (X) Developer Account with API access

Installation
git clone https://github.com/babu-mani/mtf-update-actions.git
cd mtf-update-actions
pip install -r requirements.txt

GitHub Secrets
Add the following Repository Secrets in GitHub settings

TWITTER_API_KEY
TWITTER_API_SECRET
TWITTER_ACCESS_TOKEN
TWITTER_ACCESS_TOKEN_SECRET

TECH STACK
Python (Pandas, Matplotlib, Requests)
Tweepy (Twitter API)
GitHub Actions (Cron Scheduling)

DISCLAIMER
This project is for informational and educational purposes only.
It does not constitute financial advice.

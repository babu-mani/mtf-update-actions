# 📈 NSE MTF Update Bot

An automated Python bot that fetches Margin Trading Funding (MTF) data from the NSE website, generates a visual dashboard, and posts insights to Twitter (X) daily.

FEATURES
1. Automated execution via GitHub Actions every morning at 8:56 AM IST
2. Dark-mode professional dashboard generated using matplotlib
3. Automatic retry logic to fetch the latest available NSE MTF data
4. Posts dashboard image and key MTF statistics to Twitter (X)

SETUP & USAGE

PREREQUISITES
1. Python 3.10 or higher
2. Twitter (X) Developer account with API access

INSTALLATION
git clone https://github.com/babu-mani/mtf-update-actions.git
cd mtf-update-actions
pip install -r requirements.txt

GITHUB SECRETS
Add the following repository secrets in GitHub settings

1. TWITTER_API_KEY
2. TWITTER_API_SECRET
3. TWITTER_ACCESS_TOKEN
4. TWITTER_ACCESS_TOKEN_SECRET

TECH STACK
1. Python (Pandas, Matplotlib, Requests)
2. Tweepy (Twitter API)
3. GitHub Actions (Cron scheduling)

DISCLAIMER
This project is for informational and educational purposes only.
It does not constitute financial advice.

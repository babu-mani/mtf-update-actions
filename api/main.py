name: Daily NSE MTF Tweet

on:
  schedule:
    # 03:26 UTC = 8:56 AM IST
    - cron: '26 3 * * *'
  workflow_dispatch:

jobs:
  run-script:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'

      - name: Install dependencies
        # This will look for requirements.txt in the root folder (matches your image)
        run: |
          pip install -r requirements.txt

      - name: Run Script
        env:
          TWITTER_API_KEY: ${{ secrets.TWITTER_API_KEY }}
          TWITTER_API_SECRET: ${{ secrets.TWITTER_API_SECRET }}
          TWITTER_ACCESS_TOKEN: ${{ secrets.TWITTER_ACCESS_TOKEN }}
          TWITTER_ACCESS_SECRET: ${{ secrets.TWITTER_ACCESS_SECRET }}
        # Go into api folder (where fonts and main.py are) and run
        run: |
          cd api
          python main.py

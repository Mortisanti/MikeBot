import requests
import json
from datetime import datetime, timedelta

# https://www.epicgames.com/store/en-US/free-games

url = 'https://store-site-backend-static-ipv4.ak.epicgames.com/freeGamesPromotions?locale=en-US&country=US&allowCountries=US'
headers = { 'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:94.0) Gecko/20100101 Firefox/94.0' }
r = requests.get(url, headers=headers)
with open('egpromos.json', 'w') as f:
    f.write(r.text)

with open('egpromos.json', 'r') as f:
    data = json.loads(f.read())
# Shortcut to store products (list)    
elements = data['data']['Catalog']['searchStore']['elements']

print(f"Total elements: {len(elements)}")
# Iterate through promotions checking for promotionalOffers or upcomingPromotionalOffers
for i in elements:
    # Title
    title = i['title']
    # description = i['description']
    mappings = i['catalogNs']['mappings']
    try:
        # Get page slug and build URL (not always 100% accurate because of different game editions - thanks EG)
        # page_slug = mappings[0]['pageSlug']
        # print(f"https://www.epicgames.com/store/en-US/p/{page_slug}")
        product_slug = i['productSlug'].replace('/home', '')
        if product_slug != '[]':
            print(f"https://www.epicgames.com/store/en-US/p/{product_slug}")            
        # Check promotions
        if i['promotions'] is not None:
            promotions = i['promotions']
            if len(promotions['promotionalOffers']) > 0:
                # Active promotion
                promotional_offers = promotions['promotionalOffers'][0]['promotionalOffers'][0]
                start_date = promotional_offers['startDate']
                end_date = promotional_offers['endDate']
                discount = promotional_offers['discountSetting']['discountPercentage']
                if discount == 0:
                    print(title)
                    print(start_date)
                    print(end_date)
                    # print(f"Active Promotion: {promotional_offers}\n")
            # else:
            #     # Upcoming promotion
            #     upcoming_promotional_offers = promotions['upcomingPromotionalOffers']
            #     print(title)
            #     print(f"Upcoming Promotion: {upcoming_promotional_offers}\n")
    except IndexError:
        print("Unknown game detected:")
        print(f"Title: {title}")
        # print(f"Description: {description}")

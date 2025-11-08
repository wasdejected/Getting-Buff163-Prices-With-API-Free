"""
cs2_buff_price_fetcher.py

Fetches marketplace IDs JSON from GitHub and queries buy/sell orders for exact variants.
Handles Phases, Ruby, Sapphire, Emerald, Black Pearl.
Prints highest buy and lowest sell prices in USD, rounded to two decimals.
Also prints the generated buy/sell URLs (page 1) with applied tag IDs for browser verification.
Compatible with Python 3.6–3.9.
"""

import requests
import time
import json
import re
import sys
from difflib import get_close_matches
from typing import Optional

GITHUB_URL = "https://raw.githubusercontent.com/ModestSerhat/cs2-marketplace-ids/refs/heads/main/cs2_marketplaceids.json"
HEADERS = {"User-Agent": "cs2-price-fetcher/1.0", "Accept": "application/json, text/javascript, */*; q=0.01"}
TIMEOUT = 15
CNY_TO_USD = 0.14

# Special finishes and phase tags
SPECIAL_TAGS = {
    'ruby': 3435175,
    'sapphire': 3549384,
    'emerald': 447129,
    'black pearl': 6009966,
    'phase1': 446972,
    'phase2': 446974,
    'phase3': 446975,
    'phase4': 446973
}

def fetch_marketplace_ids():
    resp = requests.get(GITHUB_URL, headers={"User-Agent": "cs2-price-fetcher"}, timeout=TIMEOUT)
    resp.raise_for_status()
    full_data = json.loads(resp.text)
    return full_data.get('items', full_data)

def normalize_name(name: str) -> str:
    n = name.replace('★', '').strip()
    n = re.sub(r"\s+", " ", n)
    return n.lower()

def find_variant_goods_id(item_name: str, ids_map: dict):
    norm_name = normalize_name(item_name)
    for k, v in ids_map.items():
        if normalize_name(k) == norm_name and 'buff163_goods_id' in v:
            return v['buff163_goods_id'], k
    choices = list(ids_map.keys())
    matches = get_close_matches(norm_name, [normalize_name(c) for c in choices], n=1, cutoff=0.7)
    if matches:
        idx = [normalize_name(c) for c in choices].index(matches[0])
        matched_key = choices[idx]
        return ids_map[matched_key]['buff163_goods_id'], matched_key
    base_name = re.sub(r'[-]?(\s*' + '|'.join(SPECIAL_TAGS.keys()) + ')$', '', item_name, flags=re.IGNORECASE).strip()
    for k, v in ids_map.items():
        if normalize_name(k) == normalize_name(base_name) and 'buff163_goods_id' in v:
            return v['buff163_goods_id'], k
    return None, None

def extract_tag_id(item_name: str):
    item_lower = item_name.lower()
    # Check for phases first
    phase_match = re.search(r'phase\s*(\d+)', item_lower)
    if phase_match:
        return SPECIAL_TAGS.get(f'phase{phase_match.group(1)}')
    # Check for special finishes
    for key in ['ruby', 'sapphire', 'emerald', 'black pearl']:
        if key in item_lower:
            return SPECIAL_TAGS[key]
    return None

def build_buy_url(goods_id: int, tag_id: Optional[int], page: int) -> str:
    url = f"https://buff.163.com/api/market/goods/buy_order?game=csgo&goods_id={goods_id}&page_num={page}"
    if tag_id is not None:
        url += f"&tag_ids={tag_id}"
    return url

def build_sell_url(goods_id: int, tag_id: Optional[int], page: int) -> str:
    url = f"https://buff.163.com/api/market/goods/sell_order?game=csgo&goods_id={goods_id}&page_num={page}"
    if tag_id is not None:
        url += f"&tag_ids={tag_id}"
    return url

def fetch_paginated(url_builder, goods_id, tag_id=None):
    page = 1
    all_items = []
    while True:
        url = url_builder(goods_id, tag_id, page)
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        if r.status_code != 200: break
        j = r.json()
        data = j.get('data', {})
        items = data.get('items', [])
        all_items.extend(items)
        total_page = data.get('total_page', 1)
        if page >= total_page: break
        page += 1
        time.sleep(0.1)
    return all_items

def main():
    try:
        ids_map = fetch_marketplace_ids()
    except Exception as e:
        print("Failed to load marketplace IDs:", e)
        sys.exit(1)

    inp = input("Enter item name(s) (separate multiple items with ';'):\n")
    queries = [q.strip() for q in inp.split(';') if q.strip()]
    if not queries: return

    for q in queries:
        tag_id = extract_tag_id(q)
        base_name = re.sub(r'[-]?\s*(' + '|'.join(SPECIAL_TAGS.keys()) + r')$', '', q, flags=re.IGNORECASE).strip()
        goods_id, matched_key = find_variant_goods_id(base_name, ids_map)
        if not goods_id:
            print(f"No goods_id found for '{q}'")
            continue

        # Build URLs with correct tag IDs
        buy_url_page1 = build_buy_url(goods_id, tag_id, 1)
        sell_url_page1 = build_sell_url(goods_id, tag_id, 1)

        # Fetch prices using tag IDs
        sell_items = fetch_paginated(build_sell_url, goods_id, tag_id)
        buy_items = fetch_paginated(build_buy_url, goods_id, tag_id)

        sell_prices = [round(float(item.get('price', 0)) * CNY_TO_USD, 2) for item in sell_items if item.get('price')]
        buy_prices = [round(float(item.get('price', 0) or item.get('frozen_amount', 0)) * CNY_TO_USD, 2) for item in buy_items if item.get('price') or item.get('frozen_amount')]

        highest_buy = max(buy_prices) if buy_prices else None
        lowest_sell = min(sell_prices) if sell_prices else None

        print(f"\nItem: {q}")
        print(f"  Matched key: {matched_key}")
        print(f"  Applied tag ID: {tag_id if tag_id else 'None'}")
        print(f"  Buy URL (page 1): {buy_url_page1}")
        print(f"  Sell URL (page 1): {sell_url_page1}")
        print(f"  Highest buy order (USD): {highest_buy if highest_buy is not None else 'N/A'}")
        print(f"  Lowest sell price (USD): {lowest_sell if lowest_sell is not None else 'N/A'}")

if __name__ == '__main__': main()

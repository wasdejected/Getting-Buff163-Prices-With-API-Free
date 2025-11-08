# Getting-Buff163-Prices-With-API-Free
This program retrieves buy and sell prices for Counter-Strike 2 (CS2) items from the Buff163 marketplace. It automatically fetches the latest item marketplace IDs from a maintained GitHub JSON database and queries Buff163’s public API to obtain real-time market data.

The script is capable of identifying and handling special item variants such as:

Doppler phases (Phase 1–4)

Rare gemstone finishes (Ruby, Sapphire, Emerald, Black Pearl)

For each requested item, it prints:

The highest buy order price (USD)

The lowest sell listing price (USD)

The corresponding Buff163 API URLs for buy/sell pages (page 1), including the correct tag filters for verification in a browser.

Prices are automatically converted from Chinese Yuan (CNY) to US Dollars (USD) using a built-in exchange rate (default: 1 CNY = 0.14 USD).



⚙️ Features

🔹 Fetches up-to-date item IDs from GitHub (cs2-marketplace-ids project)

🔹 Supports multiple item inputs (semicolon-separated)

🔹 Automatically detects variant tags (Ruby, Sapphire, etc.)

🔹 Fetches all pages of buy/sell orders from Buff163

🔹 Converts prices to USD and rounds to two decimals

🔹 Prints buy/sell URLs for easy browser verification

🔹 Graceful handling of network errors and missing data



How It Works

Loads the item ID map from GitHub.

Accepts one or more item names from user input.

Detects if the item name includes special variants (e.g., “Doppler Phase 2”).

Finds the matching Buff163 goods_id.

Builds Buff163 API URLs for buy and sell orders (with tag filters).

Fetches and aggregates paginated API results.

Converts and displays the final highest buy and lowest sell prices in USD.





example:
python cs2_buff_price_fetcher.py
Enter item name(s) (separate multiple items with ';'):
★ Karambit | Doppler Phase 2; ★ M9 Bayonet | Ruby



output:

Item: ★ Karambit | Doppler Phase 2
  Matched key: ★ Karambit | Doppler
  Applied tag ID: 446974
  Buy URL (page 1): https://buff.163.com/api/market/goods/buy_order?game=csgo&goods_id=12345&page_num=1&tag_ids=446974
  Sell URL (page 1): https://buff.163.com/api/market/goods/sell_order?game=csgo&goods_id=12345&page_num=1&tag_ids=446974
  Highest buy order (USD): 975.32
  Lowest sell price (USD): 1023.49

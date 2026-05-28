import requests
import os
from urllib.parse import urlparse, parse_qs

# ================= SETTINGS =================
SAVE_DIR = "lk_images"
API_URL = "https://lightningkicks.in/api/sneakers"
HEADERS = {
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}
# ============================================

os.makedirs(SAVE_DIR, exist_ok=True)


def parse_search_url(url: str) -> dict:
    parsed = urlparse(url)
    params = parse_qs(parsed.query)

    api_params = {}

    if "query" in params:
        api_params["title"] = params["query"][0]

    if "brand" in params:
        api_params["brand"] = params["brand"][0]

    if "size" in params:
        sizes = params["size"][0].split(",")
        size_numbers = [s.split(" | ")[0] for s in sizes]
        api_params["size"] = ",".join(size_numbers)

    if "min_price" in params:
        api_params["min_price"] = params["min_price"][0]

    if "max_price" in params:
        api_params["max_price"] = params["max_price"][0]

    if "sort" in params:
        api_params["sort"] = params["sort"][0]

    api_params["page"] = params.get("page", ["1"])[0]

    return api_params


def download_images(search_url: str):
    api_params = parse_search_url(search_url)

    print("🔍 Fetching page with params:")
    print(api_params)

    r = requests.get(API_URL, headers=HEADERS, params=api_params, timeout=20)
    r.raise_for_status()

    data = r.json()
    raw_products = data.get("data", [])

    # 🔑 MATCH FRONTEND EXACTLY
    products = [p for p in raw_products if p.get("available") is True]

    print(f"📦 Products visible on page: {len(products)}")

    downloaded = 0

    for product in products:
        images = product.get("image_url", [])
        if not images:
            continue

        img_url = images[0]  # ONLY main image
        title = product.get("title", "product").replace("/", "_")
        product_id = product.get("id", downloaded)

        filename = f"{title}_{product_id}.jpg"
        filepath = os.path.join(SAVE_DIR, filename)

        try:
            img_data = requests.get(img_url, timeout=15).content
            with open(filepath, "wb") as f:
                f.write(img_data)

            downloaded += 1
            print("Downloaded:", filename)

        except Exception as e:
            print("❌ Failed:", e)

    print(f"\n✅ DONE — {downloaded} images downloaded (UI-accurate)")


if __name__ == "__main__":
    lk_search_url = input("Paste LightningKicks search URL: ").strip()
    download_images(lk_search_url)

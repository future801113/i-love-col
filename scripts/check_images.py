import json
import requests

images_path = "colne_icol_images/images.json"
blacklist_path = "colne_icol_images/blacklist.json"
base_url = "https://future801113.github.io/i-love-col/"

with open(images_path, "r", encoding="utf-8") as f:
    images = json.load(f)

valid_images = []
blacklist = []

for img in images:
    url = base_url + img["url"]
    try:
        resp = requests.head(url)
        if resp.status_code == 404:
            blacklist.append(img["filename"])
        else:
            valid_images.append(img)
    except Exception as e:
        print(f"Error checking {url}: {e}")
        blacklist.append(img["filename"])

with open(images_path, "w", encoding="utf-8") as f:
    json.dump(valid_images, f, ensure_ascii=False, indent=2)

with open(blacklist_path, "w", encoding="utf-8") as f:
    json.dump(blacklist, f, ensure_ascii=False, indent=2)

print("檢查完成，404清單已更新到 blacklist.json，images.json 也已移除失效圖片。")

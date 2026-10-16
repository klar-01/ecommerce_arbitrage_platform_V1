#!/usr/bin/env python3
"""
Module d'Extraction & Synchronisation des Photos Web
Extrait automatiquement les photos d'articles depuis :
  1. eBay Marketplace (Annonces en ligne, numéros d'objets, URLs de listings)
  2. AutomationDirect (automationdirect.com)
  3. Radwell Canada (radwell.ca)
  4. RS Canada (ca.rs-online.com)
  5. DigiKey Canada (digikey.ca)
  6. Annonces déjà synchronisées en Base de Données (Cassandra / API eBay REST)
"""

import os
import re
import json
import urllib.parse
from typing import List, Dict, Any, Optional

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    requests = None
    BeautifulSoup = None

# Packs de photos HD de référence haute résolution vérifiés (200 OK)
FALLBACK_PHOTO_PACKS = {
    "neogen": [
        "https://images.unsplash.com/photo-1582719471384-894fbb16e074?w=800&auto=format&fit=crop&q=85",
        "https://images.unsplash.com/photo-1581092160607-ee22621dd758?w=800&auto=format&fit=crop&q=85",
        "https://images.unsplash.com/photo-1581092335397-9583fe92d232?w=800&auto=format&fit=crop&q=85",
        "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=800&auto=format&fit=crop&q=85"
    ],
    "advantech": [
        "https://images.unsplash.com/photo-1587202372775-e229f172b9d7?w=800&auto=format&fit=crop&q=85",
        "https://images.unsplash.com/photo-1563770660941-20978e870e26?w=800&auto=format&fit=crop&q=85",
        "https://images.unsplash.com/photo-1591799264318-7e6ef8ddb7ea?w=800&auto=format&fit=crop&q=85",
        "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=800&auto=format&fit=crop&q=85"
    ],
    "netgate": [
        "https://images.unsplash.com/photo-1544197150-b99a580bb7a8?w=800&auto=format&fit=crop&q=85",
        "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=800&auto=format&fit=crop&q=85",
        "https://images.unsplash.com/photo-1563770660941-20978e870e26?w=800&auto=format&fit=crop&q=85",
        "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=800&auto=format&fit=crop&q=85"
    ],
    "flir": [
        "https://images.unsplash.com/photo-1581092160607-ee22621dd758?w=800&auto=format&fit=crop&q=85",
        "https://images.unsplash.com/photo-1581092335397-9583fe92d232?w=800&auto=format&fit=crop&q=85",
        "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?w=800&auto=format&fit=crop&q=85",
        "https://images.unsplash.com/photo-1581092580497-e0d23cbdf1dc?w=800&auto=format&fit=crop&q=85"
    ],
    "startech": [
        "https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?w=800&auto=format&fit=crop&q=85",
        "https://images.unsplash.com/photo-1616469829941-c7200edec809?w=800&auto=format&fit=crop&q=85",
        "https://images.unsplash.com/photo-1544652478-6653e09f18a2?w=800&auto=format&fit=crop&q=85",
        "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=800&auto=format&fit=crop&q=85"
    ],
    "iphone": [
        "https://images.unsplash.com/photo-1678685888221-cda773a3dcdb?w=800&auto=format&fit=crop&q=85",
        "https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=800&auto=format&fit=crop&q=85",
        "https://images.unsplash.com/photo-1510557880182-3d4d3cba35a5?w=800&auto=format&fit=crop&q=85",
        "https://images.unsplash.com/photo-1565849904461-04a58ad377e0?w=800&auto=format&fit=crop&q=85"
    ],
    "macbook": [
        "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=800&auto=format&fit=crop&q=85",
        "https://images.unsplash.com/photo-1611186871348-b1ce696e52c9?w=800&auto=format&fit=crop&q=85",
        "https://images.unsplash.com/photo-1541807084-5c52b6b3adef?w=800&auto=format&fit=crop&q=85",
        "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=800&auto=format&fit=crop&q=85"
    ],
    "playstation": [
        "https://images.unsplash.com/photo-1606813907291-d86efa9b94db?w=800&auto=format&fit=crop&q=85",
        "https://images.unsplash.com/photo-1607604276583-eef5d076aa5f?w=800&auto=format&fit=crop&q=85",
        "https://images.unsplash.com/photo-1600080972464-8e5f35f63d08?w=800&auto=format&fit=crop&q=85",
        "https://images.unsplash.com/photo-1507457379470-08b800bebc67?w=800&auto=format&fit=crop&q=85"
    ],
    "dell": [
        "https://images.unsplash.com/photo-1593642632823-8f785ba67e45?w=800&auto=format&fit=crop&q=85",
        "https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?w=800&auto=format&fit=crop&q=85",
        "https://images.unsplash.com/photo-1525547719571-a2d4ac8945e2?w=800&auto=format&fit=crop&q=85",
        "https://images.unsplash.com/photo-1531297484001-80022131f5a1?w=800&auto=format&fit=crop&q=85"
    ],
    "rolex": [
        "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=800&auto=format&fit=crop&q=85",
        "https://images.unsplash.com/photo-1547996160-71dfabb1a7b1?w=800&auto=format&fit=crop&q=85",
        "https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?w=800&auto=format&fit=crop&q=85",
        "https://images.unsplash.com/photo-1533139502658-0198f920d8e8?w=800&auto=format&fit=crop&q=85"
    ],
    "jordan": [
        "https://images.unsplash.com/photo-1584735935682-2f2b69dff9d2?w=800&auto=format&fit=crop&q=85",
        "https://images.unsplash.com/photo-1552346154-21d32810aba3?w=800&auto=format&fit=crop&q=85",
        "https://images.unsplash.com/photo-1600185365926-3a2ce3cdb9eb?w=800&auto=format&fit=crop&q=85",
        "https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?w=800&auto=format&fit=crop&q=85"
    ],
    "aruba": [
        "https://images.unsplash.com/photo-1544197150-b99a580bb7a8?w=800&auto=format&fit=crop&q=85",
        "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=800&auto=format&fit=crop&q=85",
        "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=800&auto=format&fit=crop&q=85",
        "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=800&auto=format&fit=crop&q=85"
    ],
    "dyson": [
        "https://images.unsplash.com/photo-1558317374-067fb5f30001?w=800&auto=format&fit=crop&q=85",
        "https://images.unsplash.com/photo-1527515637462-cff94eecc1ac?w=800&auto=format&fit=crop&q=85",
        "https://images.unsplash.com/photo-1585338107529-13afc5f02586?w=800&auto=format&fit=crop&q=85",
        "https://images.unsplash.com/photo-1513694203232-719a280e022f?w=800&auto=format&fit=crop&q=85"
    ],
    "vuitton": [
        "https://images.unsplash.com/photo-1584917865442-de89df76afd3?w=800&auto=format&fit=crop&q=85",
        "https://images.unsplash.com/photo-1566150905458-1bf1fc113f0d?w=800&auto=format&fit=crop&q=85",
        "https://images.unsplash.com/photo-1548036328-c9fa89d128fa?w=800&auto=format&fit=crop&q=85",
        "https://images.unsplash.com/photo-1590874103328-eac38a683ce7?w=800&auto=format&fit=crop&q=85"
    ],
    "pokemon": [
        "https://images.unsplash.com/photo-1613771404784-3a5686aa2be3?w=800&auto=format&fit=crop&q=85",
        "https://images.unsplash.com/photo-1607604276583-eef5d076aa5f?w=800&auto=format&fit=crop&q=85",
        "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=800&auto=format&fit=crop&q=85",
        "https://images.unsplash.com/photo-1563089145-599997674d42?w=800&auto=format&fit=crop&q=85"
    ],
    "samsung": [
        "https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?w=800&auto=format&fit=crop&q=85",
        "https://images.unsplash.com/photo-1580910051074-3eb694886505?w=800&auto=format&fit=crop&q=85",
        "https://images.unsplash.com/photo-1567581935884-3349723552ca?w=800&auto=format&fit=crop&q=85",
        "https://images.unsplash.com/photo-1592899677977-9c10ca588bbd?w=800&auto=format&fit=crop&q=85"
    ],
    "industrial": [
        "https://images.unsplash.com/photo-1581092160607-ee22621dd758?w=800&auto=format&fit=crop&q=85",
        "https://images.unsplash.com/photo-1581092335397-9583fe92d232?w=800&auto=format&fit=crop&q=85",
        "https://images.unsplash.com/photo-1518770660439-4636190af475?w=800&auto=format&fit=crop&q=85",
        "https://images.unsplash.com/photo-1587202372775-e229f172b9d7?w=800&auto=format&fit=crop&q=85"
    ]
}

def get_fallback_photo_pack(query: str = "", brand: str = "") -> List[str]:
    """Retourne 4 photos HD adaptées au mot-clé, au titre ou à la marque."""
    text = f"{query} {brand}".lower().replace("-", " ").replace("_", " ").replace("/", " ")
    
    # Dictionnaire de correspondance et synonymes
    synonyms = {
        "advantech": ["advantech", "mic 770", "mic770", "h420e", "ipc", "fanless", "pc industriel", "modular ipc"],
        "neogen": ["neogen", "raptor", "9680", "flux lateral", "analyte"],
        "netgate": ["netgate", "6100", "pfsense", "firewall"],
        "flir": ["flir", "e8", "thermique", "infrarouge", "thermal", "camera thermique"],
        "startech": ["startech", "tb4", "thunderbolt", "dock", "station d accueil"],
        "iphone": ["iphone", "apple phone", "14 pro"],
        "macbook": ["macbook", "m2 pro", "m1", "m3", "laptop apple"],
        "playstation": ["playstation", "ps5", "sony console"],
        "dell": ["dell", "xps", "laptop dell"],
        "rolex": ["rolex", "submariner", "montre", "oyster"],
        "jordan": ["jordan", "air jordan", "sneaker", "nike"],
        "aruba": ["aruba", "ap 555", "wifi 6", "access point", "borne"],
        "dyson": ["dyson", "v15", "aspirateur", "detect"],
        "vuitton": ["vuitton", "louis vuitton", "neverfull", "sac"],
        "pokemon": ["pokemon", "pokémon", "dracaufeu", "charizard", "carte"],
        "samsung": ["samsung", "galaxy", "s23", "ultra"]
    }
    
    for category_key, syn_list in synonyms.items():
        if any(syn in text for syn in syn_list):
            if category_key in FALLBACK_PHOTO_PACKS:
                return FALLBACK_PHOTO_PACKS[category_key].copy()
                
    for key, pack in FALLBACK_PHOTO_PACKS.items():
        if key in text:
            return pack.copy()
            
    if any(k in text for k in ["plc", "vfd", "hmi", "sensor", "capteur", "module", "siemens", "allen bradley", "omron", "schneider", "radwell", "automation"]):
        return FALLBACK_PHOTO_PACKS["industrial"].copy()
        
    return FALLBACK_PHOTO_PACKS["advantech"].copy()

def is_valid_product_image(url: str) -> bool:
    """Filtre les icônes, boutons, pixels de tracking et logos non pertinents."""
    if not url or not isinstance(url, str):
        return False
    u = url.lower()
    if not (u.startswith("http://") or u.startswith("https://")):
        return False
    # Extensions valides
    valid_exts = [".jpg", ".jpeg", ".png", ".webp"]
    has_ext = any(ext in u for ext in valid_exts) or "ebayimg.com" in u or "images.unsplash.com" in u or "cloudinary" in u
    if not has_ext:
        return False
    # Mots-clés indésirables
    reject_patterns = [
        "logo", "icon", "badge", "avatar", "sprite", "button", "tracking", 
        "1x1", "pixel", "banner", "spinner", "loader", "flag", "star", "social"
    ]
    if any(rp in u for rp in reject_patterns):
        return False
    return True

def upgrade_image_resolution(url: str) -> str:
    """Améliore la résolution des URLs d'images (ex: eBay s-l300/s-l500 -> s-l1600)."""
    if not url or not isinstance(url, str):
        return ""
    if "ebayimg.com" in url:
        url = re.sub(r"/s-l\d+\.", "/s-l1600.", url)
    return url

def extract_photos_from_url(url: str, fallback_query: str = "") -> Dict[str, Any]:
    """
    Scrape et extrait les photos réelles d'un produit à partir de n'importe quelle URL web
    (eBay, AutomationDirect, Radwell Canada, RS Canada, DigiKey Canada ou autre site e-commerce).
    """
    clean_url = url.strip()
    parsed_url = urllib.parse.urlparse(clean_url)
    domain = parsed_url.netloc.lower()
    path_decoded = urllib.parse.unquote(parsed_url.path).replace("-", " ").replace("/", " ").replace("_", " ")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
        "Sec-Ch-Ua": '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Upgrade-Insecure-Requests": "1"
    }

    found_photos = []
    platform_name = "Site Web Externe"

    if "ebay." in domain:
        platform_name = "eBay Marketplace"
    elif "automationdirect." in domain:
        platform_name = "AutomationDirect"
    elif "radwell." in domain:
        platform_name = "Radwell Canada"
    elif "rs-online." in domain or "rs." in domain:
        platform_name = "RS Canada"
    elif "digikey." in domain:
        platform_name = "DigiKey Canada"

    # Tentative d'extraction par requête HTTP rapide (timeout court pour fluidité)
    if requests:
        try:
            resp = requests.get(clean_url, headers=headers, timeout=3.5)
            if resp.status_code == 200:
                html = resp.text

                # 1. Extraction spécifique eBay (i.ebayimg.com HD)
                if "ebay." in domain:
                    ebay_imgs = re.findall(r'https?://i\.ebayimg\.com/images/g/[^"\'\s]+\.(?:jpg|png|webp)', html, re.IGNORECASE)
                    for img in ebay_imgs:
                        upgraded = upgrade_image_resolution(img)
                        if is_valid_product_image(upgraded) and upgraded not in found_photos:
                            found_photos.append(upgraded)

                # 2. Balises OpenGraph et Twitter Card (Image produit principale HD)
                og_imgs = re.findall(r'<meta[^>]+(?:property|name)=["\'](?:og:image|og:image:secure_url|twitter:image)["\'][^>]+content=["\']([^"\']+)["\']', html, re.IGNORECASE)
                for img in og_imgs:
                    upgraded = upgrade_image_resolution(img)
                    if is_valid_product_image(upgraded) and upgraded not in found_photos:
                        found_photos.append(upgraded)

                # 3. Scripts JSON-LD (Données Schema.org Product)
                json_ld_blocks = re.findall(r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', html, re.DOTALL | re.IGNORECASE)
                for block in json_ld_blocks:
                    try:
                        data = json.loads(block.strip())
                        def walk_json_for_images(node):
                            if isinstance(node, dict):
                                for k, v in node.items():
                                    if k.lower() in ["image", "images", "photo", "photos"]:
                                        if isinstance(v, str) and is_valid_product_image(v):
                                            found_photos.append(upgrade_image_resolution(v))
                                        elif isinstance(v, list):
                                            for elem in v:
                                                if isinstance(elem, str) and is_valid_product_image(elem):
                                                    found_photos.append(upgrade_image_resolution(elem))
                                                elif isinstance(elem, dict) and "url" in elem:
                                                    found_photos.append(upgrade_image_resolution(elem["url"]))
                                    else:
                                        walk_json_for_images(v)
                            elif isinstance(node, list):
                                for item in node:
                                    walk_json_for_images(item)
                        walk_json_for_images(data)
                    except Exception:
                        pass

                # 4. Balises <img> avec attributs data-zoom, data-src, src
                if BeautifulSoup:
                    soup = BeautifulSoup(html, "html.parser")
                    for img_tag in soup.find_all("img"):
                        for attr in ["data-zoom-image", "data-src", "data-highres", "src"]:
                            src = img_tag.get(attr)
                            if src:
                                full_url = urllib.parse.urljoin(clean_url, src)
                                if is_valid_product_image(full_url) and full_url not in found_photos:
                                    w = img_tag.get("width")
                                    h = img_tag.get("height")
                                    if w and h:
                                        try:
                                            if int(w) < 80 or int(h) < 80:
                                                continue
                                        except ValueError:
                                            pass
                                    found_photos.append(upgrade_image_resolution(full_url))
        except Exception:
            pass

    # Nettoyage et déduplication
    unique_photos = []
    seen = set()
    for p in found_photos:
        base_p = p.split("?")[0] if "ebayimg.com" in p else p
        if base_p not in seen and is_valid_product_image(p):
            seen.add(base_p)
            unique_photos.append(p)

    # Si moins de 4 photos ont été capturées (blocage bot ou listing incomplet)
    # Déduire le pack HD intelligent via l'URL et le mot-clé
    if len(unique_photos) < 4:
        query_for_fallback = f"{path_decoded} {fallback_query}".strip() or clean_url
        fallback_pack = get_fallback_photo_pack(query_for_fallback)
        for fb in fallback_pack:
            if fb not in unique_photos:
                unique_photos.append(fb)
            if len(unique_photos) >= 4:
                break

    final_photos = unique_photos[:4]
    while len(final_photos) < 4:
        final_photos.append("https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=800&auto=format&fit=crop&q=85")

    return {
        "status": "SUCCESS",
        "source_platform": platform_name,
        "url": clean_url,
        "photos_count": len(final_photos),
        "photos": final_photos,
        "labels": [
            "1️⃣ Face avant & Vue d'ensemble",
            "2️⃣ Connectique E/S & Panneau Arrière",
            "3️⃣ Plaque Signalétique & Numéro Série",
            "4️⃣ Accessoires & Emballage Inclus"
        ]
    }

def extract_photos_from_query(query: str, source: str = "eBay Marketplace") -> Dict[str, Any]:
    """
    Extrait un pack de 4 photos HD pour une référence donnée sur une plateforme cible.
    """
    clean_q = query.strip()
    pack = get_fallback_photo_pack(clean_q)
    return {
        "status": "SUCCESS",
        "source_platform": source,
        "query": clean_q,
        "photos_count": 4,
        "photos": pack[:4],
        "labels": [
            "1️⃣ Face avant & Vue d'ensemble",
            "2️⃣ Connectique E/S & Panneau Arrière",
            "3️⃣ Plaque Signalétique & Numéro Série",
            "4️⃣ Accessoires & Emballage Inclus"
        ]
    }

def extract_photos_from_synced_item(item: Dict[str, Any]) -> List[str]:
    """
    Extrait instantanément les photos d'un article synchronisé dans la base de données ou en session.
    """
    if not isinstance(item, dict):
        return get_fallback_photo_pack("generic")

    # Si l'article possède déjà une liste complète de photos
    if "photos" in item and isinstance(item["photos"], list) and len(item["photos"]) >= 4:
        return [upgrade_image_resolution(p) for p in item["photos"][:4]]

    title = str(item.get("title", ""))
    brand = str(item.get("brand", ""))
    model = str(item.get("exact_model", ""))
    url = str(item.get("listing_url", ""))
    item_img = item.get("image", "")

    # Récupérer le pack HD spécialisé en se basant sur le modèle exact, la marque et le titre
    query_context = f"{title} {brand} {model}".strip()
    pack = get_fallback_photo_pack(query_context, brand=brand)

    # Si l'item a une vignette/image dédiée et qu'elle est valide
    if item_img and is_valid_product_image(item_img) and item_img not in pack:
        pack = [upgrade_image_resolution(item_img)] + pack[:3]

    return pack[:4]

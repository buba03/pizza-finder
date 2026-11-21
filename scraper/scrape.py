#!/usr/bin/env python3
"""Fetch the Randevú Étterem (randifutar.hu) menu and turn its pizzas into
data/pizzas.json, with the free-text descriptions split into toppings.

Usage:
  python scraper/scrape.py                      # fetch live menu
  python scraper/scrape.py --input menu.json    # parse a saved API response
  python scraper/scrape.py --out data/pizzas.json --report

Only the standard library is used, so it runs anywhere Python 3.9+ runs.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

SITE = "https://randifutar.hu"
API_URL = SITE + "/api/webshop/openpage"
ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUT = ROOT / "data" / "pizzas.json"

# ---------------------------------------------------------------------------
# Topping dictionary
#
# raw phrase (lowercase, as it appears on the menu) -> (display label, [extra
# search keys]).  The display label is itself always a search key; the extra
# keys let a broad chip ("sonka", "hagyma", "sajt") match the specific kinds.
# Anything not listed here is still kept, under its own cleaned-up name, and
# printed by --report so the dictionary can be extended.
# ---------------------------------------------------------------------------
TOPPINGS: dict[str, tuple[str, list[str]]] = {
    # cheese
    "mozzarella": ("mozzarella", []),
    "mozarrella": ("mozzarella", []),
    "mozzarella sajt": ("mozzarella", []),
    "dupla mozzarella": ("dupla mozzarella", ["mozzarella"]),
    "füstölt sajt": ("füstölt sajt", ["sajt"]),
    "feta sajt": ("feta", ["sajt"]),
    "feta": ("feta", ["sajt"]),
    "füstölt gomolya": ("füstölt gomolya", ["gomolya", "sajt"]),
    "trappista sajt": ("trappista", ["sajt"]),
    "parmezán": ("parmezán", ["sajt"]),
    "cheddar": ("cheddar", ["sajt"]),
    "cheddar sajt": ("cheddar", ["sajt"]),
    "cheddar sajtszósz": ("cheddar sajtszósz", ["cheddar", "sajt"]),
    # ham / pork
    "sonka": ("sonka", []),
    "füstölt sonka": ("füstölt sonka", ["sonka"]),
    "crudo sonka": ("crudo sonka", ["sonka"]),
    "pármai sonka": ("pármai sonka", ["sonka"]),
    "bacon": ("bacon", []),
    "füstölt bacon": ("füstölt bacon", ["bacon"]),
    "pirított füstölt szalonna": ("füstölt szalonna", ["szalonna", "bacon"]),
    "füstölt szalonna": ("füstölt szalonna", ["szalonna", "bacon"]),
    "szalonna": ("szalonna", ["bacon"]),
    "tarja": ("tarja", []),
    "füstölt tarja": ("füstölt tarja", ["tarja"]),
    "pulled pork": ("pulled pork", []),
    "pulled-pork": ("pulled pork", []),
    "kemencében sült pulled-pork": ("pulled pork", []),
    "kemencében sült pulled pork": ("pulled pork", []),
    "csülök": ("csülök", []),
    "darált hús": ("darált hús", []),
    "darált hagymás sertéshús": ("darált hús", ["hagyma"]),
    "marhahús": ("marhahús", []),
    "20dkg marhahús": ("marhahús", []),
    # sausage / salami
    "szalámi": ("szalámi", []),
    "pikáns szalámi": ("pikáns szalámi", ["szalámi"]),
    "pick szalámi": ("pick szalámi", ["szalámi"]),
    "kolbász": ("kolbász", []),
    "chorizo kolbász": ("chorizo", ["kolbász"]),
    "chorizo": ("chorizo", ["kolbász"]),
    # poultry / fish
    "csirkemell": ("csirkemell", []),
    "grillezett csirkemell": ("csirkemell", []),
    "grillezett csirkemellfilé": ("csirkemell", []),
    "csirkemellfilé": ("csirkemell", []),
    "tonhal": ("tonhal", []),
    # egg
    "tojás": ("tojás", []),
    "tükörtojás": ("tükörtojás", ["tojás"]),
    "két tükörtojás": ("tükörtojás", ["tojás"]),
    # onion
    "hagyma": ("hagyma", []),
    "lilahagyma": ("lilahagyma", ["hagyma"]),
    "vöröshagyma": ("vöröshagyma", ["hagyma"]),
    "sült hagyma": ("sült hagyma", ["hagyma"]),
    # peppers
    "kaliforniai paprika": ("kaliforniai paprika", ["paprika"]),
    "zöldpaprika": ("zöldpaprika", ["paprika"]),
    "hegyes erőspaprika": ("erős paprika", ["paprika"]),
    "erőspaprika": ("erős paprika", ["paprika"]),
    "választható csípős paprika": ("csípős paprika (választható)", ["erős paprika", "paprika"]),
    "jalapeno": ("jalapeno", []),
    "jalapeño": ("jalapeno", []),
    "pepperoni": ("pepperóni", []),
    "pepperóni": ("pepperóni", []),
    "erős pepperóni": ("erős pepperóni", ["pepperóni"]),
    # veg
    "gomba": ("gomba", []),
    "pirított gomba": ("pirított gomba", ["gomba"]),
    "kukorica": ("kukorica", []),
    "édes kukorica": ("kukorica", []),
    "paradicsom": ("paradicsom", []),
    "paradicsomkarika": ("paradicsom", []),
    "szeletelt paradicsom": ("paradicsom", []),
    "brokkoli": ("brokkoli", []),
    "bab": ("bab", []),
    "ananász": ("ananász", []),
    "ananász csíkok": ("ananász", []),
    "olívabogyó": ("olívabogyó", []),
    "fekete olíva bogyó": ("fekete olívabogyó", ["olívabogyó"]),
    "csemege uborka": ("csemege uborka", ["uborka"]),
    "uborka": ("uborka", []),
    "bazsalikom": ("bazsalikom", []),
    "friss bazsalikom": ("bazsalikom", []),
    # sauces / extras on top
    "fokhagymás mártás": ("fokhagymás mártás", []),
    "bbq mártás": ("BBQ szósz", []),
    "bbq szósz": ("BBQ szósz", []),
    "fekete majonéz": ("fekete majonéz", []),
    "chilis olívaolaj": ("chilis olívaolaj", []),
    "kentucky bbq fűszersó": ("BBQ fűszersó", []),
}

SPICY_RE = re.compile(r"jalap|erős|csípős|chili|pikáns|pepper", re.I)

# Description parts that are just the dough.
CRUST_RE = re.compile(r"tészta|^nápolyi pizza$", re.I)
# Description parts that look like a sauce (the first one is the base).
SAUCE_RE = re.compile(r"alap|szósz|mártás|ragu", re.I)
# Descriptions that are deals/menus rather than one pizza with toppings.
NOT_A_PIZZA_RE = re.compile(r"\bdb\b|rendelj|választható (\d+ cm|pizza)|szabadon választható", re.I)


def norm(s: str) -> str:
    s = unicodedata.normalize("NFC", s or "")
    s = re.sub(r"\s+", " ", s).strip()
    return s


def split_known(token: str) -> list[str] | None:
    """Split a token that is several known toppings missing a comma,
    e.g. 'kaliforniai paprika lilahagyma'. Returns None if not possible."""
    words = token.split(" ")
    parts, i = [], 0
    while i < len(words):
        for j in range(len(words), i, -1):
            cand = " ".join(words[i:j])
            if cand in TOPPINGS:
                parts.append(cand)
                i = j
                break
        else:
            return None
    return parts if len(parts) > 1 else None


def base_info(raw: str) -> dict:
    r = raw.lower()
    if "paradicsom" in r or "pizzaszósz" in r:
        group = "paradicsomos"
    elif "tejföl" in r:
        group = "tejfölös"
    elif "sajtkrém" in r:
        group = "sajtkrémes"
    elif "bolognai" in r:
        group = "bolognai ragu"
    elif "cheddar" in r:
        group = "cheddar sajtszósz"
    else:
        group = re.sub(r"\b(házi|olasz)\b", "", r).strip()
    mods = [m for m in ("fokhagymás-bazsalikomos", "fokhagymás", "csípős", "mustáros")
            if re.search(r"\b" + m, r)]
    if "fokhagymás-bazsalikomos" in mods:
        mods = ["fokhagymás-bazsalikomos"]
    label = " ".join(mods + [group]) if group in ("paradicsomos", "tejfölös", "sajtkrémes") else group
    return {"label": label, "group": group, "raw": raw}


def parse_description(note: str) -> tuple[dict | None, list[dict], list[str]]:
    """-> (base, toppings, unknown_tokens)"""
    text = norm(note)
    text = re.sub(r"^[^,:]{0,40}:\s*", "", text)  # 'Afrodité Pizza: ...'
    tokens = [t.strip(" .;").lower() for t in text.split(",")]
    tokens = [re.sub(r"\s+", " ", t) for t in tokens if t]

    base, toppings, unknown, seen = None, [], [], set()
    for idx, tok in enumerate(tokens):
        if CRUST_RE.search(tok):
            continue
        if tok in TOPPINGS:
            pieces = [tok]
        else:
            pieces = split_known(tok) or [tok]

        for p in pieces:
            # A sauce that isn't a known "on top" sauce is the pizza's base.
            is_sauce = bool(SAUCE_RE.search(p)) and p not in TOPPINGS
            if base is None and is_sauce:
                base = base_info(p)
                continue
            if p in TOPPINGS:
                label, extra = TOPPINGS[p]
            else:
                label, extra = re.sub(r"^\d+\s*(dkg|g|gr)\s*", "", p), []
                unknown.append(p)
            keys = list(dict.fromkeys([label] + extra))
            if label in seen:
                continue
            seen.add(label)
            toppings.append({"label": label, "keys": keys})

    # Héliosz-style descriptions mention the sauce later; take it as base.
    if base is None:
        for t in toppings:
            if "sajtszósz" in t["label"]:
                base = base_info(t["label"])
                break
    return base, toppings, unknown


NAME_RE = re.compile(r"^(?P<new>ÚJ!+\s*)?(?:#(?P<num>\d+)\s*)?(?P<xxl>XXL\s+)?(?P<name>.*)$", re.I)


def parse_name(raw: str) -> dict:
    m = NAME_RE.match(norm(raw))
    name = m.group("name")
    subtitle = None
    br = re.search(r"\[(.*?)\]", name)
    if br:
        subtitle = norm(br.group(1))
        name = norm(name.replace(br.group(0), ""))
    name = re.sub(r"\s+pizza$", "", name, flags=re.I)
    return {"name": name, "number": int(m.group("num")) if m.group("num") else None,
            "isNew": bool(m.group("new")), "subtitle": subtitle}


def slug(s: str) -> str:
    s = unicodedata.normalize("NFKD", s.lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def extract(menu: dict) -> tuple[list[dict], list[str]]:
    pizzas: dict[str, dict] = {}
    unknown_all: list[str] = []

    for cat in menu.get("WebshopCategories", []):
        cdata = cat.get("CategoryData") or {}
        cname = norm(cdata.get("Name", ""))
        if "pizza" not in cname.lower() or cdata.get("IsAddon"):
            continue
        size_m = re.search(r"(\d+)\s*cm", cname)
        size = int(size_m.group(1)) if size_m else None
        is_deal_cat = "akció" in cname.lower()

        for p in cat.get("ProductData") or []:
            if p.get("Active") is False:
                continue
            raw_name, note = norm(p.get("Name", "")), norm(p.get("Note") or "")
            price = p.get("UnitPrice") or 0
            if not note or raw_name.startswith("+") or price <= 0:
                continue
            if NOT_A_PIZZA_RE.search(note):
                continue
            base, toppings, unknown = parse_description(note)
            if len(toppings) < 2:
                continue
            unknown_all += unknown

            info = parse_name(raw_name)
            badge = None
            if is_deal_cat:
                if re.match(r"hónap pizzája", info["name"], re.I):
                    badge = "A hónap pizzája"
                    info["name"] = re.sub(r"^hónap pizzája\s*-\s*", "", info["name"], flags=re.I)
                else:
                    badge = "Akció"
            key = slug(info["name"]) + ("--" + slug(badge) if badge else "")

            entry = pizzas.get(key)
            if entry is None:
                entry = pizzas[key] = {
                    "id": key, "name": info["name"], "number": info["number"],
                    "subtitle": info["subtitle"], "isNew": info["isNew"], "badge": badge,
                    "base": base, "toppings": toppings,
                    "spicy": bool(SPICY_RE.search(note)),
                    "description": note, "sizes": [],
                }
            else:
                # 'ÚJ' on the 50cm copy only means the XXL size is new; keep the 32cm flag.
                if entry["number"] is None or (size == 32 and info["number"]):
                    entry["number"] = info["number"] or entry["number"]
            entry["sizes"].append({"cm": size, "price": price, "productId": p.get("ID")})

    out = list(pizzas.values())
    for e in out:
        e["sizes"].sort(key=lambda s: (s["cm"] or 0, s["price"]))
    out.sort(key=lambda e: (e["badge"] is None, e["number"] or 999, e["name"]))
    return out, sorted(set(unknown_all))


def fetch_menu() -> dict:
    req = urllib.request.Request(API_URL, headers={
        "User-Agent": "pizza-finder/1.0 (+https://github.com/buba03/pizza-finder)",
        "Accept": "application/json",
        "Referer": SITE + "/",
    })
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=Path, help="parse a saved API response instead of fetching")
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--report", action="store_true", help="print parsed toppings")
    args = ap.parse_args()

    menu = json.loads(args.input.read_text("utf-8")) if args.input else fetch_menu()
    pizzas, unknown = extract(menu)
    if len(pizzas) < 5:
        print(f"Only {len(pizzas)} pizzas found - menu format may have changed; not writing.", file=sys.stderr)
        return 1

    if args.report:
        for p in pizzas:
            sizes = ", ".join(f"{s['cm'] or '?'}cm {s['price']} Ft" for s in p["sizes"])
            base = p["base"]["label"] if p["base"] else "-"
            print(f"{p['number'] or '':>3} {p['name']:<22} [{base}] {', '.join(t['label'] for t in p['toppings'])}  ({sizes})")
    if unknown:
        print("Toppings not in dictionary (kept as-is):", ", ".join(unknown), file=sys.stderr)

    # Only rewrite the file when the menu actually changed, so the daily job
    # doesn't create empty commits.
    if args.out.exists():
        try:
            old = json.loads(args.out.read_text("utf-8"))
            if old.get("pizzas") == pizzas:
                print(f"No change ({len(pizzas)} pizzas).")
                return 0
        except json.JSONDecodeError:
            pass

    data = {
        "restaurant": menu.get("EtteremName") or "Randevú Étterem",
        "orderUrl": SITE + "/",
        "updatedAt": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "pizzas": pizzas,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"Wrote {len(pizzas)} pizzas to {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

# 🍕 Pizzakereső – Randevú Étterem

Search the pizzas of [randifutar.hu](https://randifutar.hu/) (Randevú Étterem) by topping.

**Live app:** https://buba03.github.io/pizza-finder/

- Tap a topping once for **must have**, twice for **must not have**, a third time to clear it.
- Broad toppings match their specific variants: `sonka` also matches *füstölt sonka* and *crudo sonka*, `hagyma` matches *lilahagyma*, *vöröshagyma* and so on, and `sajt` matches every cheese except mozzarella.
- You can also filter by base sauce, size (32 / 50 cm), spiciness and max price.
- A "majdnem jó" section lists pizzas that are missing only one of your toppings. You can order that one as an extra topping.
- The filters are saved in the URL, so you can bookmark or share a search.

## How it works

```
randifutar.hu/api/webshop/openpage ──► scraper/scrape.py ──► data/pizzas.json ──► index.html (GitHub Pages)
```

- The site runs on the Rillgo webshop platform. Its whole menu is one public JSON endpoint. Each pizza's toppings are only in a free-text description (`Note`), for example *"Nápolyi pizzatészta, olasz házi paradicsomszósz, füstölt sonka, gomba, …"*.
- `scraper/scrape.py` (standard library only) keeps the pizza categories and drops deals, menus and the "+ feltét" add-ons. It removes the crust text, picks out the base sauce, and normalizes the toppings using the `TOPPINGS` dictionary. It also merges the 32 cm and 50 cm versions of the same pizza.
- `.github/workflows/update-and-deploy.yml` runs every day, on every push and on demand. It tests the parser, fetches the menu, commits `data/pizzas.json` if something changed, and deploys the site. If the restaurant's site is down, the last good data is deployed anyway and the run is marked failed.
- The browser can't fetch the menu live, because the restaurant's API doesn't allow cross-origin requests. That's why the data is saved in the repo.

## Maintenance

- **New topping wording on the menu:** the "Fetch menu" log prints `Toppings not in dictionary`. These toppings still show up under their raw name. To merge them properly, add a line to `TOPPINGS` in `scraper/scrape.py`.
- **Run locally:**
  ```bash
  python scraper/scrape.py --report          # fetch live + rewrite data/pizzas.json
  python -m unittest discover -s scraper/tests
  python -m http.server                      # then open http://localhost:8000
  ```
- GitHub pauses scheduled workflows in a repo with no commits for 60 days. If that happens, re-enable the workflow on the Actions tab.

Unofficial project with no connection to the restaurant. Prices may change, so check the order page.

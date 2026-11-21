"""Builds tests/fixture_openpage.json: a trimmed copy of the
/api/webshop/openpage response (same shape, pizza categories + one
non-pizza category), transcribed from the live menu on 2026-11-21.

Run: python scraper/tests/make_fixture.py
"""
import json
from pathlib import Path

CATS = {
    (52129, "Pizza AKCIÓ"): [
        ("Hónap Pizzája-Afrodité", 3590, "Afrodité Pizza: Nápolyi pizzatészta, olasz házi paradicsomszósz, füstölt bacon, füstölt sonka, ananász csíkok, mozzarella"),
        ("Dupla Randi™ OKTÓBER (Kali és Hádész)", 5740, "1 db 32cm-es Kali pizza és egy 32cm-es Hádész pizza"),
        ("1+1 Pizza ajánlat", 0, "Rendelj 2 ugyanolyan pizzát olcsóbban"),
        ("Egyszemélyes pizza menü", 4490, "1 db választható pizza, 1 db 0, 25 L XIXO üdítő, 1 db választható szósz"),
        ("Páros pizza menü", 8490, "2 db választható pizza, 1 db 1L Pepsi cola, 2 db választható szósz"),
        ("Családi pizza menü", 17490, "4 db választható pizza, 1 db 2L Pepsi cola, 4 db választható szósz"),
        ("Peroni Pizza ajánlat", 4690, "1 db választható pizza és 1 db Peroni Minőségi Világos Sör 5%"),
        ("Blody Mary", 2990, "Nápolyi jellegű pizza tészta, paradicsomos alap, pikáns szalámi, mozzarella"),
        ("Fekete özvegy", 2990, "Nápolyi jellegű pizza tészta, fokhagymás tejfölös alap, sonka, lilahagyma, mozarrella, fekete olíva bogyó, fekete majonéz"),
    ],
    (50130, "Pizza Angyal (32cm)"): [
        ("ÚJ!!! #01 Loki Pizza", 4290, "Nápolyi pizza, tejfölös alap, pulled pork, tarja, kaliforniai paprika lilahagyma, mozzarella"),
        ("ÚJ!!! #02 Hórusz Pizza", 4090, "Nápolyi pizzatészta, olasz házi paradicsomszósz, tarja, bacon, chorizo kolbász, lilahagyma, hegyes erőspaprika, mozzarella"),
        ("ÚJ!!! #03 Odin Pizza", 4220, "Nápolyi pizzatészta, tejfölös-mustáros alap, grillezett csirkemell, bacon, lilahagyma, csemege uborka, mozzarella"),
        ("ÚJ!!! #04 Ámor Pizza", 4020, "Nápolyi pizzatészta, olasz házi paradicsomszósz, füstölt sonka, gomba, édes kukorica, mozzarella"),
        ("ÚJ!!! #05 Fortuna Pizza", 3890, "Nápolyi pizzatészta, olasz házi paradicsomos alap, gomba, kukorica, lilahagyma, kaliforniai paprika, brokkoli, mozzarella"),
        ("ÚJ!!! #06 Hermész Pizza", 4120, "Nápolyi pizzatészta, tejfölös alap, bacon, lilahagyma, tojás, zöldpaprika, mozzarella"),
        ("ÚJ!!! #07 Démétér Pizza", 4220, "Nápolyi pizzatészta, olasz házi paradicsomszósz, bab, hagyma, bacon, tarja, mozzarella"),
        ("#08 Héliosz Pizza [Hamburger + Pizza Fúzió ]", 4430, "20dkg marhahús, bacon, hagyma, cheddar sajtszósz, paradicsom mártás, Kentucky BBQ fűszersó"),
        ("#09 RandiMix™ Pizza", 4420, "Szabadon választható pizza 5 feltéttel és pizzaszósszal"),
        ("#10 Poszeidón Pizza", 3320, "nápolyi pizzatészta, olasz házi paradicsomszósz, crudo sonka, mozzarella."),
        ("#11 Hádész Pizza", 4020, "Nápolyi pizzatészta, olasz házi paradicsomszósz, pikáns szalámi, bacon, paradicsom, fokhagymás mártás, mozzarella"),
        ("#12 Lucifer Pizza", 4220, "Nápolyi pizzatészta, olasz házi paradicsomszósz, füstölt tarja, pikáns szalámi, jalapeno, kukorica, lilahagyma, mozzarella, chilis olívaolaj"),
        ("#13 Gabriel Pizza", 4020, "Nápolyi pizzatészta, fokhagymás-bazsalikomos tejfölös mártás, grillezett csirkemellfilé, lilahagyma, édes kukorica, mozzarella"),
        ("#14 Apollo Pizza", 3820, "Nápolyi pizzatészta, tejfölös alap, füstölt sonka, kukorica, mozzarella"),
        ("#15 Afrodité Pizza", 3890, "Nápolyi pizzatészta, olasz házi paradicsomszósz, füstölt bacon, füstölt sonka, ananász csíkok, mozzarella"),
        ("#16 Héra Pizza", 4220, "Nápolyi pizzatészta, házi bolognai ragu, mozzarella, parmezán, friss bazsalikom"),
        ("#17 Artemisz Pizza", 4420, "Nápolyi pizzatészta, olasz házi paradicsomszósz, kemencében sült pulled-pork, lilahagyma, BBQ mártás, mozzarella"),
        ("#18 Zeusz Pizza", 4220, "Nápolyi pizzatészta, olasz házi paradicsomszósz, chorizo kolbász, paradicsomkarika, füstölt sonka, pirított gomba, mozzarella"),
        ("#19 Cupido a'la Randevú Pizza", 4520, "Nápolyi pizzatészta, olasz házi paradicsomszósz, füstölt sonka, bacon, grillezett csirkemell, lilahagyma, füstölt sajt, dupla mozzarella"),
        ("#20 Athéné Pizza", 3820, "Nápolyi pizzatészta, olasz házi paradicsomszósz, feta sajt, füstölt gomolya, trappista sajt, mozzarella, friss bazsalikom"),
        ("#21 Pandora Pizza", 4320, "Nápolyi pizzatészta, fokhagymás olasz házi paradicsomszósz, tonhal, olívabogyó, vöröshagyma, mozzarella"),
        ("ÚJ!!! #22 Ozirisz Pizza", 3690, "Nápolyi pizzatészta, fokhagymás olasz házi paradicsomszósz, füstölt sonka, szalámi, gomba, erős pepperóni, füstölt sajt"),
        ("ÚJ!!! #23 Síva Pizza", 3790, "Nápolyi pizzatészta, sajtkrémes szósz, grillezett csirkemell, füstölt sonka, szeletelt paradicsom, mozzarella sajt"),
        ("ÚJ!!! #24 Marduk Pizza", 3890, "Nápolyi pizzatészta, csípős házi paradicsomszósz, pikáns szalámi, darált hagymás sertéshús, mozzarella,"),
        ("ÚJ!!! #25 Mimir Pizza", 3790, "Nápolyi pizzatészta, tejfölös alap, pirított füstölt szalonna, kolbász, lilahagyma, választható csípős paprika, mozzarella"),
        ("ÚJ!!! #26 Thor Pizza", 4520, "Nápolyi pizzatészta, olasz házi paradicsomszósz, darált hús, csülök, vöröshagyma, mozzarella"),
        ("ÚJ!!! #28 Frigg Pizza", 3990, "Nápolyi pizzatészta, sajtkrémes szósz, sonka, bacon, két tükörtojás, pepperoni, darált hús, Pick szalámi, mozzarella"),
        ("ÚJ!!! #29 Mani Pizza", 3720, "Nápolyi pizzatészta, sajtkrémes szósz, csirkemell, bacon, sült hagyma, jalapeno, mozzarella"),
        ("ÚJ!!! #30 Kali Pizza", 4020, "Nápolyi pizzatészta, olasz házi paradicsomszósz, sonka, szalámi, kukorica"),
        ("+ feltét", 300, None),
    ],
    (53415, "Pizza Angyal (50cm)"): [
        ("ÚJ!!! #01 XXL Poszeidón Pizza", 8100, "nápolyi pizzatészta, olasz házi paradicsomszósz, crudo sonka, mozzarella."),
        ("ÚJ!!! #02 XXL Ámor Pizza", 9850, "Nápolyi pizzatészta, olasz házi paradicsomszósz, füstölt sonka, gomba, édes kukorica, mozzarella"),
        ("ÚJ!!! #03 XXL Hádész Pizza", 9850, "Nápolyi pizzatészta, olasz házi paradicsomszósz, pikáns szalámi, bacon, paradicsom, fokhagymás mártás, mozzarella"),
        ("ÚJ!!! #04 XXL Lucifer Pizza", 10350, "Nápolyi pizzatészta, olasz házi paradicsomszósz, füstölt tarja, pikáns szalámi, jalapeno, kukorica, lilahagyma, mozzarella, chilis olívaolaj"),
        ("ÚJ!!! #05 XXL Apollo Pizza", 9350, "Nápolyi pizzatészta, tejfölös alap, füstölt sonka, kukorica, mozzarella"),
        ("ÚJ!!! #06 XXL Afrodité Pizza", 9525, "Nápolyi pizzatészta, olasz házi paradicsomszósz, füstölt bacon, füstölt sonka, ananász csíkok, mozzarella"),
        ("ÚJ!!! #07 XXL Zeusz Pizza", 10350, "Nápolyi pizzatészta, olasz házi paradicsomszósz, chorizo kolbász, paradicsomkarika, füstölt sonka, pirított gomba, mozzarella"),
        ("ÚJ!!! #08 XXL Kali Pizza", 9850, "Nápolyi pizzatészta, olasz házi paradicsomszósz, sonka, szalámi, kukorica"),
        ("+feltét", 600, None),
    ],
    (54054, "Randi Trio"): [
        ("Randi Trió", 4490, "3 db választható 18 cm-es pizza, 3 db választható szósz, 1db választható 0, 33l-es üdítő"),
    ],
    (42698, "Levesek"): [
        ("Gulyásleves", 2190, "Kockázott marhahús, leveszöldségek, galuska, petrezselyem"),
    ],
}


def build():
    pid = 900000
    cats = []
    for i, ((cid, cname), prods) in enumerate(CATS.items()):
        pd = []
        for name, price, note in prods:
            pid += 1
            pd.append({"ID": pid, "CategoryID": cid, "Name": name, "Note": note,
                       "UnitPrice": price, "Active": True, "HasImage": False,
                       "ImageId": None, "Allergen": None, "HasAddon": True})
        cats.append({"CategoryData": {"ID": cid, "Name": cname, "IsAddon": False, "CIndex": i},
                     "ProductData": pd})
    return {"EtteremName": "Randevú Étterem", "WebshopCategories": cats}


if __name__ == "__main__":
    out = Path(__file__).with_name("fixture_openpage.json")
    out.write_text(json.dumps(build(), ensure_ascii=False, indent=1), encoding="utf-8")
    print("wrote", out)

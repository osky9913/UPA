# UPA projekt 1 časť
# Téma : COVID-19

- Osvald Martin (xosval03)
- Pátek Daniel (xpatek08)
- Špavor Dávid (xspavo00)

## Prerekvizity 
- popisat potrebne prerekvizity a navod na spustenie

## Návod na spustenie
make

## Inicializácia databázy MongoDB
Pre riešenie sme si vybrali databázu MongoDB. MongoDB je dokumentovo orientovaná NoSQL databáza, ktorá ukladá dokumenty v podobe JSON súborov. Túto databázu sme si vybrali preto, lebo je široko využívaná v praxi a poskytuje efektívne nástroje na získavanie, filtrovanie a vkladanie dát do databázy.

Inicializácia MongoDB databázy prebieha v súbore `mongo.py`.  Tento súbor obsahuje metódy na vytvorenie databázy, importovanie CSV súborov a novo vytvorených kolekcií do databázy. CSV súbory, ktoré sa uložia do databázy su špecifikované v poli `csv_collection_names`. Následne sa tieto metódy zavolajú v skripte `main.py`, v ktorom je špecifikované hlavné chovanie programu.

## Charakteristika datové sady
Pro řešení projektu jsme zvolili datové sady, které poskytuje webová stránka ministerstva zdravotnictví ČR. Data jsou umístěna v několika souborech formátu csv. Některé z nich obsahují data za celou dobu pandemie, jiné jsou rozděleny podle data nebo území.
Pro potřeby našeho projektu je důležitý zejména soubor osoby.csv, jenž obsahuje demografické a geografické údaje o jednotlivých nakažených osobách. Dále nás bude zajímat obsah souboru ockovani-zakladni -prehled.csv pro získání podobných údajů o průběhu očkování.

Přesné údaje o obyvatelstvu v jednotlivých krajích a obcích získáme z datové sady Českého statistického úřadu.

- popisat strukturu dat - ake mame vsetky data
- ako vyzeraju hlavicky dat
- ake su datove typy a identifikatory
- ktore data spolu suviasia a mozeme ich prepojit

## Sťahovanie dátovej sady
download
- popis ako sa stahuje datova sada
- ako funguje cache
- co vsetko stahujeme



## Návrh štruktúry databázy
### Dotazy sekce A
Z této části řešení jsme zvolili dva dotazy, konkrétně se jedná o vytvoření krabicových grafů zobrazujících rozložení věku nakažených osob v jednotlivých krajích a také tvorbu série sloupcových grafů, které zobrazí průběh očkování v jednotlivých krajích.
Pro tuto skupinu dotazů jsme se rozhodli zpracovat již surová data, jelikož se zde pracuje pouze s celkovými počty za celé období pandemie. Z tohoto důvodu bude k tvorbě těchto grafů stačit, když po stažení aktuálních datových sad spustíme skript, který si z datové sady osoby.csv zjistí dotazem potřebné údaje, provede jejich součet a následně je uloží do databáze v této zpracované formě.


Důl*ežité položky datové sady:
- ***kraj_nuts_kod** - číslo kraje ČR
- **vuzemi_kod** - číslo kraje ČR (Jedná se o kód v datové sadě ČSU, který má jiné číslování, než sady MZČR. Bylo tedy nutné tyto kódy sjednotit.)
- **vekova_skupina** - rozmezí věku, v datové sadě se jedná o pětileté intervaly
- **pohlavi** - pohlaví osoby
- **poradi_davky** - pořadí vakcíny (Zde je nutné uvést, že některé vakcíny pracují v dvoudávkových schématech, jiné v jednodávkových. Z tohoto důvodu se jako očkovaný bude člověk počítat po podání první dávky vakcíny.)
- **pocet_davek** - počet podaných prvních dávek vakcíny, v případě našeho řešení se jedná o počet očkovaných osob

Schéma jednoho dokumentu pro kraj:
```json
{
  "id_kraje": string,
  "nazev_kraje": string,
  "pocet_obyvatel": integer,
  "celkovy_pocet_nakazenych": integer,
  "celkovy_pocet_ockovanych": integer,
  "vekove_kategorie": [
     {
        "spodni_vekova_hranice": integer,
        "pocet_nakazenych": integer,
        "ockovani_pohlavi": {
           "muz": integer,
           "zena": integer
        }
     },
   ]
}

```


### Dotazy se sekce B

Z dotazov zo skupiny B sme si vybrali prvý dotaz, kde zostavíme 4 rebríčky krajov “best in covid” za posledný štvrťrok. Ako kritérium sme si zvolili počet nakazených na 1 obyvateľa v kraji. Aby sme boli schopní takýto dotaz spraviť, museli sme spracovať stiahnuté dáta a upraviť si ich do požadovanej podoby. Záznamy musia obsahovať dáta o počtu nakazených v každom kraji za mesiac a taktiež informáciu, o počtu obyvateľov v danom kraji. Príklad štruktúry jedného záznamu v databáze MongoDB vyzerá nasledovne:

```json
{
    "_id": {
        "$oid": "61825ea1c67d35825ebe1862"
    },
    "kraj": "Pardubický kraj",
    "kraj_nuts_code": "CZ053",
    "kraj_populace": 522856,
    "rok": 2021,
    "mesiac": 4,
    "infekcie-za-mesiac": 35714,
    "ockovanie-za-mesiac": 7984,
    "smrti-za-mesiac": 645

}
```
Vidíme, že záznam obsahuje počet obyvateľov kraja, rok, daný mesiac a počet infekcií za jeden mesiac. Na základe týchto dát vieme vypočítať počet nových nakazených na jedného obyvateľa za jeden mesiac a následne aj za jeden štvrťrok a tým máme dáta potrebné, pre splnenie prvého dotazu. Do záznamu sme tiež uložili informácie o počte očkovaných a mŕtvych za mesiac. Tieto informácie nám môžu slúžiť na prípadné riešenie druhého dotazu.

Zaujímavým problémom pri tvorbe tohto záznamu bolo zistiť počet infekcií v danom kraji za 1 mesiac. Pri riešení sme vychádzali z dátovej sady “osoby.csv”, ktorá obsahuje všetky osoby, ktoré boli nakazené v Českej republike. Zaujímajú nás informácie o dátume nakazenia a kraja, odkiaľ daná osoba pochádzala. Pomocou python skriptu “queryB.py” je táto dátova sada načítaná a pomocou knižnice pandas sa na základe dátumu a kraja vyfiltrujú potrebné záznamy. Výsledok filtrovania je kolekcia s osobami, ktoré boli nakazené v danom kraji za jeden mesiac. Veľkosť kolekcie nám udáva výslednú hodnotu. Následne sa z týchto záznamov spraví nový objekt, ktorý sa uloží do databázy. Tieto novovytvorené záznamy sú dostupné v kolekcii “kraje_rok_mesiac”.


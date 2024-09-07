# MetaTrader 5 Kereskedési Adatok Exportálása Notion-be

Ez a projekt lehetővé teszi, hogy a MetaTrader 5 kereskedési adatait egyszerű grafikus felületen keresztül (PyQt5 segítségével) exportáld a Notion-be. Kiválaszthatsz egy időintervallumot a kereskedések lekéréséhez, majd azokat automatikusan küldheted egy Notion adatbázisba.

## Főbb funkciók
- Kereskedések exportálása a MetaTrader 5-ből egy kiválasztott időintervallumon belül.
- Kereskedések közvetlen küldése a Notion adatbázisba.
- Az idő konverziója New York-i időre (3 órás eltolással).
- Kereskedési adatok megjelenítése egy tiszta felületen.

## Követelmények
- **Python 3.8+**
- MetaTrader 5
- Notion API integráció
- PyQt5 (grafikus felülethez)
- MetaTrader 5 Python csomag

## Telepítés

### 1. lépés: Telepítsd a Python 3.8+ verzióját

Győződj meg róla, hogy a Python 3.8 vagy újabb verziója telepítve van. A hivatalos Python weboldalról letöltheted: [Python letöltések](https://www.python.org/downloads/)

Ellenőrizheted a Python telepítését a következő parancs futtatásával a terminálban:

```bash
python --version
```

### 2. lépés: A projekt klónozása

Klónozd a projektet a helyi gépedre:

```bash
git clone https://github.com/your-username/metatrader5-trade-exporter.git
cd metatrader5-trade-exporter
```

### 3. lépés: Függőségek telepítése

Használd a mellékelt `requirements.txt` fájlt a szükséges Python függőségek telepítéséhez:

```bash
pip install -r requirements.txt
```

Győződj meg róla, hogy a `requirements.txt` fájl a következőket (vagy hasonlókat) tartalmazza:

```txt
PyQt5
MetaTrader5
pandas
python-dotenv
pytz
requests
```

### 4. lépés: MetaTrader 5 beállítása

1. Telepítsd a **MetaTrader 5** platformot a gépedre.
2. Bizonyosodj meg róla, hogy a MetaTrader 5 megfelelően van konfigurálva és csatlakozik a bróker fiókodhoz.

Ha a MetaTrader 5 Python csomag nincs benne a `requirements.txt` fájlban, telepítsd azt a pip segítségével:

```bash
pip install MetaTrader5
```

### 5. lépés: Notion API beállítása

#### Hogyan hozz létre Notion API integrációt:

1. Nyisd meg a [Notion API oldalát](https://developers.notion.com/), és jelentkezz be a fiókodba.
2. Kattints a "My integrations" gombra a jobb felső sarokban, majd válaszd a "New integration" lehetőséget.
3. Nevezd el az integrációdat, és válaszd ki a workspace-t, amelyben használni szeretnéd. Ezután kattints a "Submit" gombra.
4. Az API kulcsodat az integráció létrehozása után fogod megkapni. Ezt az API kulcsot kell elhelyezned a `.env` fájlban az alábbi formában:

```env
NOTION_API_KEY=your_notion_api_key_here
```

#### Hogyan találhatod meg a Database ID-t:

1. Nyisd meg a Notion webes felületén az adatbázist, ahová exportálni szeretnéd a kereskedési adatokat.
2. Másold ki az adatbázis URL-jét. Az URL a következőképp fog kinézni:

   ```
   https://www.notion.so/workspace/DatabaseName-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

3. Az `xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` része az URL-nek a Database ID. Ezt az értéket helyezd a `.env` fájlban a következő sorba:

```env
NOTION_DATABASE_ID=your_notion_database_id_here
```

#### Hogyan csatolhatod az integrációt az adott adatbázishoz:

1. Nyisd meg a Notion-ben azt az adatbázist, amit használni szeretnél az exportáláshoz.
2. Kattints a jobb felső sarokban található 3 pöttyre a "New" gomb mellett.
3. A megjelenő ablakban keresd meg a Customize és az adatbázisod nevét, nyomj rá.
4. A Connactions menüpont alatt keresd az integrációdat vagy keressél rá név szerint. Ez lehet kicsit macerás! 

### 6. lépés: A program futtatása

A program futtatásához használd a következő parancsot:

```bash
python exportQT.py
```

Ez elindítja a grafikus felületet, ahol kiválaszthatod az időintervallumot és exportálhatod a kereskedéseket.

## Használat

1. **Időintervallum kiválasztása**: Használd a dátumválasztókat egy "Kezdő dátum" és egy "Befejező dátum" kiválasztásához.
2. **Kereskedések exportálása**: Kattints az "Exportálás Notion-be" gombra, hogy lekérdezd a kereskedéseket az adott időintervallumból, majd küldd őket a Notion adatbázisba.
3. **Siker/hiba visszajelzés**: Üzenetablakban kapod a visszajelzést a sikeres vagy sikertelen exportálásról.

## Hibakeresés

- Győződj meg róla, hogy a MetaTrader 5 csatlakoztatva van a brókeredhez.
- Ellenőrizd, hogy a megfelelő API kulcs és adatbázis-azonosító szerepel-e a `.env` fájlban.
- Győződj meg róla, hogy minden modul telepítve van és naprakész a `pip list` parancs segítségével.

## Licenc

Ez a projekt MIT licenc alatt van kiadva. Részletekért lásd a [LICENSE](LICENSE) fájlt.


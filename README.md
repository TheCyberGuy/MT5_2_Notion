Íme a fordítás, megőrizve a Markdown formátumot:

# MT5 to Notion Trade Exporter beállítása

Ez az útmutató végigvezet a MT5 to Notion Trade Exporter alkalmazás beállításának folyamatán, beleértve a Notion API konfigurálását és a szükséges környezeti változók beállítását.

## Követelmények

A kezdés előtt győződj meg róla, hogy a következő programok telepítve vannak a rendszeredre:

- Python 3.x
- MetaTrader 5 (MT5) telepítve és konfigurálva
- Hozzáférés a Notion API-hoz, valamint egy Notion adatbázis a kereskedési adatok tárolására
- `dotenv` és `tkcalendar` Python könyvtárak (telepítés: `pip install python-dotenv tkcalendar`)

## 1. lépés: Notion API beállítása

Ahhoz, hogy a Notionnal az API-jukon keresztül tudj kommunikálni, API kulcsot kell generálnod, és meg kell szerezned annak az adatbázisnak a **Database ID**-jét, amelybe a kereskedési adatokat szeretnéd menteni.

### 1.1 Notion integráció létrehozása (API kulcs)

1. Látogass el a [Notion Fejlesztői Oldalára](https://www.notion.so/my-integrations).
2. Kattints a **"Create New Integration"** gombra.
3. Töltsd ki a szükséges adatokat, például az integrációd nevét.
4. A létrehozás után kapni fogsz egy **"Internal Integration Token"**-t, amely az API kulcsod lesz.
5. Ezt az API kulcsot tárold biztonságosan.

### 1.2 Az adatbázis megosztása az integrációval

1. Menj a Notionba, és hozz létre egy új adatbázist (vagy használj egy meglévőt), amelyben a kereskedési adatokat szeretnéd tárolni.
2. Kattints a **Share** gombra a jobb felső sarokban.
3. Oszd meg az adatbázist az általad létrehozott **Integrációval** a nevére keresve.
4. Másold ki az **Database ID**-t az URL-ből:
   - Az adatbázis URL-je valahogy így néz ki:
     ```
     https://www.notion.so/YourWorkspace/Database-Name-158499c762eb455fb2c297ede800ae5b
     ```
   - Az utolsó `/` utáni karakterlánc a **Database ID** (`158499c762eb455fb2c297ede800ae5b` ebben a példában).

## 2. lépés: Környezeti változók beállítása

A **Notion API kulcs** és **Database ID** biztonságos tárolásához környezeti változókat kell beállítanod. Ezeket a változókat egy `.env` fájlból fogjuk betölteni.

### 2.1 `.env` fájl létrehozása

1. A projekted gyökérkönyvtárában hozz létre egy `.env` nevű fájlt.
2. Add hozzá az alábbi sorokat a fájlhoz, a helyőrző értékek helyett a saját Notion API kulcsodat és Database ID-dat használd:
   ```bash
   NOTION_API_KEY=your_notion_api_key_here
   NOTION_DATABASE_ID=your_database_id_here
   ```
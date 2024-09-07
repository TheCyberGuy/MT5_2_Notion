import MetaTrader5 as mt5
import requests
import datetime as dt
import os
from dotenv import load_dotenv
import pandas as pd
import time
import pytz

load_dotenv()

class trade():
    def __init__(self, title, ticket, position_id, symbol, side, type, size, entry_price, exit_price, profit, entry, _exit):
        self.title = str(title)
        self.ticket = ticket
        self.position_id = position_id
        self.symbol = str(symbol)
        self.side = str(side)
        self.type = str(type)
        self.size = float(size)
        self.entry_price = float(entry_price)
        self.exit_price = float(exit_price)
        self.profit = float(profit)
        self.entry = entry
        self._exit = _exit

NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

def connect_to_mt5():
    if not mt5.initialize():
        print("initialize() failed, error code =", mt5.last_error())
        quit()

def trade_exists_in_notion(position_id):
    url = f"https://api.notion.com/v1/databases/{NOTION_DATABASE_ID}/query"
    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    payload = {
        "filter": {
            "property": "Position ID",
            "number": {
                "equals": position_id
            }
        }
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        results = response.json().get('results', [])
        return len(results) > 0
    else:
        print(f"Failed to query Notion. Status code: {response.status_code}")
        return False

def convert_to_new_york_time(time):
    new_york_tz = pytz.timezone('America/New_York')

    if isinstance(time, str):
        try:
            time = dt.datetime.fromisoformat(time)
        except ValueError:
            print(f"Failed to parse datetime from string: {time}")
            return time

    if time.tzinfo is None:
        time = pytz.utc.localize(time)

    time_in_new_york = time.astimezone(new_york_tz)
    time_in_new_york = time_in_new_york - dt.timedelta(hours=3)
    return time_in_new_york

def send_to_notion(trade):
    if trade_exists_in_notion(trade.position_id):
        print(f"Trade with position ID {trade.position_id} already exists in Notion. Skipping.")
        return

    url = "https://api.notion.com/v1/pages"
    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    entry_time = convert_to_new_york_time(trade.entry)
    exit_time = convert_to_new_york_time(trade._exit)

    entry_time_iso = entry_time.isoformat()
    exit_time_iso = exit_time.isoformat()

    payload = {
        "parent": {"database_id": NOTION_DATABASE_ID},
        "properties": {
            'Name': {
                "title": [
                    {"text": {"content": f"{trade.symbol} {trade.side} {exit_time_iso}"}}
                ]
            },
            "Position ID": {"number": float(trade.position_id)},
            "Ticket": {"number": float(trade.ticket)},
            "Symbol": {"rich_text": [{"text": {"content": str(trade.symbol)}}]},
            "Deal Type": {"select": {"name": str(trade.side)}},
            "Size": {"number": float(trade.size)},
            "Entry Price": {"number": float(trade.entry_price)},
            "Exit Price": {"number": float(trade.exit_price)},
            "Profit": {"number": float(trade.profit)},
            "Trade Time": {
                "date": {
                    "start": entry_time_iso,
                    "end": exit_time_iso
                }
            },
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        print(f"Trade {trade.position_id} sent to Notion successfully")
    else:
        print(f"Failed to send trade {trade.position_id} to Notion. Status code: {response.status_code}")
        print(response.text)

def get_todays_trades(from_date, to_date):
    from_date = dt.datetime.combine(from_date, dt.datetime.min.time())
    to_date = dt.datetime.combine(to_date, dt.datetime.max.time())

    connect_to_mt5()

    deals = mt5.history_deals_get(from_date, to_date)
    if deals is None:
        print("No deals, error code=", mt5.last_error())
        return []

    print(f"Number of deals from {from_date} to {to_date}: {len(deals)}")
    if len(deals) > 0:
        print("Sample deal:", deals[0]._asdict())

    mt5.shutdown()
    return deals

def pandify_trades(deals):
    data = []
    for trade in deals:
        trade_data = {
            'ticket': trade.ticket,
            'time': pd.to_datetime(trade.time, unit='s'),
            'time_msc': trade.time_msc,
            'type': trade.type,
            'side': "Long" if trade.type == mt5.DEAL_TYPE_BUY else "Short",
            'entry': trade.entry,
            'magic': trade.magic,
            'position_id': trade.position_id,
            'reason': trade.reason,
            'volume': trade.volume,
            'price': trade.price,
            'commission': trade.commission,
            'swap': trade.swap,
            'profit': trade.profit,
            'fee': trade.fee,
            'symbol': trade.symbol,
            'comment': trade.comment,
            'external_id': trade.external_id,
        }
        data.append(trade_data)
    
    if not data:
        print("No trade data to process.")
        return pd.DataFrame()

    df = pd.DataFrame(data)
    df = df[df.type != 2]  # Exclude balance operations

    def process_trades(group):
        entry_trade = group[group['entry'] == 0].iloc[0] if not group[group['entry'] == 0].empty else None
        exit_trade = group[group['entry'] == 1].iloc[0] if not group[group['entry'] == 1].empty else None
        
        if entry_trade is None or exit_trade is None:
            return None

        return pd.Series({
            'position_id': entry_trade['position_id'],
            'symbol': entry_trade['symbol'],
            'side': entry_trade['side'],
            'entry_time': entry_trade['time'],
            'entry_price': entry_trade['price'],
            'exit_time': exit_trade['time'],
            'exit_price': exit_trade['price'],
            'volume': entry_trade['volume'],
            'profit': exit_trade['profit'],
            'commission': entry_trade['commission'] + exit_trade['commission'],
            'swap': entry_trade['swap'] + exit_trade['swap'],
        })
    
    new_df = df.groupby('position_id').apply(process_trades).reset_index(drop=True)
    new_df = new_df.dropna()
    
    return new_df

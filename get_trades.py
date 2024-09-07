import MetaTrader5 as mt5
import requests
import datetime as dt
import os
from dotenv import load_dotenv
import pandas as pd
import time

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
        # self.duration = float(duration) if duration is not None else None

# Notion API details
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
    
    entry_time = trade.entry.isoformat() if isinstance(trade.entry, dt.datetime) else str(trade.entry)
    exit_time = trade._exit.isoformat() if isinstance(trade._exit, dt.datetime) else str(trade._exit)
    
    payload = {
        "parent": {"database_id": NOTION_DATABASE_ID},
        "properties": {
            'Name': {
                "title": [
                    {
                        "text": {"content": f"{trade.symbol} {trade.side} {trade._exit}"}
                    }
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
            "Trade Time": {"date": {"start": entry_time, "end": exit_time}},
            # "Duration (seconds)": {"number": float(trade.duration) if hasattr(trade, 'duration') else None},
        }
    }
    
    payload["properties"] = {k: v for k, v in payload["properties"].items() if v is not None}

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        print(f"Trade {trade.position_id} sent to Notion successfully")
    else:
        print(f"Failed to send trade {trade.position_id} to Notion. Status code: {response.status_code}")
        print(response.text)

def get_todays_trades():
    today = dt.datetime(2024,9,2)
    to_date = dt.datetime.now()

    connect_to_mt5()

    deals = mt5.history_deals_get(today, to_date)
    if deals is None:
        print("No deals, error code=", mt5.last_error())
        return []

    print(f"Number of deals today ({today.date()}): {len(deals)}")
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
    print("DataFrame shape:", df.shape)
    print("DataFrame columns:", df.columns)

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
    new_df = new_df.dropna()  # Remove any None rows (incomplete trades)
    
    return new_df

def main():
    today_deals = get_todays_trades()
    df = pandify_trades(today_deals)

    if df.empty:
        print("No completed trades to process for today.")
        return

    trades = []
    for _, i in df.iterrows():
        # duration = (i.exit_time - i.entry_time).total_seconds()
        trades.append(
            trade(
                title=i.symbol,
                ticket=i.position_id,
                position_id=i.position_id,
                symbol=i.symbol,
                side=i.side,
                type=i.side,
                size=i.volume,
                entry_price=i.entry_price,
                exit_price=i.exit_price,
                profit=i.profit,
                entry=i.entry_time,
                _exit=i.exit_time,
                # duration=duration
            )
        )
    
    for t in trades:
        send_to_notion(t)
        time.sleep(1)

if __name__ == "__main__":
    main()
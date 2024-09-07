import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QDateEdit, QPushButton, QMessageBox
from PyQt5.QtCore import QDate
import datetime as dt
from get_trades import get_todays_trades, pandify_trades, send_to_notion, trade

class TradeFetcherUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('MetaTrader 5 Trade Exporter')

        layout = QVBoxLayout()

        # From Date picker
        self.from_date_label = QLabel('From Date:')
        self.from_date_input = QDateEdit()
        self.from_date_input.setDate(QDate.currentDate().addDays(-7))  # Default 1 week ago
        self.from_date_input.setCalendarPopup(True)

        # To Date picker
        self.to_date_label = QLabel('To Date:')
        self.to_date_input = QDateEdit()
        self.to_date_input.setDate(QDate.currentDate())
        self.to_date_input.setCalendarPopup(True)

        # Export Button
        self.export_button = QPushButton('Export Trades to Notion')
        self.export_button.clicked.connect(self.export_trades)

        layout.addWidget(self.from_date_label)
        layout.addWidget(self.from_date_input)
        layout.addWidget(self.to_date_label)
        layout.addWidget(self.to_date_input)
        layout.addWidget(self.export_button)

        self.setLayout(layout)

    def export_trades(self):
        from_date = self.from_date_input.date().toPyDate()
        to_date = self.to_date_input.date().toPyDate()

        try:
            # Pass the selected date range to get_todays_trades
            deals = get_todays_trades(from_date, to_date)
            if not deals:
                QMessageBox.information(self, 'No Trades', 'No trades found for the selected date range.')
                return

            trades_df = pandify_trades(deals)
            if trades_df.empty:
                QMessageBox.information(self, 'No Trades', 'No completed trades to process.')
                return

            for _, row in trades_df.iterrows():
                new_trade = trade(
                    title=row['symbol'],
                    ticket=row['position_id'],
                    position_id=row['position_id'],
                    symbol=row['symbol'],
                    side=row['side'],
                    type=row['side'],
                    size=row['volume'],
                    entry_price=row['entry_price'],
                    exit_price=row['exit_price'],
                    profit=row['profit'],
                    entry=row['entry_time'],
                    _exit=row['exit_time']
                )
                send_to_notion(new_trade)

            QMessageBox.information(self, 'Success', 'Trades exported to Notion successfully!')

        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Failed to export trades: {str(e)}')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TradeFetcherUI()
    window.show()
    sys.exit(app.exec_())

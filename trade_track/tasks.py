from celery import Celery
import logging
from trade_track.load import load_trade_data
from trade_track.helper_funcs import fetch_candles, evaluate_trade
import os

celery = Celery('trade_track.tasks', broker=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0'))

@celery.task(bind=True, max_retries=3, name='trade_track.tasks.process_trade')
def process_trade(self, parsed):
    try:
        symbol = parsed.get('Pair')
        start_date = parsed.get('start_date')
        end_date = parsed.get('end_date')
        entry_price = float(parsed.get('Entry Price'))
        sl = float(parsed.get('Stop-Loss'))
        tp = float(parsed.get('Target/Exit Price'))

        logging.info(f"Processing trade for {symbol} from {start_date} to {end_date}")

        period = ["1min", start_date, end_date] if start_date and end_date else ["1min"]

        candles = fetch_candles(symbol=symbol, period=period, outputsize=5)
        logging.info(f"Fetched candles for {symbol}")

        verdict, pnl = evaluate_trade(candles, entry_price, tp, sl)
        logging.info(f"Trade result for {symbol}: Verdict={verdict}, PnL={pnl}")

        if verdict not in ['win', 'loss', 'no entry']:
            raise self.retry(exc=ValueError("Unexpected verdict, retrying..."), countdown=60)

        load_trade_data({
            'Pair': symbol,
            'Verdict': verdict,
            'Entry Price': entry_price,
            'PnL': pnl
        })

    except Exception as e:
        logging.error(f"Error processing trade: {str(e)}")
        raise self.retry(exc=e, countdown=60)
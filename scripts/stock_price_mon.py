"""
  Monitor stock price change.
  If the raise/drop ratio reach the threshold, trigger an SMS msg.

  @Author: benamzing
  @ModifiedDate: 2020/04/20
"""

import easyquotation as eq
from monitor.models import StockMonitor
from monitor.models import Holiday
from monitor.models import SmsLog
import logging
import datetime
import time
from utils.sms import SmsService
from django.conf import settings
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    stream=sys.stdout
)


def get_holidays():
    try:
        holidays = Holiday.objects.all()
        return [h.date for h in holidays]
    except Exception as e:
        logging.error('Failed to get holiday: {}'.format(e))
        return []


def get_stocks(hold=True):
    try:
        stocks = StockMonitor.objects.filter(hold=hold)
        results = {}
        for s in stocks:
            results[s.code] = {
                'name': s.name,
                'raise_ratio': s.raise_ratio,
                'drop_ratio': s.drop_ratio
            }
        return results
    except Exception as e:
        logging.error('Failed to retrieve monitor list: {}'.format(str(e)))
        return {}


def count_sms_log(code, day):
    try:
        count = SmsLog.objects.filter(code=code, day=day).count()
        return count
    except Exception as e:
        logging.error('Failed to get sms log count: {}'.format(e))
        return 0


sms_service = SmsService(**settings.SMS_CONFIG)
quto = eq.use('sina')
holidays = get_holidays()


def is_trade_time(dt):
    if dt.hour in [10, 13, 14]:
        return True
    if dt.hour == 9 and dt.minute > 30:
        return True
    if dt.hour == 11 and dt.minute < 30:
        return True
    return False


def is_trade_day(dt):
    if dt.weekday() in [5, 6]:
        return False
    date = dt.strftime('%Y-%m-%d')
    if date in holidays:
        return False
    return True


def monitor():
    now = datetime.datetime.now()
    if is_trade_day(now) and is_trade_time(now):
        hold_stocks = get_stocks(hold=True)
        codes = list(hold_stocks.keys())
        result = quto.real(codes)
        for k, v in result.items():
            current_ratio = (v['now'] / v['close']) - 1
            highest_ratio = (v['high'] / v['close']) - 1
            lowest_ratio = (v['low'] / v['close']) - 1
            if current_ratio >= hold_stocks[k]['raise_ratio'] or highest_ratio >= hold_stocks[k]['raise_ratio']:
                logging.info('{}({})涨幅超过5%'.format(v['name'], k))
                action(now, k, v['name'], '涨幅超过5%')
            elif current_ratio <= 0 - hold_stocks[k]['drop_ratio'] or lowest_ratio <= 0 - hold_stocks[k]['drop_ratio']:
                logging.info('{}({})跌幅超过5%'.format(v['name'], k))
                action(now, k, v['name'], '跌幅超过5%')


def action(dt, code, name, msg):
    try:
        day = dt.strftime('%Y-%m-%d')
        t = dt.strftime('%H:%M:%S')
        count = count_sms_log(code, day)
        if count < 2:
            sms_service.send_msg(settings.SMS_RECEIVERS, settings.SMS_TEMPLATE_ID, code, '{}{}'.format(name, msg))
            log = SmsLog(day=day, time=t, code=code)
            log.save()
            logging.info('Sent sms for {} due to {}'.format(code, msg))
    except Exception as e:
        logging.error('Failed to process action for {} due to: {}'.format(code, e))


def run():
    while True:
        monitor()
        time.sleep(60)

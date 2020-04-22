"""
 SMS service
 @Author: benamazing
 @Created Date: 2020-04-21
"""

from qcloudsms_py import SmsMultiSender
from qcloudsms_py.httpclient import HTTPError
import logging


class SmsService(object):
    def __init__(self, appid, appkey, sign):
        """

        :param appid: sms appid
        :param appkey: sms appkey
        :param sign: 短信签名
        """
        self.sender = SmsMultiSender(appid, appkey)
        self.sign = sign

    def send_msg(self, tos, template_id, *params):
        """
        :param template_id: 短信模板id
        :param tos: phone number, list
        :param params: 模板的占位符值
        :return: None
        """
        if not tos:
            return None
        try:
            result = self.sender.send_with_param(86, tos, template_id, params=params, sign=self.sign)
            if result['result'] != 0:
                logging.error('Failed to send sms due to: {}'.format(result['errmsg']))
            else:
                for d in result['detail']:
                    if d['result'] != 0:
                        logging.error('Failed to send sms to {} due to: {}'.format(d['mobile'], d['errmsg']))
        except HTTPError as e:
            logging.error('Failed to send sms due to HTTPError: {}'.format(e))
        except Exception as e:
            logging.error('Failed to send sms due to Error: {}'.format(e))





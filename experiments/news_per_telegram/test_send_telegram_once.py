import os
import unittest
from unittest.mock import patch
from send_telegram_once import compose, send_once

class Tests(unittest.TestCase):
    def test_summary_and_escaped_short_label(self):
        source='<h1>시험 &amp; 뉴스</h1><h2>⑥ 오늘의 핵심 3줄</h2><p>실제 &lt;문구&gt; 보존.</p>'
        rows=[dict(company='마이크론',trailing_pe=12,forward_pe=None,collected_at_kst='test')]
        result=compose(source,rows,'https://mail.google.com/?a=1&b=2')
        self.assertIn('&lt;문구&gt;',result)
        self.assertIn('Gmail 원문 보고서 열기</a>',result)
        self.assertIn('미확인',result)
        self.assertLess(len(result),3900)
    @patch.dict(os.environ,{'TELEGRAM_TOKEN':'dummy','TELEGRAM_CHAT_ID':'123'})
    def test_one_post_and_exact_recipient(self):
        calls=[]
        class Response:
            status_code=200
            def json(self):return {'ok':True,'result':{'message_id':42,'chat':{'id':123}}}
        def post(*args,**kwargs):calls.append(kwargs);return Response()
        self.assertEqual(send_once('test',post)['message_id'],42)
        self.assertEqual(len(calls),1)
        self.assertEqual(calls[0]['json']['chat_id'],'123')
    @patch.dict(os.environ,{'TELEGRAM_TOKEN':'dummy','TELEGRAM_CHAT_ID':'123'})
    def test_timeout_does_not_retry(self):
        calls=[]
        def post(*args,**kwargs):calls.append(1);raise TimeoutError()
        with self.assertRaisesRegex(RuntimeError,'UNCONFIRMED'):
            send_once('test',post)
        self.assertEqual(len(calls),1)

if __name__ == '__main__':unittest.main()

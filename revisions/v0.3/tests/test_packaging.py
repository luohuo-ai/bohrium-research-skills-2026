import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('trace_export',ROOT/'export_development_trace.py')
exporter=importlib.util.module_from_spec(spec);spec.loader.exec_module(exporter)
TMP=ROOT/'.test-tmp';TMP.mkdir(exist_ok=True)

class TraceExportTests(unittest.TestCase):
    def test_scope_privacy_pairing_and_real_event_mapping(self):
        def row(typ,**kwargs):return {'type':'response_item','payload':{'type':typ,**kwargs}}
        events=[row('message',role='developer',content=[{'text':'SYNTHETIC PRIVATE CONTEXT'}]),
                row('message',role='user',content=[{'text':'Earlier unrelated request'}]),
                row('message',role='user',content=[{'text':'开始吧，记住我们的目标是拿高分'}]),
                row('reasoning',content=[{'text':'SYNTHETIC PRIVATE REASONING'}]),
                row('function_call',call_id='real',name='tool',arguments='actual request'),
                row('function_call_output',call_id='real',output='actual result'),
                row('function_call',call_id='echo',name='tool',arguments='dry-run command'),
                row('function_call_output',call_id='echo',output='dry_run manifest trace_steps echoed private context'),
                row('function_call',call_id='pending',name='tool',arguments='unfinished')]
        with tempfile.TemporaryDirectory(dir=TMP) as tmp:
            p=Path(tmp);source=p/'source.jsonl';target=p/'export.jsonl';audit=p/'audit.json'
            source.write_text('\n'.join(json.dumps(e,ensure_ascii=False) for e in events)+'\n',encoding='utf-8')
            summary=exporter.export(source,target,audit)
            kept=[json.loads(s) for s in target.read_text(encoding='utf-8').splitlines()]
            self.assertEqual(kept,[events[2],events[4],events[5]])
            self.assertEqual(summary['exported_events'],3)
            self.assertEqual([x['original_line'] for x in json.loads(audit.read_text(encoding='utf-8'))['source_line_map']],[3,5,6])

    def test_missing_scope_never_guessed(self):
        with tempfile.TemporaryDirectory(dir=TMP) as tmp:
            p=Path(tmp);(p/'s').write_text('{}\n',encoding='utf-8')
            with self.assertRaises(ValueError):exporter.export(p/'s',p/'out',p/'audit')


    def test_explicit_recovery_scope_excludes_earlier_public_history(self):
        def message(text):return {'type':'response_item','payload':{'type':'message','role':'user','content':[{'text':text}]}}
        records=[message('开始吧，记住我们的目标是拿高分'),message('unrelated video research'),message('recovery approval'),{'type':'response_item','payload':{'type':'message','role':'assistant','content':[{'text':'actual recovery work'}]}}]
        with tempfile.TemporaryDirectory(dir=TMP) as tmp:
            p=Path(tmp);(p/'source').write_text('\n'.join(json.dumps(x,ensure_ascii=False) for x in records)+'\n',encoding='utf-8')
            result=exporter.export(p/'source',p/'out',p/'audit',start_marker='recovery approval')
            kept=[json.loads(x) for x in (p/'out').read_text(encoding='utf-8').splitlines()]
            self.assertEqual(kept,records[2:]);self.assertEqual(result['start_line'],3)


    def test_analysis_messages_and_other_api_tokens_are_filtered(self):
        records=[{'type':'response_item','payload':{'type':'message','role':'user','content':[{'text':'开始吧，记住我们的目标是拿高分'}]}},
                 {'type':'response_item','payload':{'type':'message','role':'assistant','channel':'analysis','content':[{'text':'SYNTHETIC PRIVATE ANALYSIS'}]}},
                 {'type':'response_item','payload':{'type':'message','role':'assistant','channel':'commentary','content':[{'text':'synthetic key: '+'sk-'+'a'*32}]}}]
        with tempfile.TemporaryDirectory(dir=TMP) as tmp:
            p=Path(tmp);(p/'source').write_text('\n'.join(json.dumps(x,ensure_ascii=False) for x in records)+'\n',encoding='utf-8')
            summary=exporter.export(p/'source',p/'out',p/'audit')
            data=(p/'out').read_text(encoding='utf-8')
            self.assertNotIn('SYNTHETIC PRIVATE ANALYSIS',data)
            self.assertNotIn('sk-'+'a'*32,data)
            self.assertIn('API_TOKEN_REDACTED',data);self.assertEqual(summary['exported_events'],2)

if __name__=='__main__':unittest.main()

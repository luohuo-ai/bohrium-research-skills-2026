"""Integration checks for actual synthetic worked artifacts; not official cases."""
import importlib.util,json,os,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
TMP=ROOT/'.test-tmp';TMP.mkdir(exist_ok=True)

class WorkedExampleTests(unittest.TestCase):
    def test_worked_artifacts_keep_case_and_source_checks(self):
        for task in json.loads((ROOT/'suite-manifest.json').read_text(encoding='utf-8')):
            key=task['skill']
            with self.subTest(skill=key):
                required=['reportlab','pdfplumber'] if key=='traceable-pdf-structure' else ['rdflib'] if key=='sourced-nanopublications' else []
                if any(importlib.util.find_spec(n) is None for n in required):self.skipTest('Optional worked-example dependency missing: '+','.join(required))
                skill=ROOT/'skills'/key
                with tempfile.TemporaryDirectory(dir=TMP) as temporary:
                    out=Path(temporary)/'artifacts'
                    proc=subprocess.run([sys.executable,'-B',str(skill/'scripts/worked_example.py'),'--out',str(out)],capture_output=True,text=True,encoding='utf-8',timeout=45)
                    self.assertEqual(proc.returncode,0,proc.stderr)
                    result=json.loads((out/'result.json').read_text(encoding='utf-8'))
                    case=json.loads((skill/'examples/worked/case.json').read_text(encoding='utf-8'))
                    check=json.loads((out/'selfcheck.json').read_text(encoding='utf-8'))
                    self.assertEqual(result['case_id'],case['case_id'])
                    self.assertTrue(check['valid'],check)
                    artifact=(out/result['main_result']['artifact']).resolve()
                    self.assertTrue(artifact.is_relative_to(out.resolve()))
                    self.assertTrue(artifact.is_file() and artifact.stat().st_size>0)
                    self.assertTrue(result['sources'])
                    self.assertGreater(check['evidence']['checked_entries'],0)
                    if result['status']=='partial':self.assertTrue(result['uncertainty'])
                    if key=='verified-latex-repair':
                        build=json.loads((out/'build.json').read_text(encoding='utf-8'))
                        if build['status']=='missing_tool':self.assertNotIn('pdf',build)

if __name__=='__main__':unittest.main()

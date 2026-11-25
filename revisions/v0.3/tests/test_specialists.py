import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'shared'))
import structured_tools as st
import document_tools as dt

TEST_TMP = Path(__file__).resolve().parents[1] / '.test-tmp'
TEST_TMP.mkdir(exist_ok=True)

class StructuredTests(unittest.TestCase):
    def test_same_doi_conflict_not_silently_merged(self):
        a={'id':'a','doi':'https://doi.org/10.1234/ABC','title':'Study of cells','year':2023}
        b={'id':'b','doi':'10.1234/abc','title':'A completely different experiment','year':2024}
        report=st.deduplicate([a,b])
        self.assertEqual(len(report['records']),2)
        self.assertEqual(len(report['conflicts']),1)

    def test_same_doi_and_identity_can_group(self):
        a={'id':'a','doi':'10.1234/abc','title':'Study of cells','year':2023}
        b={**a,'id':'b','doi':'https://doi.org/10.1234/ABC'}
        result=st.deduplicate([a,b])
        self.assertEqual(len(result['records']),1)
        self.assertEqual(result['groups'][0]['member_ids'],['a','b'])

    def test_title_similarity_only_is_a_candidate(self):
        a={'id':'a','title':'Same title','year':2023,'authors':['A']}
        b={'id':'b','title':'Same title','year':2024,'authors':['B']}
        self.assertEqual(len(st.deduplicate([a,b])['records']),2)

    def test_doi_group_compares_all_members(self):
        rows=[{'id':'a','doi':'10.1234/abc','title':'Study','year':2023},
              {'id':'b','doi':'10.1234/abc','title':'Study','year':2023,'authors':['Smith']},
              {'id':'c','doi':'10.1234/abc','title':'Study','year':2023,'authors':['Lee']}]
        report=st.deduplicate(rows)
        self.assertEqual(len(report['records']),2)
        self.assertTrue(report['conflicts'])

    def test_null_doi_is_not_an_identifier(self):
        rows=[{'id':'a','doi':None,'title':'Study','year':2023},{'id':'b','doi':None,'title':'Study','year':2023}]
        self.assertEqual(len(st.deduplicate(rows)['records']),2)

    def test_empty_or_missing_collections_are_not_verified(self):
        self.assertFalse(st.deduplicate([])['valid'])
        self.assertFalse(st.validate_graph({})['valid'])
        self.assertFalse(st.lint_assertions([])['valid'])

    def test_graph_missing_endpoint_and_duplicate_ids(self):
        g={'nodes':[{'id':'a'},{'id':'a'}],'edges':[{'source':'a','target':'b','relation':'uses','evidence':['e1']}]}
        self.assertFalse(st.validate_graph(g)['valid'])

    def test_query_keeps_evidence_and_direction(self):
        g={'nodes':[{'id':'a','label':'A'},{'id':'b','label':'B'}], 'edges':[{'id':'e','source':'a','target':'b','relation':'uses','evidence':['s1:p2']}]}
        report=st.query_graph(g,'a','uses')
        self.assertEqual(report['edges'][0]['evidence'],['s1:p2'])
        self.assertEqual(st.query_graph(g,'b','uses')['edges'],[])

    def test_assertions_need_sources_and_compound_claim_review(self):
        result=st.lint_assertions([{'id':'a','assertion':'A improves X and reduces Y','subject':'A','relation':'improves','object':'X','evidence':[]}])
        self.assertFalse(result['valid'])
        self.assertTrue(result['review_flags'])

class DocumentTests(unittest.TestCase):
    def test_nonexistent_or_empty_tex_project_is_not_verified(self):
        with tempfile.TemporaryDirectory(dir=TEST_TMP) as tmp:
            self.assertFalse(dt.audit_tex(Path(tmp)/'missing')['valid'])
            self.assertFalse(dt.audit_tex(Path(tmp))['valid'])

    def test_build_into_ancestor_keeps_source_files(self):
        from unittest.mock import patch
        import subprocess
        with tempfile.TemporaryDirectory(dir=TEST_TMP) as tmp:
            out=Path(tmp);project=out/'project';project.mkdir()
            (project/'main.tex').write_text(r'\documentclass{article}\begin{document}A\end{document}',encoding='utf-8')
            seen=[]
            def compiler(command,**kwargs):
                seen.append((Path(kwargs['cwd'])/'main.tex').is_file())
                product=next(x.split('=',1)[1] for x in command if x.startswith('-output-directory='))
                (Path(product)/'main.pdf').write_bytes(b'%PDF-test')
                return subprocess.CompletedProcess(command,0,'synthetic compiler stub for copy-isolation test','')
            with patch.object(dt.shutil,'which',return_value='/mock/pdflatex'),patch.object(dt.subprocess,'run',side_effect=compiler):
                report=dt.build_tex(project,'main.tex',out,'pdflatex',3)
            self.assertEqual(report['status'],'success')
            self.assertTrue(all(seen))
    def test_tex_cross_file_labels_and_missing_references(self):
        with tempfile.TemporaryDirectory(dir=TEST_TMP) as tmp:
            p=Path(tmp)
            (p/'main.tex').write_text(r'\input{section} See \ref{known} and \ref{missing}.',encoding='utf-8')
            (p/'section.tex').write_text(r'\section{A}\label{known}',encoding='utf-8')
            report=dt.audit_tex(p)
            self.assertEqual(report['undefined_references'],['missing'])

    def test_missing_compiler_does_not_reuse_old_pdf(self):
        with tempfile.TemporaryDirectory(dir=TEST_TMP) as tmp:
            p=Path(tmp); (p/'main.tex').write_text('text',encoding='utf-8')
            out=p/'out';out.mkdir();(out/'main.pdf').write_bytes(b'old pdf')
            report=dt.build_tex(p,'main.tex',out,'definitely-absent-compiler',3)
            self.assertEqual(report['status'],'missing_tool')
            self.assertNotIn('pdf',report)

    def test_pdf_two_columns_order(self):
        try:
            import pdfplumber
            from reportlab.pdfgen import canvas
        except ImportError:
            self.skipTest('Optional PDF fixtures require pdfplumber and reportlab')
        with tempfile.TemporaryDirectory(dir=TEST_TMP) as tmp:
            p=Path(tmp)/'columns.pdf';c=canvas.Canvas(str(p),pagesize=(600,800))
            c.drawString(150,760,'A full-width document title')
            for i in range(8):
                c.drawString(40,700-i*20,f'LEFT section line {i} ends here.')
                c.drawString(330,700-i*20,f'RIGHT section line {i} ends here.')
            c.save();result=dt.extract_pdf_layout(p)
            text='\n'.join(s['text'] for s in result['segments'])
            self.assertLess(text.index('LEFT section line 7'),text.index('RIGHT section line 0'))
            self.assertTrue(all('page' in s and 'bbox' in s for s in result['segments']))

if __name__=='__main__':unittest.main()

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'shared'))
import research_tools as rt
TEST_TMP = Path(__file__).resolve().parents[1] / '.test-tmp'
TEST_TMP.mkdir(exist_ok=True)


class ResearchToolsTests(unittest.TestCase):
    def test_text_anchors_and_source_hash(self):
        with tempfile.TemporaryDirectory(dir=TEST_TMP) as tmp:
            p = Path(tmp) / 'paper.md'
            p.write_text('# Title\n\nResults were 12.5%.\nNo causality was established.\n', encoding='utf-8')
            d = rt.extract_document(p)
            self.assertEqual(d['status'], 'success')
            self.assertEqual(d['segments'][1]['line_start'], 3)
            self.assertIn('12.5%', d['segments'][1]['text'])
            self.assertEqual(len(d['sha256']), 64)

    def test_protected_facts_changed(self):
        a = r'The effect may be 12.5% [2], with $x_2=3$ and \cite{smith2024}.'
        b = r'The effect is 15.2% [3], with $x_2=4$ and \cite{smith2025}.'
        report = rt.audit_text(a, b)
        self.assertFalse(report['valid'])
        self.assertTrue(report['numeric_changes'])
        self.assertTrue(report['citation_changes'])
        self.assertTrue(report['math_changes'])
        self.assertTrue(report['semantic_review'])

    def test_spacing_numbers_and_latex_commands(self):
        self.assertTrue(rt.audit_text('Value: −2.0 ± 0.3 mg.', 'Value: −2.0 ± 0.3 mg.')['valid'])
        self.assertFalse(rt.audit_text('12 mg', '12 kg')['valid'])

    def test_edits_require_complete_unique_coverage(self):
        doc = {'segments': [{'id': 'a', 'text': 'Value 3.'}, {'id': 'b', 'text': 'Value 4.'}]}
        report = rt.audit_edits(doc, [{'id': 'a', 'after': 'Value 3.', 'reason': 'unchanged'}, {'id': 'a', 'after': 'Value 3.', 'reason': 'unchanged'}])
        self.assertFalse(report['valid'])
        self.assertEqual(report['missing_ids'], ['b'])
        self.assertEqual(report['duplicate_ids'], ['a'])

    def test_unchanged_edit_and_honest_reason(self):
        doc = {'segments': [{'id': 'a', 'text': 'The values is 3.'}]}
        report = rt.audit_edits(doc, [{'id': 'a', 'after': 'The value is 3.', 'reason': 'Correct subject number', 'change_type': 'grammar'}])
        self.assertTrue(report['valid'])
        self.assertFalse(rt.audit_edits(doc, [{'id': 'a', 'after': '3 values.'}])['valid'])

    def test_schema_nested_and_case_id(self):
        schema = {'type': 'object', 'required': ['case_id', 'items'], 'properties': {'case_id': {'type': 'string'}, 'items': {'type': 'array', 'items': {'type': 'object', 'required': ['evidence']}}}}
        self.assertTrue(rt.check_contract(schema, {'case_id': 'demo', 'items': [{'evidence': []}]})['valid'])
        self.assertFalse(rt.check_contract(schema, {'case_id': 'demo', 'items': [{}]})['valid'])

    def test_unknown_contract_never_passes(self):
        result = rt.check_contract('Return whatever fits', {'case_id': 'x'})
        self.assertFalse(result['validated'])
        self.assertFalse(result['valid'])

    def test_field_descriptions_require_original_keys(self):
        contract = {'answer': 'string', 'sources': 'array', 'uncertainty': 'explain limits'}
        self.assertFalse(rt.check_contract(contract, {'answer': 'a', 'sources': []})['valid'])

    def test_evidence_quote_must_exist(self):
        with tempfile.TemporaryDirectory(dir=TEST_TMP) as tmp:
            p=Path(tmp)/'source.txt';p.write_text('Only 12 animals were observed.',encoding='utf-8')
            doc=rt.extract_document(p)
            good={'source_id':doc['source_id'],'source_sha256':doc['sha256'],'segment_id':doc['segments'][0]['id'],'quote':'12 animals'}
            self.assertTrue(rt.check_evidence([doc],[good])['valid'])
            self.assertFalse(rt.check_evidence([doc],[{**good,'quote':'120 animals'}])['valid'])
            self.assertFalse(rt.check_evidence([doc],[{**good,'source_sha256':'stale'}])['valid'])

    def test_evidence_without_hash_is_incomplete(self):
        doc = {'source_id': 's', 'sha256': 'h', 'segments': [{'id': 'p1', 'text': 'Text.'}]}
        self.assertFalse(rt.check_evidence([doc], [{'source_id': 's', 'segment_id': 'p1', 'quote': 'Text.'}])['valid'])

    def test_unsupported_source_is_explicit(self):
        with tempfile.TemporaryDirectory(dir=TEST_TMP) as tmp:
            p = Path(tmp) / 'unknown.bin'
            p.write_bytes(b'\x00\x01')
            self.assertEqual(rt.extract_document(p)['status'], 'unsupported')

    def test_source_missing_tampered_or_unsupported_never_verified(self):
        with tempfile.TemporaryDirectory(dir=TEST_TMP) as tmp:
            p=Path(tmp)/'source.txt';p.write_text('Only 12 animals.',encoding='utf-8')
            d=rt.extract_document(p);entry={'source_id':d['source_id'],'source_sha256':d['sha256'],'segment_id':d['segments'][0]['id'],'quote':'12 animals'}
            self.assertFalse(rt.check_evidence([{**d,'path':str(p.with_name('missing.txt'))}],[entry])['valid'])
            self.assertFalse(rt.check_evidence([{**d,'status':'unsupported'}],[entry])['valid'])
            d['segments'][0]['text']='Only 120 animals.'
            self.assertFalse(rt.check_evidence([d],[{**entry,'quote':'120 animals'}])['valid'])

    def test_empty_evidence_is_not_a_positive_verification(self):
        self.assertFalse(rt.check_evidence([],[])['valid'])

    def test_chinese_adjacent_numbers_and_units(self):
        self.assertTrue(rt.audit_text('At 12 mg.','剂量为12 mg。')['valid'])
        self.assertFalse(rt.audit_text('含量为12mg。','含量为19kg。')['valid'])
        self.assertFalse(rt.audit_text('12mg剂量','12kg剂量')['valid'])

    def test_items_field_map_cannot_lose_required_key(self):
        self.assertFalse(rt.check_contract({'items':'array'},{})['valid'])

    def test_json_boolean_is_not_number_for_enum_or_const(self):
        self.assertFalse(rt.check_contract({'const':True},1)['valid'])
        self.assertFalse(rt.check_contract({'enum':[True]},1)['valid'])

    def test_union_uses_schema_interpretation_for_every_branch(self):
        self.assertTrue(rt.check_contract({'anyOf':[{'const':1},{'enum':['x']}]},'x')['valid'])
        report=rt.check_contract({'anyOf':[{'type':'object'},{'future':42}]},{})
        self.assertFalse(report['validated'])
        optional={'type':'object','properties':{'optional':{'type':'string','format':'unknown-format'}}}
        self.assertFalse(rt.check_contract(optional,{})['validated'])


if __name__ == '__main__':
    unittest.main()

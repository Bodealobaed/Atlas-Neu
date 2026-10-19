import unittest
from literature_intelligence import sanitize_query, federated_search, evidence_brief

class TestLiterature(unittest.TestCase):
    def test_privacy(self):
        for s in ['patient: John Smith', 'email@test.com', '123456789']:
            with self.assertRaises(ValueError):sanitize_query(s)
    def test_dedup_ranking(self):
        def a(q,**kw):return [{'title':'knee fracture imaging','abstract':'radiograph','doi':'10.1/a','url':'https://doi.org/10.1/a','source':'test'}, {'title':'unrelated','doi':'10.1/b','url':'https://doi.org/10.1/b','source':'test'}]
        def b(q,**kw):return [{'title':'duplicate','doi':'10.1/a','url':'https://doi.org/10.1/a','source':'test'}]
        out=federated_search('knee fracture',providers=[a,b]);self.assertEqual(len(out['records']),2)
        self.assertEqual(out['records'][0]['title'],'knee fracture imaging')
        self.assertEqual(len(evidence_brief(out['records'],'knee fracture')['candidate_topics']),1)
    def test_failure_is_explicit(self):
        import requests
        def failed(q,**kw):raise requests.Timeout()
        out=federated_search('brain MRI',providers=[failed]);self.assertEqual(len(out['provider_errors']),1)
if __name__=='__main__':unittest.main()

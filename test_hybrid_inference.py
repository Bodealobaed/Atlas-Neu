import unittest
from hybrid_inference import validate_result, infer_remote, format_findings
from PIL import Image

class HybridTests(unittest.TestCase):
    def test_rejects_no_model(self):
        with self.assertRaises(ValueError): validate_result({'findings':[{'label':'pneumonia','score':.8}]},'chest_xray')
    def test_rejects_modality_mismatch(self):
        with self.assertRaises(ValueError): validate_result({'model_card':{'model_id':'x','version':'1','task':'classification','modality':'brain_mri','license':'MIT'},'findings':[]},'chest_xray')
    def test_valid_research_result(self):
        data=validate_result({'model_card':{'model_id':'research','version':'1','task':'classification','modality':'chest_xray','license':'MIT','validated':False},'findings':[{'label':'opacity','score':0.7}]},'chest_xray')
        self.assertFalse(data['validated']);self.assertIn('Nicht klinisch validiert',format_findings(data,'German'))
    def test_consent_required(self):
        with self.assertRaises(PermissionError):infer_remote(Image.new('RGB',(10,10)),'chest_xray','https://example.org','token',False)
    def test_https_required(self):
        with self.assertRaises(ValueError):infer_remote(Image.new('RGB',(10,10)),'chest_xray','http://example.org','token',True)
if __name__=='__main__':unittest.main()

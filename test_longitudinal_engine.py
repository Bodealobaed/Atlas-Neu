import tempfile
from pathlib import Path
import pytest
from longitudinal_engine import ResearchMemory, evidence_assessment

def test_permission_review_and_retrieval():
    with tempfile.TemporaryDirectory() as directory:
        path=str(Path(directory)/'memory.sqlite3')
        memory=ResearchMemory(path)
        with pytest.raises(ValueError):
            memory.add_study('MRI knee','Medical imaging','ACL ligament','doi:1','CC BY')
        memory.add_study('MRI knee','Medical imaging','ACL ligament','doi:1','CC BY',expert_reviewed=True,permission=True)
        assert memory.retrieve('ACL ligament')[0]['title']=='MRI knee'
        assert ResearchMemory(path).retrieve('ACL ligament')
        assert memory.retrieve('unrelatedzzzz')==[]

def test_model_registry():
    with tempfile.TemporaryDirectory() as directory:
        memory=ResearchMemory(str(Path(directory)/'m.db'))
        with pytest.raises(ValueError):memory.save_model('test','Engineering','study',{'rmse':2})
        memory.save_model('test','Engineering','study',{'rmse':2},permission=True)
        assert memory.list_models('Engineering')[0]['model']['rmse']==2

def test_no_diagnostic_probability():
    assessment=evidence_assessment([{'source':'doi','reference_label':'Parkinson','visual_similarity':0.99}], [{'pmid':'1','title':'Study'}])
    assert assessment['diagnosis'] is None
    assert assessment['publication_count']==1

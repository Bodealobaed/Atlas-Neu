from pathlib import Path

def test_no_fake_numbered_chapters_or_table_appendix():
    code=Path(__file__).resolve().parents[1].joinpath('book.py').read_text()
    assert 'heading=str(ch.get(' in code
    assert "heading=f'{labels[\"chapter\"]} {i} —" not in code
    assert "story.extend([PageBreak(),P(labels['tables'],'h'),P(labels['tables'],'small')])" not in code
    assert 'Expand wording only modestly' in code

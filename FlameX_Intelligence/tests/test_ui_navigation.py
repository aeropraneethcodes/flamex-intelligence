"""Static constraints for homepage navigation and preserving scientific/data integrity."""
import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT / 'app.py').read_text(encoding='utf-8')
TREE = ast.parse(SOURCE)

def literal_assignment(name):
    for node in TREE.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in node.targets):
            return ast.literal_eval(node.value)
    raise AssertionError(f'Missing {name} assignment')

def test_all_eleven_research_destinations_preserved():
    pages = literal_assignment('PAGES')
    assert len(pages) == 11
    assert len(set(pages)) == 11
    assert {'Mission overview', 'Guided Tour', 'NASA data lab',
            'FlameIQ research assistant', 'Research brief & sources'}.issubset(pages)

def test_sidebar_labels_and_links_resolve():
    pages = set(literal_assignment('PAGES'))
    icons = literal_assignment('PAGE_ICONS')
    assert set(icons) == pages
    assert "key='active_page'" in SOURCE
    assert 'on_click=navigate_to' in SOURCE
    for page in ('Combustion explorer', 'FlameIQ research assistant',
                 'Guided Tour', 'Fuel comparison lab', 'Artemis scenario explorer'):
        assert f"args=('{page}',)" in SOURCE or f"'{page}'" in SOURCE

def test_home_spotlight_is_not_a_hardcoded_scientific_statistic():
    assert 'featured=diagnostic_data(full)' in SOURCE
    assert 'ratio=featured.get(' in SOURCE
    assert 'reference_count(full,EXPLORATION)' in SOURCE
    assert 'not a direct measurement of flame stability' in SOURCE
    assert 'team-supplied' in SOURCE

def test_original_colors_and_homepage_style_are_retained():
    assert '"#2878A5"' in (ROOT/'.streamlit/config.toml').read_text()
    assert '#F6F8FA' in (ROOT/'.streamlit/config.toml').read_text()
    assert 'hero-underlined' in SOURCE
    assert 'Reset experiment filters' in SOURCE

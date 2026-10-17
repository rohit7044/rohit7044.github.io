"""Prepare allowlisted assets; keep the supplied PDF untouched."""
from pathlib import Path
import shutil
import pymupdf as fitz

root = Path(__file__).resolve().parents[1]
out = root / 'public' / 'assets'
out.mkdir(parents=True, exist_ok=True)
source = root / 'private' / 'resume-original.pdf'
if not source.exists():
    raise SystemExit('Place the original supplied PDF at private/resume-original.pdf. This folder is ignored by Git.')
doc = fitz.open(source)
for page in doc:
    replacements = {
        'Working on State of the Art 3D-lipsync techniques for Sony Entertainment Limited': 'Research on 3D lip-sync and facial animation.',
        'Created a pipeline which provided the best facial region editing than any product in the market': 'Research on facial-region editing and identity preservation.',
        'Currently working on SOTA rendering engine for AI-lipsync': 'Research on neural rendering for facial animation.',
    }
    additions = []
    for source, replacement in replacements.items():
        for rect in page.search_for(source):
            page.add_redact_annot(rect, fill=(1, 1, 1))
            additions.append((rect, replacement))
    for link in page.get_links():
        uri = link.get('uri', '')
        if uri.startswith('tel:'):
            rect = fitz.Rect(link['from'])
            page.add_redact_annot(rect + (-10, -1, 1, 1), fill=(1, 1, 1))
            page.delete_link(link)
        elif uri.startswith('mailto:'):
            link['uri'] = 'mailto:rdas.879@gmail.com'
            page.update_link(link)
    for term in ('+91-7044168536', '7044168536'):
        for rect in page.search_for(term):
            page.add_redact_annot(rect + (-10, -1, 1, 1), fill=(1, 1, 1))
    page.apply_redactions()
    for rect, replacement in additions:
        page.insert_text((rect.x0, rect.y1 - 2), replacement, fontname='tiro', fontsize=10.5)
    # Remove hidden accessibility replacement text from the supplied document.
    # Content stream text marked /ActualText is metadata, never portfolio content.
    for xref in page.get_contents():
        import re
        stream = doc.xref_stream(xref)
        stream = re.sub(rb'/ActualText\s*(?:<[^>]*>|\((?:\\.|[^\\)])*\))', b'/ActualText ()', stream)
        doc.update_stream(xref, stream)
doc.set_metadata({})
doc.save(out / 'resume.pdf', garbage=4, deflate=True)
shutil.copyfile(out / 'resume.pdf', root / 'public' / 'Rohit Das - Deep Learning Engineer.pdf')
check = fitz.open(out / 'resume.pdf')
assert '7044168536' not in ''.join(p.get_text() for p in check)
assert not any(l.get('uri','').startswith('tel:') for p in check for l in p.get_links())
print('Prepared phone-redacted resume:', (out / 'resume.pdf').stat().st_size, 'bytes')

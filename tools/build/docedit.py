"""docedit.py -- the paragraph editor of the build kit: rep(prefix, old, new) replaces text inside the one paragraph that starts
with prefix; after(prefix, texts, like) inserts paragraphs after it in the style of another (tools/build/README.md)."""
import sys, re, os, html as _h; sys.path.insert(0, '/home/claude')
from dx import Doc
S = os.path.dirname(os.path.abspath(__file__))
def tools(D):
    def hit(prefix):
        h = [(a, b, t) for a, b, t in D.all() if t.startswith(prefix)]; assert len(h) == 1, (prefix, len(h)); return h[0]
    def put(prefix, new):
        a, b, t = hit(prefix); px = D.x[a:b]
        ppr = re.search(r'<w:pPr>.*?</w:pPr>', px, re.S); rpr = re.search(r'<w:rPr>.*?</w:rPr>', px[ppr.end() if ppr else 0:], re.S)
        op = re.match(r'<w:p[^>]*>', px).group(0)
        D.x = D.x[:a] + op + (ppr.group(0) if ppr else '') + '<w:r>' + (rpr.group(0) if rpr else '') + '<w:t xml:space="preserve">' + _h.escape(new, quote=False) + '</w:t></w:r></w:p>' + D.x[b:]
    def rep(prefix, old, new):
        a, b, t = hit(prefix); assert t.count(old) == 1, (prefix, old); put(prefix, t.replace(old, new))
    def after(prefix, texts, like=None):
        a, b, t = hit(prefix); assert D.addafter(t, texts, like=like) == 1
    return rep, after

import re, html
class Doc:
    def __init__(s, d):
        s.path=d+'/word/document.xml'; s.x=open(s.path,encoding='utf8').read(); s.n=0
    def paras(s):
        return [(m.start(),m.end()) for m in re.finditer(r'<w:p(?: [^>]*[^/>])?>.*?</w:p>', s.x, re.S)]
    @staticmethod
    def text(px):
        return html.unescape(''.join(re.findall(r'<w:t(?: [^>]*)?>(.*?)</w:t>', px, re.S)))
    def all(s):
        return [(a,b,s.text(s.x[a:b])) for a,b in s.paras()]
    def sub(s, old, new, count=0, must=True):
        """replace text inside paragraphs where the phrase lies in a single run"""
        o=html.escape(old,quote=False); n=html.escape(new,quote=False)
        c=s.x.count(o)
        if c==0:
            if must: print('MISS:',old[:90])
            return 0
        s.x=s.x.replace(o,n) if not count else s.x.replace(o,n,count); s.n+=c; return c
    def setp(s, contains, newtext, all_=False):
        """rebuild paragraph text keeping pPr and first run's rPr"""
        hits=[(a,b) for a,b,t in s.all() if contains in t]
        if not hits: print('MISS-P:',contains[:90]); return 0
        if not all_: hits=hits[:1]
        for a,b in reversed(hits):
            px=s.x[a:b]
            ppr=re.search(r'<w:pPr>.*?</w:pPr>',px,re.S); rpr=re.search(r'<w:rPr>.*?</w:rPr>',px[ppr.end() if ppr else 0:],re.S)
            op=re.match(r'<w:p[^>]*>',px).group(0)
            new=op+(ppr.group(0) if ppr else '')+('<w:r>'+(rpr.group(0) if rpr else '')+'<w:t xml:space="preserve">'+html.escape(newtext,quote=False)+'</w:t></w:r>' if newtext else '')+'</w:p>'
            s.x=s.x[:a]+new+s.x[b:]; s.n+=1
        return len(hits)
    def delp(s, contains, all_=False):
        hits=[(a,b) for a,b,t in s.all() if contains in t]
        if not hits: print('MISS-D:',contains[:90]); return 0
        if not all_: hits=hits[:1]
        for a,b in reversed(hits): s.x=s.x[:a]+s.x[b:]; s.n+=1
        return len(hits)
    def addafter(s, contains, texts, like=None):
        """insert paragraphs after the first para containing `contains`, cloning style of para containing `like` (default: same)"""
        ps=s.all(); hit=[(a,b) for a,b,t in ps if contains in t]
        if not hit: print('MISS-A:',contains[:90]); return 0
        a,b=hit[0]; src=s.x[a:b]
        if like:
            l=[(c,d) for c,d,t in ps if like in t]
            if l: src=s.x[l[0][0]:l[0][1]]
        ppr=re.search(r'<w:pPr>.*?</w:pPr>',src,re.S); rpr=re.search(r'<w:rPr>.*?</w:rPr>',src[ppr.end() if ppr else 0:],re.S)
        out=''
        for t in texts:
            out+='<w:p>'+(ppr.group(0) if ppr else '')+'<w:r>'+(rpr.group(0) if rpr else '')+'<w:t xml:space="preserve">'+html.escape(t,quote=False)+'</w:t></w:r></w:p>'
        s.x=s.x[:b]+out+s.x[b:]; s.n+=len(texts); return 1
    def save(s): open(s.path,'w',encoding='utf8').write(s.x)

def _psub(D, old, new, contains=None, all_=False):
    """run-aware replacement of `old` (plain text) inside paragraphs"""
    n=0
    for a,b in reversed(D.paras()):
        px=D.x[a:b]; t=Doc.text(px)
        if old not in t or (contains and contains not in t): continue
        ts=list(re.finditer(r'(<w:t(?: [^>]*)?>)(.*?)(</w:t>)', px, re.S))
        segs=[html.unescape(m.group(2)) for m in ts]
        while True:
            full=''.join(segs); k=full.find(old)
            if k<0: break
            e=k+len(old); pos=0; first=True
            for i,sg in enumerate(segs):
                s0,s1=pos,pos+len(sg); pos=s1
                if s1<=k or s0>=e:
                    if not (s0==s1==k and first): continue
                lo=max(k,s0)-s0; hi=min(e,s1)-s0
                segs[i]=sg[:lo]+(new if first else '')+sg[hi:]; first=False
            n+=1
            if old in new: break
        out=px
        for m,sg in reversed(list(zip(ts,segs))):
            out=out[:m.start()]+'<w:t xml:space="preserve">'+html.escape(sg,quote=False)+'</w:t>'+out[m.end():]
        D.x=D.x[:a]+out+D.x[b:]
        if not all_ and n: break
    if not n: print('MISS:',old[:100])
    D.n+=n; return n
Doc.psub=_psub

def _addbefore(D, startswith, texts):
    ps=D.all(); hit=[(a,b) for a,b,t in ps if t.startswith(startswith)]
    if not hit: print('MISS-B:',startswith); return 0
    a=hit[0][0]
    out=''.join('<w:p><w:r><w:t xml:space="preserve">'+html.escape(t,quote=False)+'</w:t></w:r></w:p>' for t in texts)
    D.x=D.x[:a]+out+D.x[a:]; D.n+=len(texts); return 1
Doc.addbefore=_addbefore

def psub_main(D, old, new, contains=None):
    """_psub restricted to paragraphs outside the embedded blocks (those starting '# =====')"""
    n=0
    for a,b in D.paras():
        px=D.x[a:b]; t=Doc.text(px)
        if t.startswith('# =====') or old not in t or (contains and contains not in t): continue
        ts=list(re.finditer(r'(<w:t(?: [^>]*)?>)(.*?)(</w:t>)', px, re.S))
        segs=[html.unescape(m.group(2)) for m in ts]
        full=''.join(segs); k=full.find(old)
        e=k+len(old); pos=0; first=True
        for i,sg in enumerate(segs):
            s0,s1=pos,pos+len(sg); pos=s1
            if s1<=k or s0>=e:
                if not (s0==s1==k and first): continue
            lo=max(k,s0)-s0; hi=min(e,s1)-s0
            segs[i]=sg[:lo]+(new if first else '')+sg[hi:]; first=False
        out=px
        for m,sg in reversed(list(zip(ts,segs))):
            out=out[:m.start()]+'<w:t xml:space="preserve">'+html.escape(sg,quote=False)+'</w:t>'+out[m.end():]
        D.x=D.x[:a]+out+D.x[b:]; n+=1
        break
    if not n: print('MISS:',old[:100])
    return n

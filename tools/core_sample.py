#!/usr/bin/env python3
"""Extract the format sample of Core Part 8.5 from the Core Specification .docx, as plain text.

Usage: python3 tools/core_sample.py [CORE.docx] > sample.txt
The sample lies between "======= BEGIN SAMPLE NAVIGATION =======" and "======= END SAMPLE NAVIGATION =======";
each paragraph is one line. The continuous integration passes the result to m193_m225.py --audit,
tools/format_check.py and tools/output_id.py --verify. Standard library only.
"""
import html, os, re, sys, zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'docs', 'Omega42_Core_Specification_V335_Rev450_STABLE.docx')
x = zipfile.ZipFile(path).read('word/document.xml').decode('utf-8')
paras = [html.unescape(''.join(re.findall(r'<w:t(?: [^>]*)?>(.*?)</w:t>', p, re.S)))
         for p in re.findall(r'<w:p(?: [^>]*[^/>])?>.*?</w:p>|<w:p/>', x, re.S)]
try:
    i = paras.index('======= BEGIN SAMPLE NAVIGATION =======')
    j = paras.index('======= END SAMPLE NAVIGATION =======')
except ValueError:
    sys.exit('sample not found in ' + path)
sys.stdout.write('\n'.join(paras[i + 1:j]) + '\n')

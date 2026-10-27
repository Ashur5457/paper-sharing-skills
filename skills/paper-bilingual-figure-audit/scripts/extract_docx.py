#!/usr/bin/env python3
"""Build a source-only translation skeleton from DOCX (no translation performed).

Exports source paragraphs, tables, ordered embedded images, and tentative
figure-caption matching. Verify every figure visually before publishing.
Requires: pip install python-docx
"""
from __future__ import annotations
import argparse
import json
import os
import pathlib
import re
import sys
from collections import defaultdict
from docx import Document
from docx.oxml.ns import qn
from docx.table import Table
from docx.text.paragraph import Paragraph

FIG = re.compile(r'^\s*(?:Fig(?:ure)?s?\.?)[\s]*([Ss]?\d+)\s*\.?[\s:–-]*(.*)', re.I)
TAB = re.compile(r'^\s*(?:Table)\s+([Ss]?\d+)\s*[.:-]?\s*(.*)', re.I)
REF = re.compile(r'^\s*(?:\[\d+\]|\d+\.\s+)[A-Z][A-Za-z ,.-]+')
HEADS = {
    'Abstract':'摘要', 'Introduction':'引言','Results and discussion':'結果與討論',
    'Results and Discussion':'結果與討論','Conclusion':'結論', 'Conclusions':'結論',
    'Experimental section':'實驗部分','Electrochemical Characterization':'電化學表徵',
    'Material characterization':'材料表徵','Preparation of the electrolytes':'電解液製備',
    'Synthesis of SPAN':'SPAN 合成','Conflict of interest':'利益衝突',
    'Acknowledgments':'致謝','Acknowledgements':'致謝', 'Figure captions':'圖說',
    'References':'參考文獻', 'Supporting Information':'補充資訊', 'TOC':'目錄圖說'
}


def para_text(p):
    """python-docx paragraph text plus limited readable OOXML equation recovery."""
    base = p.text or ''
    # OMML is often absent from p.text. Recover common fractions/variable runs.
    math_parts=[]
    for node in p._p.iter():
        if node.tag == qn('m:oMath'):
            fragments = []
            fractions = [f for f in node.iter() if f.tag == qn('m:f')]
            if fractions:
                for f in fractions:
                    num=f.find(qn('m:num'));den=f.find(qn('m:den'))
                    def tokens(n):return ''.join(t.text or '' for t in (n.iter(qn('m:t')) if n is not None else []))
                    fragments.append(tokens(num) + '/(' + tokens(den) + ')')
            else:
                fragments.append(''.join(t.text or '' for t in node.iter(qn('m:t'))))
            if any(fragments):math_parts.append(''.join(fragments))
    if math_parts:
        missing=[x for x in math_parts if x and x not in base]
        if missing:
            base=base.rstrip()+(' ' if base.strip() else '')+' '.join(missing)
    return base.strip()


def image_refs(paragraph):
    """Return r:embed ids for embedded images in paragraph, in document order."""
    ids=[]
    for blip in paragraph._p.iter():
        if blip.tag == qn('a:blip'):
            rid=blip.get(qn('r:embed'))
            if rid:ids.append(rid)
    return ids


def source_blocks(doc):
    for b in doc.element.body.iterchildren():
        if b.tag==qn('w:p'):
            yield 'paragraph', Paragraph(b, doc)
        elif b.tag==qn('w:tbl'):
            yield 'table', Table(b, doc)


def extract(src, out, assets, role):
    doc=Document(str(src));assets.mkdir(parents=True,exist_ok=True)
    sections=[];sec={'id':'source','title_en':'Source','title_zh':'', 'blocks': []};sections.append(sec)
    refs=[];figures=[];tables=[];imgs=[];captions=[];table_captions=[];all_source=[]
    current_heading='';counts=defaultdict(int);reference_mode=False
    counter=0
    for typ,obj in source_blocks(doc):
        if typ=='paragraph':
            content=para_text(obj)
            if content:
                all_source.append(content)
            for rel in image_refs(obj):
                try:
                    part=obj.part.related_parts[rel]; b=part.blob; name=str(part.partname).rsplit('/',1)[-1]
                except Exception as e:
                    print(f'WARNING image relationship {rel}: {e}',file=sys.stderr);continue
                ext=pathlib.Path(name).suffix.lower() or '.bin'
                number=len(imgs)+1
                save=assets/f'{role}_image_{number:03d}{ext}';save.write_bytes(b)
                imgs.append({'file':str(save.resolve()),'name':name,'document_order':counter})
            counter+=1
            if not content:continue
            f=FIG.match(content)
            if f and len(content)<1200 and not (not f.group(2).strip() and any(x['id']==f'Fig. {f.group(1).upper()}' for x in captions)):
                key=f'Fig. {f.group(1).upper()}'
                captions.append({'id':key,'caption_en':content,'document_order':counter,'title':f.group(2)})
                continue
            t=TAB.match(content)
            if t and len(content)<1200:
                table_captions.append({'id':f'Table {t.group(1).upper()}','title_en':content,'document_order':counter})
                continue
            if content.startswith('Theoretical Calculation—'):
                head=True
            else:
                head=(content in HEADS or obj.style.name.lower().startswith('heading') and len(content)<120)
            if head:
                trans=HEADS.get(content,'')
                sec={'id':re.sub('[^a-z0-9-]','-',content.lower())[:50].strip('-') or 'section',
                     'title_en':content,'title_zh':trans,'blocks':[]}
                sections.append(sec);current_heading=content
                continue
            if current_heading=='Acknowledgments' and ('doi.org/' in content or reference_mode):
                reference_mode=True
                refs.append({'en':content,'zh_title':''});continue
            if current_heading=='References' or re.match(r'^\[\d+\]\s+',content):
                refs.append({'en':content,'zh_title':''});continue
            n=sum(len(s['blocks']) for s in sections)+1
            b={'id':f'{role}-p{n:04d}','type':'paragraph','zh':'','en':content,'refs':[]}
            # Mentions are grounded in source, but some matching may be manually needed.
            for x in re.findall(r'(?:Fig(?:ure)?s?\.?|Table)\s*(?:S\d+|\d+)[a-z]?',content,re.I):
                x=x.replace('Figure','Fig.').replace('Fig ','Fig. ').replace('Fig..','Fig.')
                if x not in b['refs']:b['refs'].append(x)
            sec['blocks'].append(b)
        else:
            counter+=1
            rows=[[c.text.strip() for c in row.cells] for row in obj.rows]
            if not rows:continue
            ti=len(tables)+1
            prior=[c for c in table_captions if c['document_order']<counter]
            cap=prior[-1] if prior else {'id':f'Table unmapped {ti}','title_en':'Unmapped table'}
            tab={'id':cap['id'],'title_en':cap['title_en'],'title_zh':'',
                'headers_en':rows[0], 'headers_zh':['' for x in rows[0]],'rows':rows[1:]}
            if any(x['id']==tab['id'] for x in tables):tab['id']+=f'-copy{ti}'
            tables.append(tab)
    # Use sequential matching if figure count aligns with captions. For a mismatch, mark unverified.
    for i,c in enumerate(captions):
        im=imgs[i] if i<len(imgs) else None
        figures.append({'id':c['id'],'group':'si' if c['id'].startswith('Fig. S') or role=='si' else 'main',
                        'image':os.path.relpath(im['file'],out.parent) if im else None,
                        'caption_zh':'','caption_en':c['caption_en'],
                        'verified':False,
                        'source':src.name})
    extras=imgs[len(captions):]
    report={'source_file':str(src),'source_image_count':len(imgs),'figure_caption_count':len(captions),
            'table_count':len(tables),'paragraphs_for_translation':sum(len(s['blocks']) for s in sections),
            'unmapped_images':[x['file'] for x in extras],
            'warnings':['Caption-to-image matching is sequential and MUST be visually verified.',
                        'In DOCX, figure captions may be grouped at the end while actual images appear elsewhere.',
                        'Floating/shapes or externally linked images may require separate verification.',
                        'References and tracked comments may require manual classification.']}
    # Empty headings keep source English; translation of headings is required in final JSON.
    payload={'meta':{'title_zh':'','title_en':all_source[0] if all_source else src.stem,
                     'authors':'','version':src.stem,'source':src.name},
             'sections':[s for s in sections if s['blocks']],
             'figures':figures,'tables':tables,'references':refs,
             '_extraction_report':report}
    out.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2),file=sys.stderr)

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('document',type=pathlib.Path)
    ap.add_argument('--out',type=pathlib.Path,required=True)
    ap.add_argument('--assets',type=pathlib.Path,required=True)
    ap.add_argument('--role',choices=['ms','si'],required=True)
    a=ap.parse_args()
    a.out.parent.mkdir(parents=True,exist_ok=True)
    extract(a.document,a.out,a.assets,a.role)
"""Piloto Unicamp 2026. PDF e transcrições permanecem em raw/ e staging/."""
import argparse
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urlsplit
from urllib.request import Request, urlopen
import fitz

ROOT=Path(__file__).resolve().parents[1]
PILOT=ROOT/"pilot/unicamp-2026-math"
MAX_SIZE=25*1024*1024
def load(path):return json.loads(Path(path).read_text(encoding="utf-8"))

def get_pdf(url,destination):
    parsed=urlsplit(url)
    if parsed.scheme!="https" or parsed.hostname!="www.comvest.unicamp.br":
        raise ValueError("Origem não é o host oficial Comvest")
    destination.parent.mkdir(parents=True,exist_ok=True)
    temp=destination.with_suffix(".part")
    size=0
    try:
        request=Request(url,headers={"Accept":"application/pdf","User-Agent":"VestibularAberto/0.4 (piloto acadêmico)"})
        with urlopen(request,timeout=25) as source,temp.open("wb") as target:
            final=urlsplit(source.geturl())
            if final.scheme!="https" or final.hostname!="www.comvest.unicamp.br":
                raise ValueError("Redirecionamento para host não oficial")
            if source.headers.get_content_type() not in ("application/pdf","application/octet-stream"):
                raise ValueError("MIME não é PDF")
            first=True
            while chunk:=source.read(65536):
                if first and not chunk.startswith(b"%PDF-"):
                    raise ValueError("Assinatura PDF ausente")
                first=False
                size+=len(chunk)
                if size>MAX_SIZE:raise ValueError("PDF excedeu limite de 25MB")
                target.write(chunk)
        temp.replace(destination)
    finally:
        temp.unlink(missing_ok=True)

def inspect_pdf(path,expected_pages):
    if path.stat().st_size>MAX_SIZE or path.read_bytes()[:5]!=b"%PDF-":
        raise ValueError("Arquivo não é PDF permitido")
    with fitz.open(path) as pdf:
        if pdf.needs_pass:raise ValueError("PDF protegido")
        pages=len(pdf)
    if pages!=expected_pages:raise ValueError(f"Páginas divergentes: {pages}")
    return {"sha256":hashlib.sha256(path.read_bytes()).hexdigest(),
            "bytes":path.stat().st_size,"pageCount":pages}

def split_columns(page):
    box=page.rect
    middle=(box.x0+box.x1)/2
    return (page.get_text("text",sort=True,clip=fitz.Rect(box.x0,box.y0,middle,box.y1)),
            page.get_text("text",sort=True,clip=fitz.Rect(middle,box.y0,box.x1,box.y1)))

def section(text,number):
    start=re.search(r"QUEST[AÃ]O\s+"+str(int(number))+r"\b",text,re.I)
    if not start:return None
    part=text[start.end():]
    stop=re.search(r"Objetivo\s+da\s+Quest[aã]o|QUEST[AÃ]O\s+[0-9]{1,2}\b",part,re.I)
    return part[:stop.start()].strip() if stop else None

def alternatives(fragment):
    marks=list(re.finditer(r"(?<![A-Za-z0-9])([a-dA-D])\)\s*",fragment))
    if len(marks)!=4:return None
    result={}
    for i,m in enumerate(marks):
        key=m.group(1).lower()
        if key in result:return None
        end=marks[i+1].start() if i<3 else len(fragment)
        result[key]=fragment[m.end():end].strip()
    if set(result)!=set("abcd") or not all(result.values()):return None
    head=fragment[:marks[0].start()].strip()
    return {"stem":head,"choices":result} if head else None

def run(mode="probe",pdf_path=None):
    m=load(PILOT/"manifest.json")
    target=Path(pdf_path) if pdf_path else ROOT/"raw/unicamp-2026-f1-q.pdf"
    if pdf_path is None:get_pdf(m["sourceUrl"],target)
    proof=inspect_pdf(target,m["expectedPageCount"])
    result={"mode":mode,**proof,"itemsSelected":len(m["selectedQuestions"]),"itemsPublished":0}
    if mode=="extract":
        from contracts_v1 import validate_bundle
        from datetime import datetime,timezone
        data=load(PILOT/"staging-metadata-v1.json")
        doc=data["documents"][0]
        doc.update(sha256=proof["sha256"],accessStatus="accessible",
                   retrievedAt=datetime.now(timezone.utc).isoformat())
        output=ROOT/"staging/unicamp-2026-math"
        output.mkdir(parents=True,exist_ok=True)
        candidates=[]
        with fitz.open(target) as pdf:
            for metadata,q in zip(m["selectedQuestions"],data["questions"]):
                pages=metadata["physicalPages"]
                parts=[split_columns(pdf[p-1]) for p in pages]
                columns=metadata["column"]
                if columns=="left":raw=parts[0][0]
                elif columns=="right":raw=parts[0][1]
                elif columns=="left-to-right":raw="\n".join(parts[0])
                else:raw=parts[0][1]+"\n"+parts[1][0]
                text=section(raw,metadata["number"])
                parsed=alternatives(text) if text else None
                if parsed:
                    q["contentBlocks"]=[{"type":"text","text":parsed["stem"]}]
                    q["choices"]=[{"id":c,"label":c.upper(),"order":i+1,
                      "contentBlocks":[{"type":"text","text":parsed["choices"][c]}]}
                      for i,c in enumerate("abcd")]
                q["pipelineState"]="needs_review" if parsed else "blocked"
                for loc in q["sourceLocations"]:loc["sourceSha256"]=proof["sha256"]
                candidates.append({"questionId":q["id"],"rawTextCandidate":text,
                   "alternativesDetected":len(parsed["choices"]) if parsed else 0,
                   "humanReview":False,"publishable":False})
            for p in sorted({p for q in m["selectedQuestions"] for p in q["physicalPages"]}):
                pdf[p-1].get_pixmap(matrix=fitz.Matrix(1,1)).save(output/("page-"+str(p)+".png"))
        validate_bundle(data,load(ROOT/"data/taxonomy.json"))
        (output/"bundle-v1.json").write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
        (output/"candidates.json").write_text(json.dumps(candidates,ensure_ascii=False,indent=2),encoding="utf-8")
        result["perQuestion"]=[{"number":x["questionId"].split("q")[-1],"parsed":x["alternativesDetected"]==4} for x in candidates]
        result["parsedCandidates"]=sum(bool(x["alternativesDetected"]) for x in candidates)
        result["remainingHumanReview"]=len(candidates)
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return result

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--mode",choices=("probe","extract"),default="probe")
    parser.add_argument("--pdf",default=None)
    args=parser.parse_args()
    run(args.mode,args.pdf)

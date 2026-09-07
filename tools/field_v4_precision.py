from pathlib import Path
import base64, re

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'offline-downloads'

SERIES_FIX = r'''<script id="field-v4-seriesfix">
(function(){
'use strict';
if(window.__FIELD_V4_SERIESFIX__)return;window.__FIELD_V4_SERIESFIX__=true;
function firstFreeSeries(){
  if(typeof state==='undefined'||!Array.isArray(state.series))return 1;
  const used=new Set(state.series.map(s=>Number(s.seriesNo)).filter(n=>Number.isFinite(n)&&n>0));
  let n=1;while(used.has(n))n++;return n;
}
function offerFirstFree(){const e=document.getElementById('seriesNo');if(e&&!e.disabled)e.value=firstFreeSeries()}
const save=document.getElementById('saveSeriesBtn');
if(save)save.addEventListener('click',()=>setTimeout(offerFirstFree,0));
document.addEventListener('click',e=>{if(e.target&&e.target.id==='sessionTodayV4')setTimeout(offerFirstFree,0)});
document.addEventListener('change',e=>{if(e.target&&e.target.id==='sessionDateV4')setTimeout(offerFirstFree,0)});
setTimeout(offerFirstFree,0);
})();
</script>'''


def improve_brace(html: str) -> str:
    # Existing German dates are dd.mm.yyyy. English en-GB and Spanish es-ES are dd/mm/yyyy.
    # Add slash-date migration only; new sessions already use the explicit local day key.
    needle = "m=z.match(/(\\d{4})-(\\d{1,2})-(\\d{1,2})/); if(m)return `${m[1]}-${m[2].padStart(2,'0')}-${m[3].padStart(2,'0')}`;\n return localStorage.getItem(ACTIVE)||TODAY;"
    repl = "m=z.match(/(\\d{4})-(\\d{1,2})-(\\d{1,2})/); if(m)return `${m[1]}-${m[2].padStart(2,'0')}-${m[3].padStart(2,'0')}`;\n m=z.match(/(\\d{1,2})\\/(\\d{1,2})\\/(\\d{4})/); if(m)return `${m[3]}-${m[2].padStart(2,'0')}-${m[1].padStart(2,'0')}`; // slashDateV4: en-GB / es-ES\n return localStorage.getItem(ACTIVE)||TODAY;"
    if 'slashDateV4' not in html:
        if needle not in html:
            raise RuntimeError('seriesDay migration marker not found')
        html = html.replace(needle, repl, 1)
    if 'field-v4-seriesfix' not in html:
        html = html.replace('</body>', SERIES_FIX + '\n</body>', 1)
    return html


def improve_blank(html: str) -> str:
    # Pure layout change: no blank-shaft, nocking-point or tiller calculation is touched.
    html = html.replace('header{position:sticky;top:0;z-index:10;', 'header{position:static;top:auto;z-index:10;')
    return html


def patch_combo(path: Path):
    t = path.read_text(encoding='utf-8')
    mb = re.search(r"const BRACE='([^']*)';", t)
    mk = re.search(r"const BLANK='([^']*)';", t)
    if not mb or not mk:
        raise RuntimeError(f'embedded payload missing: {path}')
    brace = improve_brace(base64.b64decode(mb.group(1)).decode('utf-8'))
    blank = improve_blank(base64.b64decode(mk.group(1)).decode('utf-8'))
    brace64 = base64.b64encode(brace.encode('utf-8')).decode('ascii')
    blank64 = base64.b64encode(blank.encode('utf-8')).decode('ascii')
    # Replace from right to left so character offsets remain valid.
    replacements = sorted([(mb.start(1), mb.end(1), brace64), (mk.start(1), mk.end(1), blank64)], reverse=True)
    for a,b,v in replacements:
        t = t[:a] + v + t[b:]
    path.write_text(t, encoding='utf-8')


def patch_single(path: Path):
    path.write_text(improve_brace(path.read_text(encoding='utf-8')), encoding='utf-8')

singles = [
    OUT/'Standhoehen_Optimierer_v3_Offline_DE.html',
    OUT/'Optimizador_Fistmele_v3_Offline_ES.html',
    OUT/'Brace_Height_Optimizer_v3_Offline_EN.html',
]
combos = [
    OUT/'Bogen_Setup_Assistent_v3_Offline_DE.html',
    OUT/'Asistente_Puesta_a_Punto_v3_Offline_ES.html',
    OUT/'Bow_Setup_Assistant_v3_Offline_EN.html',
]
for p in singles: patch_single(p)
for p in combos: patch_combo(p)

# Precise regression checks: requested functions plus the tuning logic that must remain unchanged.
for p in combos:
    t = p.read_text(encoding='utf-8')
    mb = re.search(r"const BRACE='([^']*)';", t); mk = re.search(r"const BLANK='([^']*)';", t)
    assert mb and mk
    brace = base64.b64decode(mb.group(1)).decode('utf-8')
    blank = base64.b64decode(mk.group(1)).decode('utf-8')
    assert 'brace_sessions_wa_v4' in brace
    assert 'field-v4-seriesfix' in brace
    assert 'slashDateV4' in brace
    assert 'touchstart' in brace and 'touchmove' in brace
    assert 'arrowQuality' in brace or 'Pfeilqualität' in brace or 'calidad' in brace.lower()
    assert 'state.series.sort' in brace
    assert 'recommendedTiller' in blank and 'tillerHistory' in blank
    assert 'Nock' in blank or 'nock' in blank.lower()
    assert 'position:sticky;top:0;z-index:10' not in blank
    assert '© 2026 Rainer Blome' in brace and '© 2026 Rainer Blome' in blank
    assert ('Haftung' in brace or 'responsabilidad' in brace.lower() or 'liability' in brace.lower())
    assert ('Haftung' in blank or 'responsabilidad' in blank.lower() or 'liability' in blank.lower())
    print('precision OK:', p.name)

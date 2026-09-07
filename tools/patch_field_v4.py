from pathlib import Path
import base64, re, json

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'offline-downloads'

ADDON = r'''<script id="field-v4-addon">
(function(){
'use strict';
if(window.__FIELD_V4__) return; window.__FIELD_V4__=true;
const lang=(document.documentElement.lang||'de').toLowerCase().slice(0,2);
const TXT={
 de:{archive:'Ergebnisse nach Datum',today:'Heute',view:'Gespeicherten Tag anzeigen',current:'Aktuelle Aufnahme',old:'Archivansicht – zum Erfassen bitte auf „Heute“ wechseln.',noedit:'Frühere Messungen werden nur angezeigt. Zum Ändern bitte „Heute“ wählen.',zoom:'2 Finger: zoomen · im Zoom 1 Finger: verschieben · kurz tippen: markieren'},
 es:{archive:'Resultados por fecha',today:'Hoy',view:'Mostrar un día guardado',current:'Sesión actual',old:'Vista de archivo – para registrar datos nuevos seleccione «Hoy».',noedit:'Las mediciones anteriores se muestran en modo de solo lectura. Seleccione «Hoy» para modificar datos.',zoom:'2 dedos: zoom · con zoom, 1 dedo: desplazar · toque breve: marcar'},
 en:{archive:'Results by date',today:'Today',view:'Show a saved day',current:'Current session',old:'Archive view – select “Today” to record new data.',noedit:'Earlier measurements are shown read-only. Select “Today” to make changes.',zoom:'2 fingers: zoom · when zoomed, 1 finger: pan · short tap: mark'}
}[lang]||null;
if(!TXT || typeof state==='undefined' || typeof drawAll!=='function') return;

// More usable screen area: the program header no longer occupies the top while scrolling.
const st=document.createElement('style');
st.textContent=`header{position:static!important;top:auto!important}.canvasWrap{overflow:hidden!important;position:relative}.canvasWrap #photoCanvas{transform-origin:0 0;will-change:transform}.sessionArchive .row{display:flex;gap:8px;flex-wrap:wrap;align-items:end}.sessionArchive select{min-width:190px}.sessionArchive .archiveNotice{margin-top:9px}`;
document.head.appendChild(st);

// ---------- Daily sessions ----------
const ARCH='brace_sessions_wa_v4', ACTIVE='brace_active_day_wa_v4', LEGACY='brace_series_wa_v1';
const dayKey=d=>{const y=d.getFullYear(),m=String(d.getMonth()+1).padStart(2,'0'),dd=String(d.getDate()).padStart(2,'0');return `${y}-${m}-${dd}`};
const TODAY=dayKey(new Date());
let archive={}; try{archive=JSON.parse(localStorage.getItem(ARCH)||'{}')||{}}catch(e){archive={}};
let viewing=TODAY;
const clone=x=>JSON.parse(JSON.stringify(x||[]));
function seriesDay(s){
 const z=String(s&&s.date||''); let m=z.match(/(\d{1,2})\.(\d{1,2})\.(\d{4})/); if(m)return `${m[3]}-${m[2].padStart(2,'0')}-${m[1].padStart(2,'0')}`;
 m=z.match(/(\d{4})-(\d{1,2})-(\d{1,2})/); if(m)return `${m[1]}-${m[2].padStart(2,'0')}-${m[3].padStart(2,'0')}`;
 return localStorage.getItem(ACTIVE)||TODAY;
}
function mergeDay(k,arr){
 const map=new Map((archive[k]||[]).map(s=>[Number(s.seriesNo),s]));
 (arr||[]).forEach(s=>map.set(Number(s.seriesNo),s));
 archive[k]=[...map.values()].sort((a,b)=>Number(a.seriesNo)-Number(b.seriesNo));
}
function saveArchive(){try{localStorage.setItem(ARCH,JSON.stringify(archive))}catch(e){}}
(function migrate(){
 const old=Array.isArray(state.series)?state.series:[];
 if(old.length){const groups={};old.forEach(s=>{const k=seriesDay(s);(groups[k]||(groups[k]=[])).push(s)});Object.entries(groups).forEach(([k,a])=>mergeDay(k,a));}
 if(!archive[TODAY]) archive[TODAY]=[];
 saveArchive(); localStorage.setItem(ACTIVE,TODAY);
 state.series=clone(archive[TODAY]).sort((a,b)=>Number(a.seriesNo)-Number(b.seriesNo));
 localStorage.setItem(LEGACY,JSON.stringify(state.series));
})();

function syncToday(){if(viewing!==TODAY)return;state.series.sort((a,b)=>Number(a.seriesNo)-Number(b.seriesNo));archive[TODAY]=clone(state.series);saveArchive();localStorage.setItem(LEGACY,JSON.stringify(state.series));}
const originalDrawAll=drawAll;
drawAll=function(){state.series.sort((a,b)=>Number(a.seriesNo)-Number(b.seriesNo));syncToday();originalDrawAll();renderArchivePanel();};

const originalDelete=window.deleteSeries;
window.deleteSeries=function(id){
 if(viewing!==TODAY){alert(TXT.noedit);return}
 const s=state.series.find(x=>Number(x.id)===Number(id)),n=s?Number(s.seriesNo):null;
 originalDelete(id); if(n&&document.getElementById('seriesNo'))document.getElementById('seriesNo').value=n;
};
const saveBtn=document.getElementById('saveSeriesBtn');
if(saveBtn)saveBtn.addEventListener('click',e=>{if(viewing!==TODAY){e.preventDefault();e.stopImmediatePropagation();alert(TXT.noedit)}},true);

function pretty(k){const [y,m,d]=k.split('-');return `${d}.${m}.${y}`}
function setViewing(k){
 if(viewing===TODAY)syncToday(); viewing=k;
 state.series=clone(archive[k]||[]).sort((a,b)=>Number(a.seriesNo)-Number(b.seriesNo));
 const old=viewing!==TODAY;
 if(saveBtn)saveBtn.disabled=old;
 ['imageInput','cameraInput','braceHeight','seriesNo'].forEach(id=>{const e=document.getElementById(id);if(e)e.disabled=old});
 originalDrawAll(); renderArchivePanel(); window.scrollTo({top:0,behavior:'smooth'});
}
function renderArchivePanel(){
 let box=document.getElementById('sessionArchiveV4');
 if(!box){
  box=document.createElement('section');box.id='sessionArchiveV4';box.className='card sessionArchive';
  const anchor=document.getElementById('bestResult');if(anchor&&anchor.parentElement)anchor.parentElement.parentNode.insertBefore(box,anchor.parentElement);
 }
 const dates=Object.keys(archive).filter(k=>(archive[k]||[]).length||k===TODAY).sort().reverse();
 box.innerHTML=`<h2>${TXT.archive}</h2><div class="row"><div><label>${TXT.view}</label><select id="sessionDateV4">${dates.map(k=>`<option value="${k}" ${k===viewing?'selected':''}>${k===TODAY?TXT.today+' – ':''}${pretty(k)} (${(archive[k]||[]).length})</option>`).join('')}</select></div><button type="button" class="secondary" id="sessionTodayV4">${TXT.today}</button></div><div class="status ${viewing===TODAY?'':'warn'} archiveNotice">${viewing===TODAY?TXT.current:TXT.old}</div>`;
 box.querySelector('#sessionDateV4').onchange=e=>setViewing(e.target.value);
 box.querySelector('#sessionTodayV4').onclick=()=>setViewing(TODAY);
}

// ---------- Reliable two-finger zoom on the arrow photo ----------
const canvas=document.getElementById('photoCanvas'), wrap=canvas&&canvas.closest('.canvasWrap');
if(canvas&&wrap&&typeof screenToCanvas==='function'){
 const z={scale:1,tx:0,ty:0,pinch:false,pan:false,moved:false,lastX:0,lastY:0,startDist:0,startScale:1,anchorX:0,anchorY:0,suppressUntil:0};
 const apply=()=>{canvas.style.transform=`translate(${z.tx}px,${z.ty}px) scale(${z.scale})`};
 const reset=()=>{z.scale=1;z.tx=0;z.ty=0;apply()};
 function localMid(a,b){const r=wrap.getBoundingClientRect();return{x:(a.clientX+b.clientX)/2-r.left,y:(a.clientY+b.clientY)/2-r.top}}
 function markAt(x,y){
  if(!state.image)return;const p=screenToCanvas({clientX:x,clientY:y});
  if(state.mode&&state.mode.startsWith('calib')){if(state.calib.length>=2)state.calib=[];state.calib.push(p);state.mode=state.calib.length===1?'calib2':'arrows'}
  else{const max=Number(document.getElementById('arrowsPerEnd').value||6);if(state.arrows.length<max)state.arrows.push(p);else if(typeof setStatus==='function')setStatus(lang==='es'?`Ya hay ${max} flechas marcadas.`:lang==='en'?`${max} arrows are already marked.`:`Bereits ${max} Pfeile markiert.`,true)}
  drawPhoto();
 }
 canvas.addEventListener('click',e=>{if(Date.now()<z.suppressUntil){e.preventDefault();e.stopImmediatePropagation()}},true);
 canvas.addEventListener('touchstart',e=>{
  if(e.touches.length===2){e.preventDefault();z.pinch=true;z.pan=false;z.moved=true;const a=e.touches[0],b=e.touches[1],m=localMid(a,b);z.startDist=Math.hypot(b.clientX-a.clientX,b.clientY-a.clientY);z.startScale=z.scale;z.anchorX=(m.x-z.tx)/z.scale;z.anchorY=(m.y-z.ty)/z.scale;}
  else if(e.touches.length===1&&z.scale>1.001){e.preventDefault();z.pan=true;z.moved=false;z.lastX=e.touches[0].clientX;z.lastY=e.touches[0].clientY;}
 },{passive:false,capture:true});
 canvas.addEventListener('touchmove',e=>{
  if(e.touches.length===2&&z.pinch){e.preventDefault();const a=e.touches[0],b=e.touches[1],m=localMid(a,b),d=Math.hypot(b.clientX-a.clientX,b.clientY-a.clientY),ns=Math.max(1,Math.min(6,z.startScale*d/Math.max(1,z.startDist)));z.scale=ns;z.tx=m.x-z.anchorX*ns;z.ty=m.y-z.anchorY*ns;apply();}
  else if(e.touches.length===1&&z.scale>1.001&&z.pan){e.preventDefault();const t=e.touches[0],dx=t.clientX-z.lastX,dy=t.clientY-z.lastY;if(Math.hypot(dx,dy)>2)z.moved=true;z.tx+=dx;z.ty+=dy;z.lastX=t.clientX;z.lastY=t.clientY;apply();}
 },{passive:false,capture:true});
 canvas.addEventListener('touchend',e=>{
  if(z.pinch){z.suppressUntil=Date.now()+700;if(e.touches.length<2)z.pinch=false;return}
  if(z.scale>1.001&&z.pan&&e.touches.length===0){e.preventDefault();z.suppressUntil=Date.now()+700;const t=e.changedTouches&&e.changedTouches[0];if(t&&!z.moved)markAt(t.clientX,t.clientY);z.pan=false;}
 },{passive:false,capture:true});
 // Reset zoom automatically when a new photo is loaded or markings are reset.
 ['imageInput','cameraInput','resetPointsBtn'].forEach(id=>{const e=document.getElementById(id);if(e)e.addEventListener('change',reset);if(e&&id==='resetPointsBtn')e.addEventListener('click',reset)});
 const hint=document.createElement('p');hint.className='hint';hint.textContent=TXT.zoom;wrap.insertAdjacentElement('afterend',hint);
}

// Ensure the current day is shown after the addon has migrated the data.
drawAll();
})();
</script>'''


def patch_brace_html(html):
    if 'field-v4-addon' in html:
        return html
    return html.replace('</body>', ADDON + '\n</body>')


def patch_combo(path: Path):
    t=path.read_text(encoding='utf-8')
    # Patch embedded brace-height app only; bare-shaft/tiller logic is intentionally untouched.
    m=re.search(r"const BRACE='([^']*)';",t)
    if not m:
        raise RuntimeError(f'BRACE payload not found in {path}')
    brace=base64.b64decode(m.group(1)).decode('utf-8')
    brace=patch_brace_html(brace)
    b64=base64.b64encode(brace.encode('utf-8')).decode('ascii')
    t=t[:m.start(1)]+b64+t[m.end(1):]
    # Outer combined-app header must not permanently consume the top of the iPad screen.
    t=t.replace('position:sticky;top:0;z-index:20','position:static;top:auto;z-index:20')
    if '.phaseActive>header' not in t:
        t=t.replace('</style>', '.phaseActive>header{display:none}.phaseActive main{padding:4px}.phaseActive #phase1,.phaseActive #phase2{padding:5px;border:0;box-shadow:none;margin:0}.phaseActive #phase1>h2,.phaseActive #phase2>h2{font-size:15px;margin:2px 0 5px}.phaseActive iframe{height:calc(100vh - 95px);min-height:650px}\n</style>',1)
    t=t.replace("function showOverview(){document.getElementById('overview')", "function showOverview(){document.body.classList.remove('phaseActive');document.getElementById('overview')")
    t=t.replace("function showPhase(n){document.getElementById('overview')", "function showPhase(n){document.body.classList.add('phaseActive');document.getElementById('overview')")
    path.write_text(t,encoding='utf-8')


def patch_single(path: Path):
    path.write_text(patch_brace_html(path.read_text(encoding='utf-8')),encoding='utf-8')

singles=[
 OUT/'Standhoehen_Optimierer_v3_Offline_DE.html',
 OUT/'Optimizador_Fistmele_v3_Offline_ES.html',
 OUT/'Brace_Height_Optimizer_v3_Offline_EN.html',
]
combos=[
 OUT/'Bogen_Setup_Assistent_v3_Offline_DE.html',
 OUT/'Asistente_Puesta_a_Punto_v3_Offline_ES.html',
 OUT/'Bow_Setup_Assistant_v3_Offline_EN.html',
]
for p in singles: patch_single(p)
for p in combos: patch_combo(p)

# Sanity checks: preserve key original features and verify new functions are present.
for p in combos:
    t=p.read_text(encoding='utf-8')
    assert 'const BLANK=' in t, p
    assert 'field-v4-addon' not in t  # addon is inside base64 BRACE payload
    m=re.search(r"const BRACE='([^']*)';",t); b=base64.b64decode(m.group(1)).decode('utf-8')
    for needle in ['Pfeilqualität' if '_DE.' in p.name else ('calidad' if '_ES.' in p.name else 'Arrow')]:
        assert needle.lower() in b.lower(), (p,needle)
    assert 'brace_sessions_wa_v4' in b
    assert 'touchstart' in b and 'touchmove' in b
    assert 'state.series.sort' in b
    assert '.phaseActive>header' in t
    print('patched',p.name,len(t))

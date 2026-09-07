from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]

CFG = {
    'index.html': dict(
        date_label='Messdatum', today='Heute',
        zoom='1 Finger: Pfeil markieren · 2 Finger: zoomen · bei Zoom mit 1 Finger verschieben',
    ),
    'standhoehe-es/index.html': dict(
        date_label='Fecha de medición', today='Hoy',
        zoom='1 dedo: marcar flecha · 2 dedos: ampliar · con zoom, mover con 1 dedo',
    ),
    'brace-height-en/index.html': dict(
        date_label='Measurement date', today='Today',
        zoom='1 finger: mark arrow · 2 fingers: zoom · when zoomed, pan with 1 finger',
    ),
}

SESSION_JS = r'''
const SESSION_STORE="brace_sessions_by_date_v2";
const LEGACY_SERIES_KEY="brace_series_wa_v1";
function localDateKey(d=new Date()){const y=d.getFullYear(),m=String(d.getMonth()+1).padStart(2,"0"),day=String(d.getDate()).padStart(2,"0");return `${y}-${m}-${day}`}
let sessionDate=localDateKey();
let sessions={};
try{sessions=JSON.parse(localStorage.getItem(SESSION_STORE)||"{}")||{}}catch(e){sessions={}}
if(!Object.keys(sessions).length){
  try{const legacy=JSON.parse(localStorage.getItem(LEGACY_SERIES_KEY)||"[]");if(Array.isArray(legacy)&&legacy.length)sessions[sessionDate]=legacy}catch(e){}
}
state.series=Array.isArray(sessions[sessionDate])?[...sessions[sessionDate]]:[];
function firstMissingSeriesNo(){const used=new Set(state.series.map(s=>Number(s.seriesNo)).filter(Number.isFinite));let n=1;while(used.has(n))n++;return n}
function refreshSessionDates(){
  const sel=$("sessionDate");if(!sel)return;
  const dates=Array.from(new Set([localDateKey(),sessionDate,...Object.keys(sessions)])).sort().reverse();
  sel.innerHTML=dates.map(d=>`<option value="${d}">${d}</option>`).join("");sel.value=sessionDate;
}
function persistSeries(){
  state.series.sort((a,b)=>Number(a.seriesNo)-Number(b.seriesNo));
  sessions[sessionDate]=state.series;
  localStorage.setItem(SESSION_STORE,JSON.stringify(sessions));
  localStorage.setItem(LEGACY_SERIES_KEY,JSON.stringify(state.series));
  refreshSessionDates();
}
function switchSession(d){
  if(!d)return;persistSeries();sessionDate=d;
  state.series=Array.isArray(sessions[d])?[...sessions[d]]:[];
  state.series.sort((a,b)=>Number(a.seriesNo)-Number(b.seriesNo));
  state.image=null;state.calib=[];state.arrows=[];state.mode="calib1";
  $("seriesNo").value=firstMissingSeriesNo();
  resetPhotoZoom();refreshSessionDates();drawAll();
}
'''

ZOOM_JS = r'''
const photoView={zoom:1,baseW:0,baseH:0,pinch:false,moved:false,startX:0,startY:0,lastX:0,lastY:0,startDist:0,startZoom:1,anchorX:0,anchorY:0,tapX:0,tapY:0};
function resetPhotoZoom(){
  const c=$("photoCanvas"),w=$("photoViewport");if(!c||!w)return;
  photoView.zoom=1;w.scrollLeft=0;w.scrollTop=0;
  const bw=Math.max(1,Math.min(c.width||1,w.clientWidth||c.width||1));photoView.baseW=bw;photoView.baseH=bw*(c.height||1)/(c.width||1);
  c.style.width=photoView.baseW+"px";c.style.height=photoView.baseH+"px";
}
function setPhotoZoom(z,clientX,clientY){
  const c=$("photoCanvas"),w=$("photoViewport");if(!c||!w)return;
  const old=photoView.zoom||1,nz=Math.max(1,Math.min(8,z));const r=w.getBoundingClientRect();
  const lx=clientX-r.left,ly=clientY-r.top;const ax=(w.scrollLeft+lx)/old,ay=(w.scrollTop+ly)/old;
  photoView.zoom=nz;c.style.width=(photoView.baseW*nz)+"px";c.style.height=(photoView.baseH*nz)+"px";
  w.scrollLeft=Math.max(0,ax*nz-lx);w.scrollTop=Math.max(0,ay*nz-ly);
}
function addPhotoPoint(clientX,clientY){
  if(!state.image)return;let p=screenToCanvas({clientX,clientY});
  if(state.mode.startsWith("calib")){if(state.calib.length>=2)state.calib=[];state.calib.push(p);state.mode=state.calib.length===1?"calib2":"arrows"}
  else{let max=Number($("arrowsPerEnd").value||6);if(state.arrows.length<max)state.arrows.push(p);else setStatus(`Bereits ${max} Pfeile markiert.`,true)}
  drawPhoto();
}
function installPhotoGestures(){
  const c=$("photoCanvas"),w=$("photoViewport");if(!c||!w||c.dataset.gestures)return;c.dataset.gestures="1";
  c.addEventListener("touchstart",e=>{e.preventDefault();photoView.moved=false;
    if(e.touches.length===2){photoView.pinch=true;const a=e.touches[0],b=e.touches[1];photoView.startDist=Math.hypot(b.clientX-a.clientX,b.clientY-a.clientY);photoView.startZoom=photoView.zoom;}
    else if(e.touches.length===1){photoView.pinch=false;const t=e.touches[0];photoView.startX=photoView.lastX=photoView.tapX=t.clientX;photoView.startY=photoView.lastY=photoView.tapY=t.clientY;}
  },{passive:false});
  c.addEventListener("touchmove",e=>{e.preventDefault();
    if(e.touches.length===2){photoView.pinch=true;photoView.moved=true;const a=e.touches[0],b=e.touches[1],d=Math.hypot(b.clientX-a.clientX,b.clientY-a.clientY),mx=(a.clientX+b.clientX)/2,my=(a.clientY+b.clientY)/2;setPhotoZoom(photoView.startZoom*d/Math.max(1,photoView.startDist),mx,my);}
    else if(e.touches.length===1&&photoView.zoom>1){const t=e.touches[0],dx=t.clientX-photoView.lastX,dy=t.clientY-photoView.lastY;if(Math.hypot(t.clientX-photoView.startX,t.clientY-photoView.startY)>6)photoView.moved=true;w.scrollLeft-=dx;w.scrollTop-=dy;photoView.lastX=t.clientX;photoView.lastY=t.clientY;}
  },{passive:false});
  c.addEventListener("touchend",e=>{e.preventDefault();if(e.touches.length===0){if(!photoView.pinch&&!photoView.moved)addPhotoPoint(photoView.tapX,photoView.tapY);photoView.pinch=false;photoView.moved=false;}},{passive:false});
}
'''

for rel, txt in CFG.items():
    p = ROOT / rel
    t = p.read_text(encoding='utf-8')
    original = t

    # Do not stack the patch on itself.
    if 'brace_sessions_by_date_v2' in t:
        print('already patched:', rel)
        continue

    # No fixed header while entering/marking data.
    t = t.replace('header{position:sticky;top:0;z-index:5;', 'header{position:static;z-index:5;')

    # Photo viewport: allow the canvas to grow beyond the viewport for pinch zoom.
    t = t.replace('<div class="canvasWrap"><canvas id="photoCanvas"', '<div class="canvasWrap" id="photoViewport"><canvas id="photoCanvas"')
    t = t.replace('#photoCanvas{display:block;max-width:100%;height:auto;', '#photoCanvas{display:block;max-width:none;height:auto;')

    # Extra small date/session controls.
    marker = '<canvas id="chartCanvas"'
    session_html = f'''<div class="row noPrint" style="margin:0 0 10px"><div style="min-width:220px;flex:1"><label>{txt['date_label']}</label><select id="sessionDate"></select></div><button class="secondary" id="goToday" type="button">{txt['today']}</button></div>\n'''
    if marker not in t:
        raise RuntimeError(f'chart marker missing: {rel}')
    t = t.replace(marker, session_html + marker, 1)

    # Gesture hint directly at the photo.
    vp_end = '</div>\n<p class="hint">'
    t = t.replace(vp_end, f'</div>\n<p class="hint"><b>{txt["zoom"]}</b></p>\n<p class="hint">', 1)

    # Add dated-session storage immediately after state declaration.
    state_pat = re.compile(r'(const state=\{image:null,mode:"calib1",calib:\[\],arrows:\[\],series:JSON\.parse\(localStorage\.getItem\("brace_series_wa_v1"\)\|\|"\[\]"\),settings:JSON\.parse\(localStorage\.getItem\("brace_settings_wa_v1"\)\|\|"\{\}"\)\};)')
    t, n = state_pat.subn(r'\1\n' + SESSION_JS, t, count=1)
    if n != 1:
        raise RuntimeError(f'state marker missing: {rel}')

    # Add gesture code after coordinate mapping function.
    screen_pat = re.compile(r'(function screenToCanvas\(e\)\{.*?\})\n(function targetDiameterCm)', re.S)
    t, n = screen_pat.subn(r'\1\n' + ZOOM_JS + r'\n\2', t, count=1)
    if n != 1:
        raise RuntimeError(f'screenToCanvas marker missing: {rel}')

    # Photo load resets zoom, installs gestures and leaves all calculation logic untouched.
    t = t.replace('state.image=img;state.calib=[];state.arrows=[];state.mode="calib1";drawPhoto();setTimeout(drawPhoto,100)',
                  'state.image=img;state.calib=[];state.arrows=[];state.mode="calib1";resetPhotoZoom();installPhotoGestures();drawPhoto();setTimeout(()=>{resetPhotoZoom();drawPhoto()},100)')

    # Replace the old click handler with the common point-adder. Mouse remains supported.
    old_click = '$("photoCanvas").addEventListener("click",e=>{if(!state.image)return;let p=screenToCanvas(e);if(state.mode.startsWith("calib")){if(state.calib.length>=2)state.calib=[];state.calib.push(p);state.mode=state.calib.length===1?"calib2":"arrows"}else{let max=Number($("arrowsPerEnd").value||6);if(state.arrows.length<max)state.arrows.push(p);else setStatus(`Bereits ${max} Pfeile markiert.`,true)}drawPhoto()});'
    if old_click in t:
        t = t.replace(old_click, '$("photoCanvas").addEventListener("click",e=>{if(e.detail===0)return;addPhotoPoint(e.clientX,e.clientY)});installPhotoGestures();')
    else:
        # Translated versions keep the same logic but may have translated messages.
        t = re.sub(r'\$\("photoCanvas"\)\.addEventListener\("click",e=>\{if\(!state\.image\)return;let p=screenToCanvas\(e\);.*?drawPhoto\(\)\}\);',
                   '$("photoCanvas").addEventListener("click",e=>{if(e.detail===0)return;addPhotoPoint(e.clientX,e.clientY)});installPhotoGestures();', t, count=1, flags=re.S)

    # Robust series ordering and fill the first free series number after save.
    t = t.replace('let idx=state.series.findIndex(s=>s.seriesNo===entry.seriesNo);', 'let idx=state.series.findIndex(s=>Number(s.seriesNo)===Number(entry.seriesNo));')
    t = t.replace('state.series.sort((a,b)=>a.seriesNo-b.seriesNo);', 'state.series.sort((a,b)=>Number(a.seriesNo)-Number(b.seriesNo));')
    t = t.replace('$("seriesNo").value=Number($("seriesNo").value||1)+1;', '$("seriesNo").value=firstMissingSeriesNo();')

    # Every series write now also updates the dated archive.
    t = t.replace('localStorage.setItem("brace_series_wa_v1",JSON.stringify(state.series));', 'persistSeries();')
    t = t.replace('localStorage.removeItem("brace_series_wa_v1");', 'persistSeries();')

    # Deleting a series immediately offers exactly that number again.
    t = re.sub(r'window\.deleteSeries=id=>\{state\.series=state\.series\.filter\(s=>s\.id!==id\);persistSeries\(\);drawAll\(\)\}',
               'window.deleteSeries=id=>{const old=state.series.find(s=>s.id===id);state.series=state.series.filter(s=>s.id!==id);persistSeries();if(old)$("seriesNo").value=Number(old.seriesNo)||firstMissingSeriesNo();drawAll()}', t)

    # Always render the overview in series-number order.
    t = t.replace('function renderTable(){let b=best();', 'function renderTable(){state.series.sort((a,b)=>Number(a.seriesNo)-Number(b.seriesNo));let b=best();')

    # Date selector actions and today's fresh start. Settings (including archer/bow) remain untouched.
    init_marker = 'restoreSettings();drawAll();'
    init_code = '''restoreSettings();refreshSessionDates();if($("sessionDate"))$("sessionDate").onchange=e=>switchSession(e.target.value);if($("goToday"))$("goToday").onclick=()=>switchSession(localDateKey());$("seriesNo").value=firstMissingSeriesNo();resetPhotoZoom();drawAll();'''
    if init_marker not in t:
        raise RuntimeError(f'init marker missing: {rel}')
    t = t.replace(init_marker, init_code, 1)

    t = t.replace('content="2026-08-25-r2-arrow-quality"', 'content="2026-09-07-field-v4"')

    if t == original:
        raise RuntimeError(f'no changes made: {rel}')
    p.write_text(t, encoding='utf-8')
    print('patched:', rel)

# Remove sticky top bars from all three bare-shaft apps as well; no other tuning logic is changed.
for rel in ['blankschaft-tuner-v261/index.html','blankschaft-tuner-es/index.html','bare-shaft-tuner-en/index.html']:
    p=ROOT/rel
    if not p.exists():
        print('missing optional:',rel);continue
    t=p.read_text(encoding='utf-8')
    t=t.replace('header{position:sticky;top:0;z-index:10;', 'header{position:static;z-index:10;')
    p.write_text(t,encoding='utf-8')
    print('header made non-sticky:',rel)

# The combined offline assistant must not add its own fixed top bar above Phase 1/2.
bp=ROOT/'tools'/'build_offline.py'
b=bp.read_text(encoding='utf-8')
b=b.replace('header{{padding:14px 16px;background:#fff;border-bottom:1px solid var(--line);position:sticky;top:0;z-index:20}}',
            'header{{padding:10px 16px;background:#fff;border-bottom:1px solid var(--line);position:static;z-index:20}}')
bp.write_text(b,encoding='utf-8')
print('patched combo generator header')

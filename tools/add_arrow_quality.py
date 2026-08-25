from pathlib import Path
import re, json

configs = {
    'index.html': {
        'section':'<section class="card"><h2>5. Pfeilqualität</h2><p class="hint">Die Bewertung vergleicht jeden nummerierten Pfeil über alle Serien anhand seines mittleren Abstands zum Mittelpunkt der fünf gewerteten Pfeile. Einen Pfeil antippen, um sein Trefferbild über alle Serien zu sehen. Eine Serie in der Übersicht antippen, um das komplette Serien-Trefferbild zu öffnen.</p><div id="arrowQualityWrap"></div></section>',
        'title_arrow':'Pfeil {n} – Trefferbild über alle Serien','title_series':'Serie {n} – Trefferbild',
        'no_data':'Für die Pfeilbewertung bitte neue Serien mit dieser Version aufnehmen. Ältere gespeicherte Serien enthalten noch keine Einzelpositionen.',
        'arrow':'Pfeil','rank':'Rang','avg':'Ø Abstand','outliers':'Ausreißer','series':'Serie','brace':'Standhöhe','discarded':'gestrichen','close':'Schließen',
        'best':'sehr konstant','good':'gut','neutral':'unauffällig','watch':'auffällig','check':'prüfen','center':'Mittelpunkt der gewerteten Pfeile','left':'links','right':'rechts','up':'oben','down':'unten'
    },
    'standhoehe-es/index.html': {
        'section':'<section class="card"><h2>5. Calidad de las flechas</h2><p class="hint">La evaluación compara cada flecha numerada a lo largo de todas las tandas mediante su distancia media al centro de las cinco flechas valoradas, después de descartar el impacto atípico. Toque una flecha para ver su patrón de impactos en todas las tandas. Toque una tanda en el resumen para ver el patrón completo de esa tanda.</p><div id="arrowQualityWrap"></div></section>',
        'title_arrow':'Flecha {n} – patrón de impactos en todas las tandas','title_series':'Tanda {n} – patrón de impactos',
        'no_data':'Para evaluar las flechas, registre nuevas tandas con esta versión. Las tandas guardadas anteriormente todavía no contienen las posiciones individuales.',
        'arrow':'Flecha','rank':'Puesto','avg':'Distancia media','outliers':'Descartes','series':'Tanda','brace':'Fistmele','discarded':'descartada','close':'Cerrar',
        'best':'muy constante','good':'buena','neutral':'normal','watch':'llamativa','check':'revisar','center':'Centro de las flechas valoradas','left':'izquierda','right':'derecha','up':'arriba','down':'abajo'
    },
    'brace-height-en/index.html': {
        'section':'<section class="card"><h2>5. Arrow quality</h2><p class="hint">The evaluation compares each numbered arrow across all ends using its mean distance from the centre of the five scored arrows after the outlier has been discarded. Tap an arrow to view its impact pattern across all ends. Tap an end in the overview to view the complete impact pattern for that end.</p><div id="arrowQualityWrap"></div></section>',
        'title_arrow':'Arrow {n} – impact pattern across all ends','title_series':'End {n} – impact pattern',
        'no_data':'To evaluate individual arrows, record new ends with this version. Previously saved ends do not yet contain the individual impact positions.',
        'arrow':'Arrow','rank':'Rank','avg':'Mean distance','outliers':'Outliers','series':'End','brace':'Brace height','discarded':'discarded','close':'Close',
        'best':'very consistent','good':'good','neutral':'normal','watch':'noticeable','check':'check','center':'Centre of scored arrows','left':'left','right':'right','up':'up','down':'down'
    }
}

css = '''
.arrowQualityGrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(155px,1fr));gap:9px;margin-top:10px}.arrowQualityCard{border:1px solid var(--line);border-radius:12px;padding:10px;background:#fafcfe}.arrowQualityCard button{width:100%;text-align:left;background:#e9eef6;color:#183452}.arrowQualityCard b{display:block;font-size:17px;margin-bottom:3px}.arrowQualityCard .small{display:block;font-size:12px;color:var(--muted);margin-top:4px}.seriesClick{cursor:pointer}.seriesClick:hover{background:#f5f8fc}.detailOverlay{position:fixed;inset:0;z-index:1000;background:#0009;display:flex;align-items:center;justify-content:center;padding:14px}.detailOverlay.hidden{display:none}.detailPanel{width:min(880px,96vw);max-height:94vh;overflow:auto;background:#fff;border-radius:16px;padding:14px;box-shadow:0 12px 44px #0007}.detailPanel h2{margin-right:80px}.detailCanvasWrap{border:1px solid var(--line);border-radius:12px;overflow:auto;background:#fff}.detailCanvasWrap canvas{display:block;width:100%;height:auto;background:#fff}.detailTop{display:flex;justify-content:space-between;gap:10px;align-items:flex-start}.detailTop button{flex:0 0 auto}.detailText{margin-top:10px;color:var(--muted);font-size:13px}
'''

helper_template = r'''
const AQTXT=__AQTXT__;
function buildArrowMetrics(points,dropIndex){
  const sc=scaleCmPerPx();if(!sc||!points.length)return [];
  const ref=points.filter((_,i)=>i!==dropIndex),base=ref.length?ref:points;
  const cx=base.reduce((s,p)=>s+p.x,0)/base.length,cy=base.reduce((s,p)=>s+p.y,0)/base.length;
  return points.map((p,i)=>{const x=(p.x-cx)*sc*10,y=(p.y-cy)*sc*10;return{arrow:i+1,xMm:x,yMm:y,distanceMm:Math.hypot(x,y),dropped:i===dropIndex}})
}
function arrowQualityData(){
  const map=new Map();
  state.series.forEach(s=>{if(!Array.isArray(s.arrowMetrics))return;s.arrowMetrics.forEach(m=>{if(!map.has(m.arrow))map.set(m.arrow,{arrow:m.arrow,sum:0,count:0,dropped:0});const a=map.get(m.arrow);a.sum+=Number(m.distanceMm)||0;a.count++;if(m.dropped)a.dropped++})});
  return [...map.values()].filter(a=>a.count).map(a=>({...a,avg:a.sum/a.count})).sort((a,b)=>a.avg-b.avg)
}
function qualityWord(rank,total){if(total<=1)return AQTXT.neutral;const p=(rank-1)/(total-1);return p<.18?AQTXT.best:p<.40?AQTXT.good:p<.68?AQTXT.neutral:p<.88?AQTXT.watch:AQTXT.check}
function renderArrowQuality(){
  const w=$("arrowQualityWrap");if(!w)return;const d=arrowQualityData();
  if(!d.length){w.innerHTML='<div class="status warn">'+AQTXT.no_data+'</div>';return}
  let h='<div class="arrowQualityGrid">';d.forEach((a,i)=>{h+='<div class="arrowQualityCard"><button type="button" onclick="showArrowDetail('+a.arrow+')"><b>'+AQTXT.arrow+' '+a.arrow+'</b><span>'+AQTXT.rank+' '+(i+1)+'/'+d.length+' · '+qualityWord(i+1,d.length)+'</span><span class="small">'+AQTXT.avg+': '+a.avg.toFixed(1)+' mm · '+AQTXT.outliers+': '+a.dropped+'/'+a.count+'</span></button></div>'});h+='</div>';w.innerHTML=h
}
function detailScale(items,w,h){let m=30;items.forEach(p=>{m=Math.max(m,Math.abs(Number(p.xMm)||0),Math.abs(Number(p.yMm)||0))});m*=1.25;return{m,scale:Math.min((w-100)/(2*m),(h-100)/(2*m))}}
function drawDetail(items,mode){
  const c=$("detailCanvas"),ctx=c.getContext('2d'),W=c.width,H=c.height,cx=W/2,cy=H/2,s=detailScale(items,W,H);ctx.clearRect(0,0,W,H);ctx.fillStyle='#fff';ctx.fillRect(0,0,W,H);
  ctx.strokeStyle='#e1e6ed';ctx.lineWidth=1;const step=s.m>120?50:s.m>60?25:10;for(let r=step;r<=s.m;r+=step){ctx.beginPath();ctx.arc(cx,cy,r*s.scale,0,Math.PI*2);ctx.stroke()}
  ctx.strokeStyle='#7e8998';ctx.lineWidth=1.5;ctx.beginPath();ctx.moveTo(40,cy);ctx.lineTo(W-40,cy);ctx.moveTo(cx,40);ctx.lineTo(cx,H-40);ctx.stroke();ctx.fillStyle='#5b6572';ctx.font='13px system-ui';ctx.fillText(AQTXT.left,44,cy-8);ctx.textAlign='right';ctx.fillText(AQTXT.right,W-44,cy-8);ctx.textAlign='left';ctx.fillText(AQTXT.up,cx+8,54);ctx.fillText(AQTXT.down,cx+8,H-44);ctx.font='12px system-ui';ctx.fillText(AQTXT.center,cx+8,cy+18);
  items.forEach(p=>{const x=cx+(Number(p.xMm)||0)*s.scale,y=cy+(Number(p.yMm)||0)*s.scale;ctx.beginPath();ctx.arc(x,y,p.dropped?9:7,0,Math.PI*2);ctx.fillStyle=p.dropped?'#d7263d':mode==='arrow'?'#1b63c9':'#0f9d58';ctx.fill();ctx.strokeStyle='#fff';ctx.lineWidth=2;ctx.stroke();ctx.fillStyle='#18202a';ctx.font='bold 13px system-ui';ctx.fillText(mode==='arrow'?(AQTXT.series+' '+p.seriesNo):(AQTXT.arrow+' '+p.arrow),x+10,y-8)})
}
window.showArrowDetail=function(n){
  const items=[];state.series.forEach(s=>{if(!Array.isArray(s.arrowMetrics))return;const m=s.arrowMetrics.find(x=>Number(x.arrow)===Number(n));if(m)items.push({...m,seriesNo:s.seriesNo})});if(!items.length)return;
  $("detailTitle").textContent=AQTXT.title_arrow.replace('{n}',n);$("detailText").textContent=AQTXT.avg+': '+(items.reduce((a,p)=>a+(Number(p.distanceMm)||0),0)/items.length).toFixed(1)+' mm · '+AQTXT.series+': '+items.length;$("detailOverlay").classList.remove('hidden');drawDetail(items,'arrow')
};
window.showSeriesDetail=function(id,ev){if(ev&&ev.target&&ev.target.closest&&ev.target.closest('button'))return;const s=state.series.find(x=>Number(x.id)===Number(id));if(!s||!Array.isArray(s.arrowMetrics))return;
  $("detailTitle").textContent=AQTXT.title_series.replace('{n}',s.seriesNo);$("detailText").textContent=AQTXT.brace+': '+Number(s.braceHeight).toFixed(1)+' '+s.braceUnit+' · '+AQTXT.discarded+': '+AQTXT.arrow+' '+s.droppedArrow;$("detailOverlay").classList.remove('hidden');drawDetail(s.arrowMetrics,'series')
};
function closeDetail(){const o=$("detailOverlay");if(o)o.classList.add('hidden')}window.closeDetail=closeDetail;
document.addEventListener('keydown',e=>{if(e.key==='Escape')closeDetail()});
'''

for fn,cfg in configs.items():
    p=Path(fn); t=p.read_text(encoding='utf-8')
    t=re.sub(r'<meta name="app-release" content="[^"]+">','<meta name="app-release" content="2026-08-25-r2-arrow-quality">',t)
    if '.arrowQualityGrid{' not in t:
        t=t.replace('.printOnly{display:none}',css+'\n.printOnly{display:none}',1)
    if 'id="arrowQualityWrap"' not in t:
        t=t.replace('<section class="card printOnly">',cfg['section']+'\n<section class="card printOnly">',1)
    if 'id="detailOverlay"' not in t:
        overlay='<div id="detailOverlay" class="detailOverlay hidden" role="dialog" aria-modal="true"><div class="detailPanel"><div class="detailTop"><h2 id="detailTitle"></h2><button type="button" class="secondary" onclick="closeDetail()">'+cfg['close']+'</button></div><div class="detailCanvasWrap"><canvas id="detailCanvas" width="820" height="560"></canvas></div><div id="detailText" class="detailText"></div></div></div>'
        t=t.replace('</main>',overlay+'\n</main>',1)
    if 'function buildArrowMetrics(' not in t:
        helper=helper_template.replace('__AQTXT__',json.dumps(cfg,ensure_ascii=False,separators=(',',':')))
        t=t.replace('function drawPhoto()',helper+'\nfunction drawPhoto()',1)
    if 'arrowMetrics:buildArrowMetrics' not in t:
        t=t.replace('droppedArrow:res.dropIndex+1,','droppedArrow:res.dropIndex+1,arrowMetrics:buildArrowMetrics(state.arrows,res.dropIndex),',1)
    # Table rows: add click behavior to any best-row template that is not already clickable.
    t=t.replace('<tr class="${ib?\'best\':\'\'}">','<tr class="${ib?\'best \':\'\'}seriesClick" onclick="showSeriesDetail(${s.id},event)">')
    t=t.replace('<tr class="${ib?\"best\":\"\"}">','<tr class="${ib?\"best \":\"\"}seriesClick" onclick="showSeriesDetail(${s.id},event)">')
    t=t.replace('function drawAll(){saveSettings();drawChart();renderTable();renderBest();drawPhoto()}','function drawAll(){saveSettings();drawChart();renderTable();renderBest();renderArrowQuality();drawPhoto()}')
    p.write_text(t,encoding='utf-8')

assistants={
    'bogen-setup-assistent/index.html':'https://rblome22.github.io/Standhoehe--Recurve/',
    'bogen-setup-assistent-es/index.html':'https://rblome22.github.io/Standhoehe--Recurve/standhoehe-es/',
    'bow-setup-assistant-en/index.html':'https://rblome22.github.io/Standhoehe--Recurve/brace-height-en/'
}
for fn,url in assistants.items():
    p=Path(fn); t=p.read_text(encoding='utf-8')
    t=re.sub(r'<meta name="app-release" content="[^"]+">','<meta name="app-release" content="2026-08-25-r2-arrow-quality">',t)
    # Replace only Phase-1 iframe source, preserving normal links.
    t=re.sub(r'(id="braceFrame"[^>]*src=")'+re.escape(url)+r'(?:\?[^\"]*)?(\")',lambda m:m.group(1)+url+'?v=20260825-r2-arrow-quality'+m.group(2),t)
    p.write_text(t,encoding='utf-8')

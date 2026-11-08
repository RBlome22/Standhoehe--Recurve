/* Ergänzung Blankschafttest – Standhöhenfunktion unverändert. */
(()=>{
'use strict';
const el=id=>document.getElementById(id);
const STORAGE='recurve_blankschaft_tests_v1';
const stage=el('bsPhotoStage'), img=el('bsPhoto'), canvas=el('bsOverlay');
const ctx=canvas.getContext('2d');
const s={url:null,ready:false,mode:'calib',calib:[],marks:[],selected:'f',saved:[]};
try { const data=JSON.parse(localStorage.getItem(STORAGE)||'[]'); if(Array.isArray(data))s.saved=data; } catch(e){}
const num=id=>Number(el(id).value);
const fTarget=()=>num('bsFCount');
const bTarget=()=>num('bsBCount');
const count=type=>s.marks.filter(p=>p.type===type).length;
const required=()=>`${fTarget()} befiederte Pfeile und ${bTarget()} Blankschäfte`;
const fColor='#168849', bColor='#e58306';
function status(message, warning=false){el('bsStatus').textContent=message;el('bsStatus').className=warning?'status warn':'status';}
function phase(){
 if(!s.ready)return 'photo';
 if(s.calib.length<2)return 'calibration';
 return 'mark';
}
function setSelected(type){
 s.selected=type;
 el('bsSelectF').dataset.active=String(type==='f');
 el('bsSelectB').dataset.active=String(type==='b');
 if(phase()==='mark')status(`Pfeilart ${type==='f'?'Befiedert':'Blank'} gewählt. Treffer auf dem Foto antippen.`);
}
function point(e){const r=canvas.getBoundingClientRect();return{x:(e.clientX-r.left)/r.width*canvas.width,y:(e.clientY-r.top)/r.height*canvas.height};}
function distance(a,b){return Math.hypot(a.x-b.x,a.y-b.y);}
function drawDot(p,labelText,color,diamond=false){
 const r=Math.max(6,canvas.width*.009);
 ctx.lineWidth=Math.max(2,canvas.width*.003);
 ctx.strokeStyle='#fff';ctx.fillStyle=color;
 ctx.beginPath();
 if(diamond){ctx.moveTo(p.x,p.y-r);ctx.lineTo(p.x+r,p.y);ctx.lineTo(p.x,p.y+r);ctx.lineTo(p.x-r,p.y);ctx.closePath();}
 else ctx.arc(p.x,p.y,r,0,Math.PI*2);
 ctx.fill();ctx.stroke();
 ctx.font=`bold ${Math.max(15,canvas.width*.019)}px system-ui`;
 ctx.textBaseline='middle';ctx.textAlign='left';ctx.lineWidth=4;ctx.strokeStyle='rgba(0,0,0,.85)';
 ctx.strokeText(labelText,p.x+r+4,p.y-r);ctx.fillStyle=color;ctx.fillText(labelText,p.x+r+4,p.y-r);
}
function draw(){
 ctx.clearRect(0,0,canvas.width,canvas.height);
 const rad=Math.max(6,canvas.width*.007);
 if(s.calib.length){
  ctx.fillStyle='#00baf0';ctx.strokeStyle='#00baf0';ctx.lineWidth=3;
  s.calib.forEach((p,i)=>{ctx.beginPath();ctx.arc(p.x,p.y,rad,0,2*Math.PI);ctx.fill();drawDot(p,'K'+(i+1),'#00baf0');});
  if(s.calib.length===2){ctx.beginPath();ctx.moveTo(s.calib[0].x,s.calib[0].y);ctx.lineTo(s.calib[1].x,s.calib[1].y);ctx.stroke();}
 }
 let f=0,b=0;
 for(const p of s.marks){if(p.type==='f'){f++;drawDot(p,'F'+f,fColor)}else{b++;drawDot(p,'B'+b,bColor,true)}}
 const result=calculate();
 if(result){
  // Bezugsmittelpunkt und Mittelwert der Blankschäfte
  drawDot(result.fCentre,'F-Mitte','#0561bf');
  drawDot(result.bCentre,'B-Mitte','#9e4d00',true);
  ctx.beginPath();ctx.moveTo(result.fCentre.x,result.fCentre.y);ctx.lineTo(result.bCentre.x,result.bCentre.y);
  ctx.strokeStyle='#225aab';ctx.lineWidth=2;ctx.setLineDash([9,5]);ctx.stroke();ctx.setLineDash([]);
 }
}
function calculate(){
 if(!s.ready||s.calib.length!==2||count('f')!==fTarget()||count('b')!==bTarget())return null;
 const diameter=num('bsDiameter'),px=distance(s.calib[0],s.calib[1]);
 if(!Number.isFinite(diameter)||diameter<=0||px<2)return null;
 const f=s.marks.filter(p=>p.type==='f'),b=s.marks.filter(p=>p.type==='b');
 const avg=a=>({x:a.reduce((v,p)=>v+p.x,0)/a.length,y:a.reduce((v,p)=>v+p.y,0)/a.length});
 const fc=avg(f),bc=avg(b),mmPerPx=diameter*10/px;
 const dx=(bc.x-fc.x)*mmPerPx,dy=(fc.y-bc.y)*mmPerPx;
 return {fCentre:fc,bCentre:bc,dx,dy,offset:Math.hypot(dx,dy),mmPerPx,
  bare:b.map((p,i)=>({number:i+1,dx:(p.x-fc.x)*mmPerPx,dy:(fc.y-p.y)*mmPerPx}))};
}
function fmt(n){return (Math.round(n*10)/10).toFixed(1).replace('.',',');}
function direction(n,pos,neg){return Math.abs(n)<.05?'0 mm':`${fmt(Math.abs(n))} mm ${n>0?pos:neg}`;}
function safe(text){return String(text).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
function update(){
 const fc=count('f'),bc=count('b');
 el('bsCounter').textContent=`Befiedert: ${fc}/${fTarget()} · Blank: ${bc}/${bTarget()}`;
 const ul=el('bsMarkers'); ul.innerHTML='';
 s.marks.forEach((m,i)=>{
  const row=document.createElement('li');
  const text=document.createElement('span');text.textContent=`Treffer ${i+1}:`;
  const sel=document.createElement('select');sel.setAttribute('aria-label',`Pfeilart für Treffer ${i+1}`);
  sel.innerHTML='<option value="f">Befiederter Pfeil</option><option value="b">Blankschaft</option>';sel.value=m.type;
  sel.addEventListener('change',()=>{m.type=sel.value;refresh();});
  const del=document.createElement('button');del.className='secondary';del.textContent='Entfernen';
  del.addEventListener('click',()=>{s.marks.splice(i,1);refresh();});
  row.append(text,sel,del);ul.append(row);
 });
 const result=calculate();
 if(result){
  const lines=result.bare.map(p=>`<tr><td>Blank ${p.number}</td><td>${safe(direction(p.dx,'rechts','links'))}</td><td>${safe(direction(p.dy,'oben','unten'))}</td></tr>`).join('');
  el('bsResult').className='bs-result';
  el('bsResult').innerHTML=`<h3>Blankschaft-Ergebnis</h3>
  <div class="bs-offsets"><div>Horizontal<strong>${safe(direction(result.dx,'rechts','links'))}</strong></div>
  <div>Vertikal<strong>${safe(direction(result.dy,'oben','unten'))}</strong></div>
  <div>Gesamtabstand<strong>${fmt(result.offset)} mm</strong></div></div>
  <p class="hint" style="margin:10px 0">Vergleich der Mittelpunkte: ${fTarget()} befiederte Pfeile gegen ${bTarget()} Blankschaft/Blankschäfte, Entfernung ${num('bsDistance')} m.</p>
  <table><thead><tr><th>Pfeil</th><th>Horizontal</th><th>Vertikal</th></tr></thead><tbody>${lines}</tbody></table>`;
 }else{
  el('bsResult').className='status warn';
  const missing=[];
  if(!s.ready)missing.push('Foto');
  if(s.calib.length<2)missing.push('2 Kalibrierpunkte');
  if(fc!==fTarget())missing.push(`befiederte Pfeile ${fc}/${fTarget()}`);
  if(bc!==bTarget())missing.push(`Blankschäfte ${bc}/${bTarget()}`);
  if(!(num('bsDiameter')>0))missing.push('gültigen Scheibendurchmesser');
  el('bsResult').textContent=`Für die Berechnung fehlen: ${missing.join(', ')}. Keine Pfeile werden automatisch gestrichen.`;
 }
}
function refresh(){update();draw();}
function loadPhoto(file){
 if(!file)return;
 if(s.url){URL.revokeObjectURL(s.url);s.url=null;}
 s.ready=false;s.calib=[];s.marks=[];s.mode='calib';
 stage.hidden=true;el('bsEmptyPhoto').style.display='block';status('Foto wird geladen …');
 const url=URL.createObjectURL(file);s.url=url;
 img.onload=()=>{
  const w=img.naturalWidth,h=img.naturalHeight;
  if(!(w>0&&h>0)){status('Foto hat keine gültigen Bildabmessungen.',true);return;}
  const factor=Math.min(1100/w,1100/h,1);
  canvas.width=Math.max(1,Math.round(w*factor));
  canvas.height=Math.max(1,Math.round(h*factor));
  stage.hidden=false;el('bsEmptyPhoto').style.display='none';s.ready=true;
  status('Foto sichtbar. Bitte zwei gegenüberliegende Punkte des Scheibendurchmessers antippen (links und rechts).');
  refresh();
 };
 img.onerror=()=>{stage.hidden=true;status('Fotoformat wird nicht angezeigt. Bitte ein JPG-/PNG-Foto versuchen.',true);};
 img.src=url;
}
function snapshot(){
 if(!s.ready)return null;
 try{
  const w=640,h=Math.max(1,Math.round(640*canvas.height/canvas.width));
  const c=document.createElement('canvas');c.width=w;c.height=h;let g=c.getContext('2d');
  g.drawImage(img,0,0,w,h);g.drawImage(canvas,0,0,w,h);
  return c.toDataURL('image/jpeg',.70);
 }catch(e){return null;}
}
function persist(){
 try{localStorage.setItem(STORAGE,JSON.stringify(s.saved));return true;}
 catch(e){
  // Try storing the same numeric records without photo to avoid quota crashes.
  try{s.saved.forEach(item=>{item.photo=null});localStorage.setItem(STORAGE,JSON.stringify(s.saved));status('Speicherplatz knapp. Messergebnisse gespeichert, Archivfotos ausgelassen.',true);return true;}catch(e2){status('Lokaler Speicher voll: bitte zuerst JSON sichern, dann alte Tests löschen.',true);return false;}
 }
}
function renderHistory(){
 const wrap=el('bsTableWrap');
 if(!s.saved.length){wrap.innerHTML='<p class="hint">Noch keine gespeicherten Blankschafttests.</p>';return;}
 let html='<table><thead><tr><th>Datum</th><th>Pfeile</th><th>Horizontal</th><th>Vertikal</th><th>Abstand</th><th class="noPrint">Aktion</th></tr></thead><tbody>';
 s.saved.slice().reverse().forEach(r=>{
  html+=`<tr><td>${safe(r.date)}</td><td>${r.fCount} F + ${r.bCount} B</td><td>${fmt(r.dx)} mm</td><td>${fmt(r.dy)} mm</td><td>${fmt(r.offset)} mm</td><td class="noPrint"><button class="secondary" type="button" data-bs-view="${r.id}">Anzeigen</button> <button class="danger" type="button" data-bs-delete="${r.id}">Löschen</button></td></tr>`;
 });
 wrap.innerHTML=html+'</tbody></table>';
 wrap.querySelectorAll('[data-bs-delete]').forEach(btn=>btn.addEventListener('click',()=>{
  if(!confirm('Diesen Blankschafttest löschen?'))return;
  s.saved=s.saved.filter(x=>String(x.id)!==btn.dataset.bsDelete);persist();renderHistory();
 }));
 wrap.querySelectorAll('[data-bs-view]').forEach(btn=>btn.addEventListener('click',()=>{
  const r=s.saved.find(x=>String(x.id)===btn.dataset.bsView);if(!r)return;
  el('bsResult').className='bs-result';
  el('bsResult').innerHTML=`<h3>Archivierter Blankschafttest vom ${safe(r.date)}</h3><div class="bs-offsets"><div>Horizontal<strong>${safe(direction(r.dx,'rechts','links'))}</strong></div><div>Vertikal<strong>${safe(direction(r.dy,'oben','unten'))}</strong></div><div>Gesamtabstand<strong>${fmt(r.offset)} mm</strong></div></div><p>${r.fCount} befiederte Pfeile, ${r.bCount} Blankschäfte, Entfernung ${r.distance} m</p>`;
  el('bsPhotoPrint').src=r.photo||''; 
  el('bsResult').scrollIntoView({behavior:'smooth',block:'center'});
 }));
}
function save(){
 const r=calculate();if(!r){status(`Bitte genau ${required()} zuordnen und die Scheibe kalibrieren.`,true);return;}
 const photo=snapshot();
 const record={id:Date.now(),date:new Date().toLocaleString('de-DE'),archer:el('archer').value,bow:el('bow').value,
  fCount:fTarget(),bCount:bTarget(),diameter:num('bsDiameter'),distance:num('bsDistance'),
  dx:r.dx,dy:r.dy,offset:r.offset,bare:r.bare,photo};
 s.saved.push(record); if(!persist()){s.saved.pop();return;}
 el('bsPhotoPrint').src=photo||'';
 renderHistory();status('Blankschafttest gespeichert. Foto und Abweichungen wurden übernommen.');
}
function download(name,text,mime){
 const a=document.createElement('a'),url=URL.createObjectURL(new Blob([text],{type:mime}));
 a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1500);
}
function printBS(){
 const r=calculate();
 if(r){const photo=snapshot();if(photo){el('bsPhotoPrint').src=photo;el('bsPhotoPrint').style.display='block';}}
 document.body.classList.add('bs-only');window.print();
}
window.addEventListener('afterprint',()=>document.body.classList.remove('bs-only'));
// On some iPad versions afterprint is not delivered; clean up when focus returns.
window.addEventListener('focus',()=>document.body.classList.remove('bs-only'));
for(const id of ['bsImageInput','bsCameraInput'])el(id).addEventListener('change',e=>{loadPhoto(e.target.files[0]);e.target.value='';});
canvas.addEventListener('click',e=>{
 if(!s.ready)return;
 const p=point(e);
 if(s.calib.length<2){s.calib.push(p);if(s.calib.length===2){s.mode='mark';status('Kalibrierung fertig. Befiedert oder Blank wählen und alle Treffer antippen.');}}
 else{
  if(count(s.selected)>=(s.selected==='f'?fTarget():bTarget())){status(`Maximale Anzahl für ${s.selected==='f'?'befiederte Pfeile':'Blankschäfte'} erreicht. Andere Pfeilart wählen oder unten umsortieren.`,true);return;}
  s.marks.push({...p,type:s.selected});
  if(count('f')>=fTarget()&&count('b')<bTarget())setSelected('b');
  else if(count('b')>=bTarget()&&count('f')<fTarget())setSelected('f');
 }
 refresh();
});
el('bsSelectF').addEventListener('click',()=>setSelected('f'));
el('bsSelectB').addEventListener('click',()=>setSelected('b'));
el('bsCalibration').addEventListener('click',()=>{s.calib=[];s.mode='calib';status('Bitte zwei Punkte des Scheibendurchmessers antippen. Die Zuordnung der Pfeile bleibt erhalten.');refresh();});
el('bsUndo').addEventListener('click',()=>{if(s.marks.length)s.marks.pop();else if(s.calib.length)s.calib.pop();refresh();});
el('bsClear').addEventListener('click',()=>{if(!confirm('Alle Foto-Markierungen des aktuellen Blankschafttests löschen?'))return;s.marks=[];s.calib=[];status('Markierungen gelöscht. Bitte neu kalibrieren.');refresh();});
for(const id of ['bsFCount','bsBCount','bsDiameter','bsDistance'])el(id).addEventListener('change',refresh);
el('bsSave').addEventListener('click',save);
el('bsPrint').addEventListener('click',printBS);
el('bsExport').addEventListener('click',()=>download('blankschafttests_sicherung.json',JSON.stringify({type:'recurve-blankschaft',version:1,tests:s.saved},null,2),'application/json'));
el('bsImport').addEventListener('click',()=>el('bsImportFile').click());
el('bsImportFile').addEventListener('change',e=>{
 const file=e.target.files[0];if(!file)return;
 const reader=new FileReader();reader.onload=()=>{try{const obj=JSON.parse(reader.result);if(!Array.isArray(obj.tests))throw new Error('Kein gültiges Blankschaft-Archiv');
  if(confirm(`${obj.tests.length} gespeicherte Tests importieren und bisheriges Blankschaft-Archiv ersetzen?`)){
   s.saved=obj.tests.filter(t=>typeof t.dx==='number'&&typeof t.dy==='number'&&typeof t.offset==='number');persist();renderHistory();status(`${s.saved.length} Blankschafttests importiert.`);
  }}catch(err){status('JSON-Import fehlgeschlagen: '+err.message,true);}};reader.readAsText(file);e.target.value='';
});
renderHistory();refresh();
})();
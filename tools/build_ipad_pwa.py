from pathlib import Path
import shutil, struct, zlib, math

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'ipad-app'
OUT.mkdir(exist_ok=True)

# Copy the fully self-contained combined apps into one PWA scope.
files = {
    'de.html': ROOT/'offline-downloads'/'Bogen_Setup_Assistent_v3_Offline_DE.html',
    'es.html': ROOT/'offline-downloads'/'Asistente_Puesta_a_Punto_v3_Offline_ES.html',
    'en.html': ROOT/'offline-downloads'/'Bow_Setup_Assistant_v3_Offline_EN.html',
}
for dst, src in files.items():
    shutil.copyfile(src, OUT/dst)

index = r'''<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover,user-scalable=yes">
<meta name="theme-color" content="#0b6b4b">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<meta name="apple-mobile-web-app-title" content="Bogen Setup">
<meta name="application-name" content="Bogen Setup">
<title>Bogen Setup</title>
<link rel="manifest" href="./manifest.webmanifest">
<link rel="apple-touch-icon" sizes="180x180" href="./icon-180.png">
<style>
:root{--bg:#f3f6f4;--card:#fff;--ink:#17231e;--muted:#66736d;--green:#0b6b4b;--dark:#173d32;--line:#d7e0db;--blue:#255e9d}
*{box-sizing:border-box;-webkit-tap-highlight-color:transparent}body{margin:0;background:var(--bg);color:var(--ink);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Arial,sans-serif}main{max-width:760px;margin:auto;padding:22px 16px 34px}.logo{width:112px;height:112px;border-radius:24px;display:block;margin:12px auto 18px;box-shadow:0 5px 22px #0002}h1{text-align:center;margin:0 0 6px;font-size:30px}.sub{text-align:center;color:var(--muted);margin:0 0 22px}.card{background:#fff;border:1px solid var(--line);border-radius:18px;padding:18px;margin:14px 0;box-shadow:0 5px 20px #0000000d}.status{border-left:5px solid var(--green);background:#edf7f2;border-radius:12px;padding:12px 14px;line-height:1.45}.status.wait{border-left-color:#b47b15;background:#fff7e8}.buttons{display:grid;gap:12px;margin-top:16px}button{border:0;border-radius:15px;padding:17px 16px;min-height:58px;font:inherit;font-weight:800;font-size:18px;background:var(--green);color:#fff}button.secondary{background:#e8f0fb;color:#244f83}button.tertiary{background:#e6eeea;color:var(--dark)}.steps{font-size:15px;line-height:1.55}.small{font-size:13px;color:var(--muted);line-height:1.45}footer{text-align:center;color:var(--muted);font-size:12px;margin-top:22px;line-height:1.5}@media(min-width:700px){main{padding-top:38px}.logo{width:132px;height:132px}}
</style>
</head>
<body><main>
<img class="logo" src="./icon-192.png" alt="Bogen Setup Logo">
<h1>Bogen Setup</h1>
<p class="sub">Standhöhe · Pfeilqualität · Blankschaft · Nockpunkt · Tiller</p>
<section class="card">
<div id="offlineStatus" class="status wait"><b>Offline wird vorbereitet …</b><br>Beim ersten Öffnen bitte kurz mit dem Internet verbunden bleiben.</div>
<div class="buttons">
<button onclick="openApp('de.html','de')">Deutsch</button>
<button class="secondary" onclick="openApp('es.html','es')">Español</button>
<button class="tertiary" onclick="openApp('en.html','en')">English</button>
</div>
</section>
<section class="card steps">
<b>Auf dem iPad installieren:</b><br>
1. Diese Seite einmal in <b>Safari</b> öffnen.<br>
2. Warten, bis oben <b>„✓ Offline bereit“</b> steht.<br>
3. Safari: <b>Teilen → Zum Home-Bildschirm</b>.<br>
4. <b>Hinzufügen</b> wählen.<br><br>
Danach erscheint das Symbol <b>„Bogen Setup“</b> auf dem iPad-Home-Bildschirm. Die App kann anschließend am Übungsplatz ohne Internet gestartet werden.
</section>
<section class="card small"><b>Hinweis:</b> Die Messdaten bleiben lokal auf dem jeweiligen Gerät. Für eine neue Programmversion die App später einmal wieder mit Internet öffnen.</section>
<footer>© 2026 Rainer Blome · r.blome@rainer-blome.de · Alle Rechte vorbehalten.<br>Die Benutzung erfolgt auf eigene Gefahr. Für eventuell entstandene Schäden wird keine Haftung übernommen.</footer>
</main>
<script>
function openApp(file,lang){try{localStorage.setItem('bogenSetupLanguage',lang)}catch(e){} location.href='./'+file;}
if('serviceWorker' in navigator){
  navigator.serviceWorker.register('./sw.js').then(()=>navigator.serviceWorker.ready).then(()=>{
    const s=document.getElementById('offlineStatus');
    s.className='status'; s.innerHTML='<b>✓ Offline bereit</b><br>Die Programme wurden auf diesem Gerät gespeichert.';
  }).catch(()=>{
    document.getElementById('offlineStatus').innerHTML='<b>Offline-Speicherung nicht bestätigt.</b><br>Bitte die Seite in Safari neu laden.';
  });
}else{
  document.getElementById('offlineStatus').innerHTML='<b>Offline-Speicherung wird von diesem Browser nicht unterstützt.</b><br>Bitte Safari verwenden.';
}
</script>
</body></html>'''
(OUT/'index.html').write_text(index, encoding='utf-8')

manifest = '''{
  "name": "Bogen Setup",
  "short_name": "Bogen Setup",
  "description": "Recurve Bogen einstellen: Standhöhe, Pfeilqualität, Blankschaft, Nockpunkt und Tiller",
  "start_url": "./index.html",
  "scope": "./",
  "display": "standalone",
  "background_color": "#f3f6f4",
  "theme_color": "#0b6b4b",
  "icons": [
    {"src":"./icon-192.png","sizes":"192x192","type":"image/png","purpose":"any maskable"},
    {"src":"./icon-512.png","sizes":"512x512","type":"image/png","purpose":"any maskable"}
  ]
}'''
(OUT/'manifest.webmanifest').write_text(manifest, encoding='utf-8')

sw = r'''const CACHE='bogen-setup-ipad-v1';
const ASSETS=['./','./index.html','./de.html','./es.html','./en.html','./manifest.webmanifest','./icon-180.png','./icon-192.png','./icon-512.png'];
self.addEventListener('install',e=>{e.waitUntil(caches.open(CACHE).then(c=>c.addAll(ASSETS)).then(()=>self.skipWaiting()))});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim()))});
self.addEventListener('fetch',e=>{if(e.request.method!=='GET')return;e.respondWith(caches.match(e.request).then(r=>r||fetch(e.request).then(resp=>{const copy=resp.clone();caches.open(CACHE).then(c=>c.put(e.request,copy));return resp}).catch(()=>{if(e.request.mode==='navigate')return caches.match('./index.html');}))) });'''
(OUT/'sw.js').write_text(sw, encoding='utf-8')

# Pure-Python PNG generator. Icon: green field, archery target, diagonal arrow.
def make_png(size, path):
    bg=(11,107,75,255)
    pix=[[list(bg) for _ in range(size)] for _ in range(size)]
    cx=cy=size//2
    rings=[(0.36,(245,248,246,255)),(0.29,(46,117,182,255)),(0.21,(205,54,54,255)),(0.13,(245,196,50,255))]
    for frac,col in rings:
        r=int(size*frac); r2=r*r
        for y in range(max(0,cy-r),min(size,cy+r+1)):
            dy=y-cy
            for x in range(max(0,cx-r),min(size,cx+r+1)):
                dx=x-cx
                if dx*dx+dy*dy<=r2: pix[y][x]=list(col)
    rr=max(2,size//45)
    for y in range(cy-rr,cy+rr+1):
        for x in range(cx-rr,cx+rr+1):
            if 0<=x<size and 0<=y<size: pix[y][x]=[30,30,30,255]
    x0=int(size*.18); y0=int(size*.82); x1=int(size*.82); y1=int(size*.18)
    width=max(3,size//40); vx=x1-x0; vy=y1-y0; L=math.hypot(vx,vy); nx=-vy/L; ny=vx/L
    for t in range(int(L)+1):
        x=x0+vx*t/L; y=y0+vy*t/L
        for w in range(-width,width+1):
            xx=int(round(x+nx*w)); yy=int(round(y+ny*w))
            if 0<=xx<size and 0<=yy<size: pix[yy][xx]=[255,255,255,255]
    head=max(14,size//8); ux=vx/L; uy=vy/L; bx=x1-ux*head; by=y1-uy*head
    p1=(x1,y1); p2=(bx+nx*head*.55,by+ny*head*.55); p3=(bx-nx*head*.55,by-ny*head*.55)
    def inside(px,py,a,b,c):
        def s(p1,p2,p3): return (p1[0]-p3[0])*(p2[1]-p3[1])-(p2[0]-p3[0])*(p1[1]-p3[1])
        d1=s((px,py),a,b); d2=s((px,py),b,c); d3=s((px,py),c,a)
        return not ((d1<0 or d2<0 or d3<0) and (d1>0 or d2>0 or d3>0))
    minx=max(0,int(min(p1[0],p2[0],p3[0]))-1); maxx=min(size-1,int(max(p1[0],p2[0],p3[0]))+1)
    miny=max(0,int(min(p1[1],p2[1],p3[1]))-1); maxy=min(size-1,int(max(p1[1],p2[1],p3[1]))+1)
    for y in range(miny,maxy+1):
        for x in range(minx,maxx+1):
            if inside(x,y,p1,p2,p3): pix[y][x]=[255,255,255,255]
    tail=max(12,size//10)
    for sign in (-1,1):
        ax=x0+nx*sign*2; ay=y0+ny*sign*2
        bx2=x0-ux*tail+nx*sign*tail*.45; by2=y0-uy*tail+ny*sign*tail*.45
        cx2=x0-ux*tail*.65; cy2=y0-uy*tail*.65
        pts=((ax,ay),(bx2,by2),(cx2,cy2))
        minx=max(0,int(min(p[0] for p in pts))-1); maxx=min(size-1,int(max(p[0] for p in pts))+1)
        miny=max(0,int(min(p[1] for p in pts))-1); maxy=min(size-1,int(max(p[1] for p in pts))+1)
        for y in range(miny,maxy+1):
            for x in range(minx,maxx+1):
                if inside(x,y,*pts): pix[y][x]=[255,255,255,255]
    raw=b''.join(b'\x00'+bytes(sum(row,[])) for row in pix)
    def chunk(tag,data): return struct.pack('>I',len(data))+tag+data+struct.pack('>I',zlib.crc32(tag+data)&0xffffffff)
    data=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',size,size,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(raw,9))+chunk(b'IEND',b'')
    path.write_bytes(data)

for s in (180,192,512): make_png(s, OUT/f'icon-{s}.png')
print('Built iPad PWA in', OUT)
# Trigger marker: 2026-09-05

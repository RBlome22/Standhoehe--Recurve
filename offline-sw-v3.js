const CACHE_NAME='bogen-setup-v3-offline-20260905-1';
const BASE='/Standhoehe--Recurve/';
const PRECACHE=[
  BASE,
  BASE+'index.html',
  BASE+'standhoehe-es/',
  BASE+'standhoehe-es/index.html',
  BASE+'brace-height-en/',
  BASE+'brace-height-en/index.html',
  BASE+'arrow-quality-addon.js',
  BASE+'standhoehe-v3/',
  BASE+'standhoehe-v3/index.html',
  BASE+'standhoehe-es-v3/',
  BASE+'standhoehe-es-v3/index.html',
  BASE+'brace-height-v3/',
  BASE+'brace-height-v3/index.html',
  BASE+'blankschaft-tuner-v261/',
  BASE+'blankschaft-tuner-v261/index.html',
  BASE+'blankschaft-tuner-es/',
  BASE+'blankschaft-tuner-es/index.html',
  BASE+'bare-shaft-tuner-en/',
  BASE+'bare-shaft-tuner-en/index.html',
  BASE+'bogen-setup-assistent/',
  BASE+'bogen-setup-assistent/index.html',
  BASE+'bogen-setup-assistent-es/',
  BASE+'bogen-setup-assistent-es/index.html',
  BASE+'bow-setup-assistant-en/',
  BASE+'bow-setup-assistant-en/index.html',
  BASE+'bogen-setup-assistent-v3/',
  BASE+'bogen-setup-assistent-v3/index.html',
  BASE+'bogen-setup-assistent-es-v3/',
  BASE+'bogen-setup-assistent-es-v3/index.html',
  BASE+'bow-setup-assistant-v3/',
  BASE+'bow-setup-assistant-v3/index.html',
  BASE+'offline-v3-de.webmanifest',
  BASE+'offline-v3-es.webmanifest',
  BASE+'offline-v3-en.webmanifest'
];
self.addEventListener('install',event=>{
  event.waitUntil(caches.open(CACHE_NAME).then(async cache=>{
    for(const url of PRECACHE){
      try{await cache.add(new Request(url,{cache:'reload'}));}catch(e){console.warn('Could not precache',url,e);}
    }
  }).then(()=>self.skipWaiting()));
});
self.addEventListener('activate',event=>{
  event.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>k.startsWith('bogen-setup-v3-offline-')&&k!==CACHE_NAME).map(k=>caches.delete(k)))).then(()=>self.clients.claim()));
});
self.addEventListener('fetch',event=>{
  const req=event.request;
  if(req.method!=='GET')return;
  const url=new URL(req.url);
  if(url.origin!==self.location.origin || !url.pathname.startsWith(BASE))return;
  event.respondWith((async()=>{
    const cache=await caches.open(CACHE_NAME);
    const cached=await cache.match(req,{ignoreSearch:true});
    if(cached){
      event.waitUntil(fetch(req).then(r=>{if(r&&r.ok)cache.put(req,r.clone());}).catch(()=>{}));
      return cached;
    }
    try{
      const fresh=await fetch(req);
      if(fresh&&fresh.ok)cache.put(req,fresh.clone());
      return fresh;
    }catch(e){
      if(req.mode==='navigate'){
        const fallback=await cache.match(BASE+'bogen-setup-assistent-v3/',{ignoreSearch:true});
        if(fallback)return fallback;
      }
      throw e;
    }
  })());
});

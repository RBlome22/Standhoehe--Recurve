from pathlib import Path
import base64
import re

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'offline-downloads'
OUT.mkdir(exist_ok=True)


def clean_html(relpath):
    t = (ROOT / relpath).read_text(encoding='utf-8')
    t = re.sub(r'\s*<link rel="manifest"[^>]*>', '', t)
    t = re.sub(r'\s*<link rel="apple-touch-icon"[^>]*>', '', t)
    # Remove any service-worker registration added to a web-only wrapper.
    t = re.sub(r'<script>\s*if\s*\(\s*[\'\"]serviceWorker[\'\"]\s*in\s*navigator\s*\).*?</script>', '', t, flags=re.S)
    return t


def enc(text):
    return base64.b64encode(text.encode('utf-8')).decode('ascii')


def make_combo(lang, brace_html, blank_html, text):
    brace64 = enc(brace_html)
    blank64 = enc(blank_html)
    return '''<!doctype html>
<html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><meta name="apple-mobile-web-app-capable" content="yes"><title>{title}</title>
<style>
:root{{--bg:#f3f6f4;--card:#fff;--ink:#17231e;--muted:#66736d;--green:#0b6b4b;--dark:#173d32;--line:#d7e0db;--blue:#255e9d}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Arial,sans-serif}}header{{padding:14px 16px;background:#fff;border-bottom:1px solid var(--line);position:sticky;top:0;z-index:20}}header b{{font-size:22px}}header span{{display:block;color:var(--muted);font-size:13px;margin-top:3px}}main{{max-width:1180px;margin:auto;padding:16px}}.card{{background:#fff;border:1px solid var(--line);border-radius:18px;padding:18px;margin-bottom:14px;box-shadow:0 5px 20px #0000000d}}h1,h2{{margin:0 0 12px}}p{{line-height:1.5}}.notice{{border-left:5px solid var(--green);background:#edf7f2;border-radius:12px;padding:12px 14px;margin:12px 0;line-height:1.45}}.notice.blue{{border-left-color:var(--blue);background:#eef5ff;color:#183f70}}.actions{{display:flex;gap:10px;flex-wrap:wrap;margin-top:14px}}button{{border:0;border-radius:14px;padding:14px 16px;min-height:50px;font:inherit;font-weight:800;font-size:16px;cursor:pointer;flex:1 1 220px}}.primary{{background:var(--green);color:#fff}}.secondary{{background:#e6eeea;color:var(--dark)}}.hidden{{display:none!important}}iframe{{width:100%;height:78vh;min-height:620px;border:1px solid var(--line);border-radius:14px;background:#fff}}footer{{max-width:1180px;margin:auto;padding:0 16px 28px;text-align:center;color:var(--muted);font-size:12px}}@media(max-width:700px){{iframe{{height:76vh;min-height:540px}}}}
</style></head><body>
<header><b>{title}</b><span>{subtitle}</span></header><main>
<section id="overview" class="card"><h1>{title}</h1><p>{intro}</p><div class="notice blue">{note}</div><div class="actions"><button class="primary" onclick="showPhase(1)">{open1}</button><button class="secondary" onclick="showPhase(2)">{open2}</button></div></section>
<section id="phase1" class="card hidden"><h2>{phase1}</h2><iframe id="braceFrame" title="{phase1}"></iframe><div class="actions"><button class="secondary" onclick="showOverview()">{back}</button><button class="primary" onclick="showPhase(2)">{open2}</button></div></section>
<section id="phase2" class="card hidden"><h2>{phase2}</h2><iframe id="blankFrame" title="{phase2}"></iframe><div class="actions"><button class="secondary" onclick="showOverview()">{back}</button></div></section>
</main><footer>{rights}<br>{risk}</footer>
<script>
const BRACE='{brace64}';
const BLANK='{blank64}';
function decode64(x){{const s=atob(x),a=new Uint8Array(s.length);for(let i=0;i<s.length;i++)a[i]=s.charCodeAt(i);return new TextDecoder('utf-8').decode(a)}}
let loaded1=false, loaded2=false;
function showOverview(){{document.getElementById('overview').classList.remove('hidden');document.getElementById('phase1').classList.add('hidden');document.getElementById('phase2').classList.add('hidden');window.scrollTo(0,0)}}
function showPhase(n){{document.getElementById('overview').classList.add('hidden');document.getElementById('phase1').classList.toggle('hidden',n!==1);document.getElementById('phase2').classList.toggle('hidden',n!==2);if(n===1&&!loaded1){{document.getElementById('braceFrame').srcdoc=decode64(BRACE);loaded1=true}}if(n===2&&!loaded2){{document.getElementById('blankFrame').srcdoc=decode64(BLANK);loaded2=true}}window.scrollTo(0,0)}}
</script></body></html>'''.format(lang=lang, brace64=brace64, blank64=blank64, **text)


LANGS = {
    'de': {
        'brace': 'index.html',
        'blank': 'blankschaft-tuner-v261/index.html',
        'brace_file': 'Standhoehen_Optimierer_v3_Offline_DE.html',
        'blank_file': 'Blankschaft_Tuner_Offline_DE.html',
        'combo_file': 'Bogen_Setup_Assistent_v3_Offline_DE.html',
        'text': dict(
            title='Bogen-Setup Assistent v3 – Offline',
            subtitle='Vollständig offline · Standhöhe · Pfeilqualität · Blankschaft · Nockpunkt · Tiller',
            intro='Diese Datei enthält beide Programme vollständig. Nach dem Herunterladen wird keine Internetverbindung benötigt.',
            note='Nach Phase 1 die optimale Standhöhe notieren. Anschließend Phase 2 durchführen.',
            open1='Standhöhen-Optimierer öffnen',
            open2='Weiter zum Blankschaft-Tuner',
            phase1='Phase 1 – Standhöhe',
            phase2='Phase 2 – Blankschaft / Nockpunkt / Tiller',
            back='Zurück zur Übersicht',
            rights='© 2026 Rainer Blome · r.blome@rainer-blome.de · Alle Rechte vorbehalten.',
            risk='Die Benutzung erfolgt auf eigene Gefahr. Für eventuell entstandene Schäden wird keine Haftung übernommen.'
        )
    },
    'es': {
        'brace': 'standhoehe-es/index.html',
        'blank': 'blankschaft-tuner-es/index.html',
        'brace_file': 'Optimizador_Fistmele_v3_Offline_ES.html',
        'blank_file': 'Afinador_Flecha_Desnuda_Offline_ES.html',
        'combo_file': 'Asistente_Puesta_a_Punto_v3_Offline_ES.html',
        'text': dict(
            title='Asistente de puesta a punto v3 – Sin conexión',
            subtitle='Completamente sin conexión · fistmele · calidad de flechas · flecha desnuda · punto de enfleche · tiller',
            intro='Este archivo contiene las dos aplicaciones completas. Después de descargarlo no se necesita conexión a Internet.',
            note='Después de la fase 1, anote el fistmele óptimo. A continuación realice la fase 2.',
            open1='Abrir optimizador de fistmele',
            open2='Continuar con el afinador de flecha desnuda',
            phase1='Fase 1 – Fistmele',
            phase2='Fase 2 – Flecha desnuda / punto de enfleche / tiller',
            back='Volver al resumen',
            rights='© 2026 Rainer Blome · r.blome@rainer-blome.de · Todos los derechos reservados.',
            risk='El uso se realiza bajo la propia responsabilidad del usuario. No se asume ninguna responsabilidad por los daños que pudieran producirse.'
        )
    },
    'en': {
        'brace': 'brace-height-en/index.html',
        'blank': 'bare-shaft-tuner-en/index.html',
        'brace_file': 'Brace_Height_Optimizer_v3_Offline_EN.html',
        'blank_file': 'Bare_Shaft_Tuner_Offline_EN.html',
        'combo_file': 'Bow_Setup_Assistant_v3_Offline_EN.html',
        'text': dict(
            title='Bow Setup Assistant v3 – Offline',
            subtitle='Fully offline · brace height · arrow quality · bare shaft · nocking point · tiller',
            intro='This file contains both applications in full. After downloading, no internet connection is required.',
            note='After phase 1, note the optimum brace height. Then continue with phase 2.',
            open1='Open Brace Height Optimizer',
            open2='Continue to Bare Shaft Tuner',
            phase1='Phase 1 – Brace height',
            phase2='Phase 2 – Bare shaft / nocking point / tiller',
            back='Back to overview',
            rights='© 2026 Rainer Blome · r.blome@rainer-blome.de · All rights reserved.',
            risk='Use at your own risk. No liability is accepted for any damage that may occur.'
        )
    }
}

for lang, cfg in LANGS.items():
    brace = clean_html(cfg['brace'])
    blank = clean_html(cfg['blank'])
    (OUT / cfg['brace_file']).write_text(brace, encoding='utf-8')
    (OUT / cfg['blank_file']).write_text(blank, encoding='utf-8')
    combo = make_combo(lang, brace, blank, cfg['text'])
    assert 'fetch(' not in combo
    assert 'github.io' not in combo
    (OUT / cfg['combo_file']).write_text(combo, encoding='utf-8')

index = '''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Offline Downloads</title><style>body{font-family:system-ui;background:#f4f6f5;margin:0;color:#17231e}.w{max-width:900px;margin:auto;padding:20px}.c{background:#fff;border:1px solid #d7e0db;border-radius:16px;padding:18px;margin:14px 0}a{display:block;margin:8px 0;padding:13px 15px;border-radius:12px;background:#0b6b4b;color:#fff;text-decoration:none;font-weight:700}small{color:#66736d}</style></head><body><div class="w"><h1>Offline-Dateien / Archivos sin conexión / Offline files</h1><div class="c"><h2>Deutsch</h2><a href="Bogen_Setup_Assistent_v3_Offline_DE.html" download>Bogen-Setup Assistent v3 – Offline</a><a href="Standhoehen_Optimierer_v3_Offline_DE.html" download>Standhöhen-Optimierer v3 – Offline</a><a href="Blankschaft_Tuner_Offline_DE.html" download>Blankschaft-Tuner – Offline</a></div><div class="c"><h2>Español</h2><a href="Asistente_Puesta_a_Punto_v3_Offline_ES.html" download>Asistente de puesta a punto v3 – Sin conexión</a><a href="Optimizador_Fistmele_v3_Offline_ES.html" download>Optimizador de fistmele v3 – Sin conexión</a><a href="Afinador_Flecha_Desnuda_Offline_ES.html" download>Afinador de flecha desnuda – Sin conexión</a></div><div class="c"><h2>English</h2><a href="Bow_Setup_Assistant_v3_Offline_EN.html" download>Bow Setup Assistant v3 – Offline</a><a href="Brace_Height_Optimizer_v3_Offline_EN.html" download>Brace Height Optimizer v3 – Offline</a><a href="Bare_Shaft_Tuner_Offline_EN.html" download>Bare Shaft Tuner – Offline</a></div><div class="c"><small>© 2026 Rainer Blome · r.blome@rainer-blome.de</small></div></div></body></html>'''
(OUT / 'index.html').write_text(index, encoding='utf-8')

for p in sorted(OUT.glob('*.html')):
    print(p.name, p.stat().st_size)

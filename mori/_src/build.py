#!/usr/bin/env python3
"""Assemble /mori/*.html from page fragments in ./src.

Fragment shorthand:
  [[한국어||English]]      -> <span lang="ko">..</span><span lang="en">..</span>
  <tbl [class]> ... </tbl> -> table; first line = header, cells split by ' | '
  `code`, **bold**         -> <code>, <b>   (not applied inside <pre>)
"""
import re, sys, html, pathlib

HERE = pathlib.Path(__file__).parent
OUT = pathlib.Path(sys.argv[1])
REPO = "https://github.com/saranf/mori-soc"

PAGES = [
    dict(id="index", file="index.html", group="overview",
         ko="MORI 소개", en="Overview",
         tko="MORI SOC — 감사 대응형 보안 운영 플랫폼", ten="MORI SOC — audit-ready security operations platform",
         dko="MORI SOC 는 Zabbix · Fleet · Wazuh · Trivy · Loki 위에 읽기 전용으로 얹혀 ISMS-P / ISO 27001 증적을 자동으로 쌓는 오픈소스 보안 운영 플랫폼입니다.",
         secs=[]),
    dict(id="architecture", file="architecture.html", group="arch",
         ko="아키텍처", en="Architecture",
         tko="아키텍처 · MORI SOC", ten="Architecture · MORI SOC",
         dko="MORI SOC 의 증적 층 구조, 서비스 구성, 데이터 흐름, 데이터 모델, 권한, 증적 무결성 장치.",
         secs=[("position", "MORI 의 위치", "Where MORI sits"), ("services", "서비스 구성", "Services"), ("dataflow", "데이터 흐름", "Data flow"), ("data-model", "데이터 모델", "Data model"), ("rbac", "인증 · 권한", "Auth · roles"), ("integrity", "증적 무결성", "Evidence integrity"), ("scale", "확장성 · 스택", "Scale · stack")]),
    dict(id="features", file="features.html", group="arch",
         ko="핵심 기능", en="Core features",
         tko="핵심 기능 · MORI SOC", ten="Core features · MORI SOC",
         dko="통제 카탈로그와 통제 운영, 증적 신뢰 층, 감사 실사용 기능, 개인정보 · 코드 리뷰 · 계정 · 취약점 모듈.",
         secs=[("catalog", "통제 카탈로그", "Control catalog"), ("governance", "통제 운영", "Control governance"), ("trust", "증적 신뢰 층", "Evidence trust"), ("audit", "감사 실사용", "Audit tooling"), ("ops", "트리아지 · 위험성", "Triage · risk"), ("code-review", "코드 리뷰 증적", "Code review"), ("privacy", "개인정보 3.x", "Privacy 3.x"), ("accounts", "계정 거버넌스", "Accounts"), ("platform", "플랫폼 공통", "Platform")]),
    dict(id="integrations", file="integrations.html", group="arch",
         ko="연동 · 배포", en="Integrations · deployment",
         tko="연동 · 배포 · MORI SOC", ten="Integrations · deployment · MORI SOC",
         dko="Zabbix · Fleet · Trivy · Wazuh · 코드 리뷰 · LDAP 연동, 데모와 브라운필드 시작, compose 프로필, 운영 · 백업.",
         secs=[("connectors", "커넥터", "Connectors"), ("quickstart", "시작하기", "Getting started"), ("production", "운영 전환", "Production"), ("backup", "백업 · 업그레이드", "Backup · upgrade"), ("status", "지금 · 다음", "Status")]),
    dict(id="api", file="api.html", group="ref",
         ko="API 레퍼런스", en="API reference",
         tko="API 레퍼런스 · MORI SOC", ten="API reference · MORI SOC",
         dko="MORI SOC REST API 레퍼런스: 인증, 분류별 212개 엔드포인트, 증적 인제스트.",
         secs=[("auth", "인증", "Authentication"), ("ingest", "증적 보내기", "Sending evidence"), ("endpoints", "엔드포인트", "Endpoints")]),
]
GROUPS = [("overview", "시작하기", "Get started"), ("arch", "문서", "Docs"), ("ref", "레퍼런스", "Reference")]

GH_SVG = '<svg width="15" height="15" viewBox="0 0 16 16" fill="currentColor" aria-hidden="true"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/></svg>'


def bi(ko, en):
    return f'<span lang="ko">{ko}</span><span lang="en">{en}</span>'


def inline(s):
    s = re.sub(r"`([^`\n]+)`", lambda m: "<code>" + html.escape(m.group(1), quote=False) + "</code>", s)
    return s


def tbl(m):
    cls = m.group(1).strip()
    lines = [l.strip() for l in m.group(2).strip().splitlines() if l.strip()]
    head = [c.strip() for c in lines[0].split(" | ")]
    out = [f'<div class="tbl {cls}"><table><thead><tr>']
    out += [f"<th>{c}</th>" for c in head]
    out.append("</tr></thead><tbody>")
    for l in lines[1:]:
        cells = [c.strip() for c in l.split(" | ")]
        out.append("<tr>" + "".join(f"<td>{c}</td>" for c in cells) + "</tr>")
    out.append("</tbody></table></div>")
    return "".join(out)


def expand(src):
    parts = re.split(r"(<pre[\s\S]*?</pre>)", src)
    res = []
    for p in parts:
        if not p.startswith("<pre"):
            p = re.sub(r"<tbl([^>]*)>([\s\S]*?)</tbl>", tbl, p)
            p = inline(p)
        res.append(p)
    src = "".join(res)
    src = re.sub(r"\[\[([\s\S]*?)\|\|([\s\S]*?)\]\]", lambda m: bi(m.group(1), m.group(2)), src)
    return src


def header(page, landing):
    nav = [("index", "소개", "Overview", "index.html"),
           ("architecture", "아키텍처", "Architecture", "architecture.html"),
           ("features", "핵심 기능", "Features", "features.html"),
           ("integrations", "연동 · 배포", "Integrations", "integrations.html"),
           ("api", "API", "API", "api.html")]
    links = "".join(
        f'<a href="{f}"' + (' aria-current="page"' if pid == page["id"] else "") + f'>{bi(k, e)}</a>'
        for pid, k, e, f in nav)
    menu = "" if landing else '<button type="button" class="icon-btn menu-btn" id="menuBtn" aria-label="Menu"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M4 7h16M4 12h16M4 17h16"/></svg></button>'
    return f'''<header class="g-top">
  <div class="wrap">
    {menu}
    <a class="g-brand" href="index.html" aria-label="MORI SOC home"><span class="mk" aria-hidden="true">M</span>MORI SOC<span class="chip">{'v0.6 alpha' if landing else 'Docs'}</span></a>
    <a class="g-by" href="../index.html">by RM Studio</a>
    <nav class="g-nav" aria-label="MORI SOC">{links}</nav>
    <div class="g-tools">
      <a class="gh-link" href="{REPO}" target="_blank" rel="noopener">{GH_SVG}<span>GitHub</span></a>
      <div class="seg" role="group" aria-label="Language"><button type="button" data-set-lang="ko">KO</button><button type="button" data-set-lang="en">EN</button></div>
      <button type="button" class="icon-btn" id="themeBtn" aria-label="Toggle theme"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg></button>
    </div>
  </div>
</header>'''


def sidebar(page):
    out = ['<aside class="side" aria-label="Documentation">']
    for gid, gk, ge in GROUPS:
        out.append(f'<div class="grp">{bi(gk, ge)}</div>')
        for p in PAGES:
            if p["group"] != gid:
                continue
            cur = ' aria-current="page"' if p["id"] == page["id"] else ""
            out.append(f'<a href="{p["file"]}"{cur}>{bi(p["ko"], p["en"])}</a>')
            if p["secs"]:
                href = "" if p["id"] == page["id"] else p["file"]
                if p["id"] == page["id"]:
                    out.append('<div class="sub-links">' + "".join(
                        f'<a href="{href}#{sid}">{bi(k, e)}</a>' for sid, k, e in p["secs"]) + "</div>")
    out.append(f'<div class="grp">{bi("링크", "Links")}</div>')
    out.append(f'<a href="{REPO}" target="_blank" rel="noopener">GitHub ↗</a>')
    out.append(f'<a href="{REPO}/blob/main/CHANGELOG.md" target="_blank" rel="noopener">Changelog ↗</a>')
    out.append(f'<a href="{REPO}/blob/main/README_FULL.md" target="_blank" rel="noopener">README (full) ↗</a>')
    out.append(f'<a href="../index.html">RM Studio ↗</a>')
    out.append(f'<div class="ver">{bi("MORI SOC 0.6.0 (alpha) 기준", "Based on MORI SOC 0.6.0 (alpha)")}</div>')
    out.append("</aside>")
    return "\n".join(out)


def pager(page):
    docs = [p for p in PAGES]
    i = docs.index(page)
    prev = docs[i - 1] if i > 0 else None
    nxt = docs[i + 1] if i + 1 < len(docs) else None
    s = '<nav class="pager" aria-label="Pages">'
    if prev:
        s += f'<a class="prev" href="{prev["file"]}"><small>{bi("이전", "Previous")}</small><b>← {bi(prev["ko"], prev["en"])}</b></a>'
    if nxt:
        s += f'<a class="next" href="{nxt["file"]}"><small>{bi("다음", "Next")}</small><b>{bi(nxt["ko"], nxt["en"])} →</b></a>'
    return s + "</nav>"


FOOT = f'''<footer class="g-foot"><div class="wrap">
  <span>© 2026 RM Studio · MORI SOC is licensed under the Apache License 2.0</span>
  <span><a href="{REPO}" target="_blank" rel="noopener">GitHub</a> · <a href="../index.html">rm-studio-org.github.io</a></span>
</div></footer>'''


def page_html(page, body):
    landing = page["id"] == "index"
    head = f'''<!doctype html>
<html lang="ko" data-lang="ko" data-title-ko="{html.escape(page['tko'])}" data-title-en="{html.escape(page['ten'])}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(page['tko'])}</title>
<meta name="description" content="{html.escape(page['dko'])}">
<meta property="og:title" content="{html.escape(page['ten'])}">
<meta property="og:description" content="{html.escape(page['dko'])}">
<meta property="og:type" content="website">
<meta property="og:image" content="https://rm-studio-org.github.io/assets/banner.png">
<link rel="icon" href="assets/mori-mark.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css">
<link rel="stylesheet" href="../assets/product-base.css">
<link rel="stylesheet" href="assets/mori.css">
<script>
(function(){{var d=document.documentElement,l=null,t=null;
try{{var q=new URLSearchParams(location.search).get('lang');if(q==='ko'||q==='en')l=q;}}catch(e){{}}
try{{l=l||localStorage.getItem('rm-lang');t=localStorage.getItem('rm-theme');}}catch(e){{}}
if(!l)l=(navigator.language||'ko').toLowerCase().indexOf('ko')===0?'ko':'en';
d.setAttribute('data-lang',l);d.lang=l;if(t==='light'||t==='dark')d.setAttribute('data-theme',t);}})();
</script>
</head>
<body>
'''
    if landing:
        main = f"{header(page, True)}\n<main>\n{body}\n</main>\n{FOOT}"
    else:
        crumb = f'<div class="crumb"><a href="index.html">MORI SOC</a><span>/</span><span>{bi(dict((g[0], g[1]) for g in GROUPS)[page["group"]], dict((g[0], g[2]) for g in GROUPS)[page["group"]])}</span></div>'
        main = f'''{header(page, False)}
<div class="docs">
{sidebar(page)}
<main class="content" id="main">
{crumb}
{body}
{pager(page)}
</main>
<nav class="toc" id="toc" aria-label="On this page"><div class="t">{bi("이 페이지", "On this page")}</div><div class="list"></div></nav>
</div>
{FOOT}'''
    return head + main + '\n<script src="assets/mori.js"></script>\n</body>\n</html>\n'


for p in PAGES:
    src = (HERE / "src" / p["file"]).read_text()
    src = re.sub(r"<!--include:([\w.]+)-->", lambda m: (HERE / "src" / m.group(1)).read_text(), src)
    (OUT / p["file"]).write_text(page_html(p, expand(src)))
    print("wrote", p["file"])

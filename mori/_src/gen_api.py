#!/usr/bin/env python3
"""Generate src/_endpoints.html for MORI SOC.

usage:
  python3 routes.py <mori-soc>/src/mori_soc/api   # writes routes.json (FastAPI decorators, AST)
  python3 gen_api.py routes.json
Descriptions live in desc.py ("METHOD path": (ko, en)); the script fails if one is missing.
"""
import json, sys, html, re, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from desc import D

HERE = pathlib.Path(__file__).parent
routes = [r for r in json.load(open(sys.argv[1])) if r["schema"]]

# Tag order and descriptions follow MORI_OPENAPI_TAGS in api/server.py.
# The last two groups collect routes that have no tag in the source.
GROUPS = [
    ("Health", "health", "헬스 · 상태", "Health", "헬스체크 · 상태 — 라이브니스 / 레디니스 프로브, 메트릭.", "Health checks — liveness / readiness probes and metrics."),
    ("Auth", "auth", "인증 · 세션", "Auth", "로그인 / 로그아웃, 가입 승인 요청.", "Sign-in / sign-out and sign-up approval requests."),
    ("Compliance", "compliance", "통제 점검 · 심사 준비", "Compliance", "PDCA, SoA(적용선언서), 통제 카탈로그 · 증적, 증적 신선도 · 감사 표본 · 전체 증적 ZIP, Gap.", "PDCA, SoA, control catalog · evidence, freshness · audit sampling · full evidence ZIP, gaps."),
    ("Governance", "governance", "통제 운영 플랫폼", "Control governance", "Framework · Version(불변) · AssuranceCycle · EvidenceContract, as-of 재현, 이벤트 원장.", "Framework · version (immutable) · assurance cycle · evidence contract, as-of replay, event ledger."),
    ("Privacy", "privacy", "개인정보 3.x", "Privacy (3.x)", "처리흐름도(SVG), 처리업무, 외부 수신자 구분, 처리방침 대조, 개인정보 증적 패키지.", "Data-flow diagram (SVG), processing tasks, external recipients, policy comparison, privacy evidence package."),
    ("Vulnerabilities", "vulns", "취약점 조치", "Vulnerabilities", "CVE 조치 · 예외 · 기한(예외 자동연장 금지), 위험성 평가.", "CVE remediation · exceptions · due dates (no auto-extension), risk assessment."),
    ("Assets", "assets", "자산 · 담당자", "Assets", "인벤토리, 담당자 · 중요도, 인증범위 커버리지, 감사로그 무결성.", "Inventory, owners · importance, certification-scope coverage, audit-log integrity."),
    ("Accounts", "accounts", "계정 거버넌스", "Account governance", "로컬 계정 × LDAP × 승인대장 대조, 퇴사자 · 미승인 sudo · 휴면 검출.", "Local accounts × LDAP × approval register; leavers, unapproved sudo, dormant accounts."),
    ("Incidents", "incidents", "인시던트", "Incidents", "확정 경보의 인시던트 승격 · 타임라인.", "Promote confirmed alerts to incidents · timeline."),
    ("Alerts", "alerts", "경보 트리아지", "Alert triage", "확정 / 예외 / 담당자, 옵트인 Zabbix write-back.", "Confirm / exception / owner, opt-in Zabbix write-back."),
    ("Sources", "sources", "증적 소스 수집 (ingest)", "Evidence sources (ingest)", "Trivy · Wazuh · code-review · privacy-flow · evidence push, OIDC 검증, 스캐너 배포.", "Trivy · Wazuh · code-review · privacy-flow · evidence push, OIDC verification, scanner distribution."),
    ("Zabbix", "zabbix", "증적 소스: Zabbix", "Source: Zabbix", "모니터링 호스트 (read-only).", "Monitored hosts (read-only)."),
    ("Trivy", "trivy", "증적 소스: Trivy", "Source: Trivy", "컨테이너 · 이미지 취약점 스캔 결과.", "Container · image vulnerability scan results."),
    ("Fleet", "fleet", "증적 소스: Fleet", "Source: Fleet", "Fleet / osquery 엔드포인트 인벤토리.", "Fleet / osquery endpoint inventory."),
    ("Admin", "admin", "관리자", "Admin", "콘솔 운영, 사용자 · 권한 · LDAP · 감사로그.", "Console operations, users · permissions · LDAP · audit logs."),
    ("Settings", "settings", "설정", "Settings", "위험 DoA 기준.", "Risk DoA criteria."),
    ("Onboarding", "onboarding", "온보딩", "Onboarding", "첫 실행 체크리스트, 커넥터 상태 · 연결 테스트, 스캔 설정, 데모 → 실전 전환.", "First-run checklist, connector status · tests, scan setup, demo → production."),
    ("_dash", "dashboard", "대시보드 · 자연어 질의", "Dashboard · NLQ", "대시보드 요약 · 개인 설정, 자연어 질의, 안내서. (소스에 태그 없음)", "Dashboard summary · preferences, natural-language query, guides. (untagged in source)"),
    ("_hook", "webhooks", "웹훅", "Webhooks", "알림 웹훅 등록 · 테스트. (소스에 태그 없음)", "Notification webhook registration · test. (untagged in source)"),
]
UNTAGGED = {"/assets": "Assets", "/health": "Health", "/webhooks": "_hook"}

def group_of(r):
    if r["tags"]:
        return r["tags"][0]
    for pre, g in UNTAGGED.items():
        if r["p"].startswith(pre):
            return g
    return "_dash"

ORDER = {"GET": 0, "POST": 1, "PUT": 2, "PATCH": 3, "DELETE": 4}
by = {}
for r in routes:
    key = f'{r["m"]} {r["p"]}'
    if key not in D:
        sys.exit("missing description: " + key)
    by.setdefault(group_of(r), []).append((r["p"], r["m"], *D[key]))

out, total = [], 0
for tag, gid, ko, en, dko, den in GROUPS:
    eps = sorted(by.pop(tag, []), key=lambda e: (e[0], ORDER[e[1]]))
    if not eps:
        continue
    total += len(eps)
    out.append(f'<div class="api-group" id="api-{gid}">')
    out.append(f'<div class="gh"><h3 id="g-{gid}" data-notoc>[[{ko}||{en}]]</h3><span class="c">{len(eps)}</span></div>')
    out.append(f'<p class="gd">[[{dko}||{den}]]</p>')
    out.append('<div class="eps">')
    for path, m, sko, sen in eps:
        p = re.sub(r"\{([^}]+)\}", r"<em>{\1}</em>", html.escape(path))
        out.append(f'<div class="ep"><span class="m {m.lower()}">{m}</span><span class="p">{p}</span><span class="d">[[{html.escape(sko)}||{html.escape(sen)}]]</span></div>')
    out.append("</div></div>")
assert not by, list(by)
(HERE / "src" / "_endpoints.html").write_text("\n".join(out) + "\n")
print("endpoints:", total)

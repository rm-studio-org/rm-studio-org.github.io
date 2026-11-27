#!/usr/bin/env python3
"""Generate src/_endpoints.html from the Georu OpenAPI snapshot.  usage: gen_api.py <openapi.json>"""
import json, sys, html, re, pathlib

spec = json.load(open(sys.argv[1]))
OUT = pathlib.Path(__file__).parent / "src" / "_endpoints.html"

# (tag in spec, id, ko name, en name, en description)
GROUPS = [
    ("마이그레이션 실행", "run", "마이그레이션 실행", "Migration run", "Run a table, stop a Job, fill missing rows and manage cron schedules."),
    ("실행 그룹", "groups", "실행 그룹", "Execution groups", "Progress, results (success · failed · not run) and stop for date-split and scenario runs."),
    ("시나리오 이관", "scenarios", "시나리오 이관", "Scenarios", "Run steps (tables) and date ranges as sequential Jobs in a defined order. Progress and stop are on the execution-group API."),
    ("Execution Gate", "gate", "실행 게이트", "Execution gate", "Single-run rule: see the unit currently running, force-release the gate."),
    ("Migration Chunk Management", "chunks", "청크", "Chunks", "Per-chunk status and selective re-run."),
    ("실행 전 점검·알림", "precheck", "실행 전 점검 · 알림", "Precheck · notifications", "Precheck (writes nothing to the target), unfinished-code status, UI notifications, group-run summary."),
    ("Report", "report", "보고서", "Reports", "Migration result reports and CSV · XLSX · PDF exports."),
    ("Excel Load", "excel", "엑셀 이관", "Excel load", "Load an uploaded Excel file (TOBE column headers) through the table migration pipeline."),
    ("Project", "project", "이관 진행", "Migration progress", "Recommended phases, checklist and Excel template."),
    ("System Status", "status", "시스템 상태", "System status", "System status and monitoring."),
    ("시스템 지표", "metrics", "시스템 지표", "System metrics", "Current values for the top summary bar and 5-minute metric history."),
    ("운영 기록 정리", "cleanup", "운영 기록 정리", "Operations-store cleanup", "User-initiated cleanup of old records in the operations store (no automatic cleanup)."),
    ("Sequence v1", "sequence", "채번", "Numbering (sequence v1)", "Sequence control table: query, bulk reserve, set value, sync to MAX."),
    ("Generator", "generator", "이관 설계 도구", "Design tools", "Code generation, relationship analysis, draft mapping definition."),
    ("내 계정", "account", "내 계정", "My account", "The signed-in user's own account info and password change."),
    ("사용자 관리", "users", "사용자 관리", "User management", "Add, edit, suspend, unlock, reset password and delete UI users (super administrator only). 404 SECURITY_DISABLED when sign-in is off."),
    ("권한 관리", "roles", "권한 관리", "Role management", "Per-role menu levels and idle lock (super administrator only). 404 SECURITY_DISABLED when sign-in is off."),
    ("화면 내부용", "internal", "화면 내부용", "UI internal", "Read-only queries used by the operation UI. They follow the screens and are not a stable integration API."),
]

EN = {
 "특정 테이블 마이그레이션 실행": "Run migration for one table",
 "실행 중인 마이그레이션 중지": "Stop a running migration",
 "스케줄 즉시 실행": "Trigger a schedule now",
 "스케줄 재개": "Resume a schedule",
 "스케줄 일시정지": "Pause a schedule",
 "일시정지한 스케줄 전체 재개": "Resume all paused schedules",
 "활성 스케줄 전체 일시정지": "Pause all active schedules",
 "빠진 행 채우기 확인": "Check fill-missing-rows eligibility",
 "빠진 행 채우기 실행": "Fill missing rows",
 "등록된 스케줄 목록": "List schedules",
 "스케줄 주기 기록": "Schedule run history",
 "Cron 표현식 유효성 검증": "Validate a cron expression",
 "마이그레이션 스케줄 취소": "Cancel a schedule",
 "실행 그룹 중지 요청": "Request group stop",
 "실행 그룹 목록": "List execution groups",
 "실행 그룹 상세": "Execution group detail",
 "시나리오 정의": "Scenario definition",
 "사용자 정의 시나리오 수정": "Update a user-defined scenario",
 "사용 여부 변경": "Enable / disable",
 "시나리오 목록": "List scenarios",
 "사용자 정의 시나리오 추가": "Add a user-defined scenario",
 "시나리오 실행": "Run a scenario",
 "시나리오 사전 확인": "Pre-confirm a scenario",
 "정의 검증": "Validate a definition",
 "분할 구간 미리보기": "Preview split ranges",
 "저장 전 사전 확인": "Pre-confirm before saving",
 "변경 이력": "Change history",
 "이력 시점 정의 전문": "Full definition at a history point",
 "정의 JSON 내려받기": "Download definition JSON",
 "다음 자동 채번 id": "Next auto-assigned id",
 "게이트 강제 해제": "Force-release the gate",
 "게이트 상태": "Gate status",
 "청크 재실행": "Re-run chunks",
 "청크 진행률 조회": "Chunk progress",
 "묶음 실행 종료 (요약 알림)": "Finish a group run (summary alert)",
 "실행 전 점검 시작": "Start a precheck",
 "UI 알림 목록": "UI notifications",
 "미완 코드 현황": "Unfinished-code status",
 "안내서 원문 (Markdown)": "Guide source (Markdown)",
 "실행 전 점검 결과": "Precheck result",
 "실행 전 점검 결과 내보내기 (csv / xlsx)": "Export precheck result (csv / xlsx)",
 "최근 실행 전 점검 목록": "Recent prechecks",
 "내보내기 목록": "List exports",
 "비동기 zip 내보내기 요청": "Request an async zip export",
 "기간 요약 보고서 (json/pdf/xlsx/csv)": "Period summary report (json/pdf/xlsx/csv)",
 "Job 목록 (json/csv/xlsx)": "Job list (json/csv/xlsx)",
 "Job 1건 결과 보고서 (json/pdf/xlsx)": "Single Job report (json/pdf/xlsx)",
 "Job 로그 (json/csv)": "Job logs (json/csv)",
 "Job 청크 상태 (json/csv)": "Job chunk status (json/csv)",
 "내보내기 상태": "Export status",
 "내보내기 삭제": "Delete an export",
 "내보내기 zip 다운로드": "Download export zip",
 "파일 목록": "List files",
 "업로드 (저장 후 즉시 검증)": "Upload (validated immediately)",
 "재검증": "Re-validate",
 "템플릿 xlsx (헤더 + 컬럼 설명 시트)": "Template xlsx (header + column notes sheet)",
 "상태별 건수": "Counts by status",
 "분할 안내 계산 (데이터 행 수·열 수 → 파일당 행 수·파일별 범위)": "Split plan (rows · columns → rows per file · ranges)",
 "크기 제한 (업로드 상한·xlsx 셀 상한·권장값·Excel 형식 한계)": "Size limits (upload · xlsx cells · recommended · Excel format)",
 "파일 1건": "File detail",
 "삭제 (실행 중 제외)": "Delete (not while running)",
 "검증 보고서·실행 오류 목록": "Validation report · run errors",
 "미리보기 (헤더·앞 N행·컬럼 대응표)": "Preview (header · first N rows · column binding)",
 "검증·실행 오류 목록 xlsx": "Validation · run errors xlsx",
 "원본 다운로드": "Download original",
 "컬럼 대응표 (타겟 컬럼 ↔ DTO 프로퍼티, 필수·감사·채번)": "Column binding (target column ↔ DTO property, required · audit · numbering)",
 "항목 체크 · 메모": "Check item · memo",
 "엑셀 올리기": "Upload Excel",
 "권장 단계로 되돌리기": "Reset to recommended phases",
 "체크리스트": "Checklist",
 "기록": "Events",
 "엑셀 내려받기": "Download Excel",
 "실행 중인 작업 목록 조회": "Running jobs",
 "플러그인 목록 및 상태": "Plugins and status",
 "성능 메트릭": "Performance metrics",
 "시스템 전체 현황": "System overview",
 "로그 목록": "Logs",
 "로그 파일 목록": "Log files",
 "작업 실행 이력": "Job execution history",
 "데이터베이스 연결 상태": "Database connection status",
 "현재 시스템 지표": "Current metrics",
 "시스템 지표 이력": "Metric history",
 "정리 실행": "Run cleanup",
 "정리 미리보기 (건수만)": "Preview cleanup (counts only)",
 "현재값 조회": "Current value",
 "값 설정 (운영 보정)": "Set value (operational fix)",
 "MAX 동기화": "Sync to MAX",
 "일괄 선점": "Bulk reserve",
 "관리 테이블 전체 목록": "All control rows",
 "정책 목록": "Policies",
 "업체 규칙 파일 읽기": "Read vendor rules file",
 "현재 규칙 내려받기": "Download current rules",
 "관계 분석 검사": "Check relationship analysis",
 "관계 분석 xlsx 내려받기": "Download relationship analysis xlsx",
 "매핑 정의서 초안 xlsx 내려받기": "Download draft mapping xlsx",
 "매핑 정의서 초안 검사": "Check draft mapping",
 "코드 zip 내려받기": "Download generated code zip",
 "코드 생성 검사": "Check code generation",
 "업체 규칙 파일 양식": "Vendor rules template",
 "테이블 정의 예제 양식": "Table definition sample",
 "화면 기본값": "Screen defaults",
 "공통코드 표 예제 양식": "Common-code table sample",
 "최근 실행 기록": "Recent runs",
 "코드 생성 예제 양식": "Code generation sample",
 "내 비밀번호 바꾸기": "Change my password",
 "내 계정 정보 (이름 · 권한 · 메뉴별 단계 · 유휴 잠금)": "My account (name · role · menu levels · idle lock)",
 "사용자 고치기 (이름 · 권한)": "Edit user (name · role)",
 "사용자 삭제": "Delete user",
 "사용 중지 · 다시 사용": "Suspend · re-enable",
 "사용자 목록": "List users",
 "사용자 추가 (초기 비밀번호는 관리자가 정함, 첫 로그인 때 변경 강제)": "Add user (admin sets initial password; change forced at first sign-in)",
 "로그인 실패 잠금 풀기": "Unlock after failed sign-ins",
 "비밀번호 초기화 (다음 로그인 때 변경 강제)": "Reset password (change forced at next sign-in)",
 "권한 고치기 (관리자 권한은 유휴 잠금만)": "Edit role (admin role: idle lock only)",
 "권한 삭제 — 그 권한의 사용자도 함께 지움": "Delete role — also deletes its users",
 "권한 목록 (사용자 수 포함)": "List roles (with user counts)",
 "권한 추가": "Add role",
 "그 권한의 사용자 목록 (삭제 전 확인)": "Users in a role (check before delete)",
 "권한표에 쓰는 메뉴 목록": "Menus used in the permission table",
 "타겟 테이블 현재 건수 (화면용)": "Current target row count (UI)",
 "시나리오 설계용 테이블 카탈로그": "Table catalog for scenario design",
 "실행 1건 상세 (화면용)": "Run detail (UI)",
 "화면 공통 정보 (환경 · 프로파일)": "Common UI info (environment · profile)",
}

ORDER = {"get": 0, "post": 1, "put": 2, "delete": 3, "patch": 4}
by_tag = {}
missing = []
for path, ops in spec["paths"].items():
    for m, o in ops.items():
        if m not in ORDER:
            continue
        tag = (o.get("tags") or ["-"])[0]
        ko = o.get("summary", "")
        en = EN.get(ko)
        if en is None:
            missing.append(ko); en = ko
        by_tag.setdefault(tag, []).append((path, m, ko, en))
if missing:
    sys.exit("missing EN: %r" % missing)

tag_desc = {t["name"]: t.get("description", "") for t in spec.get("tags", [])}
total = 0
out = []
for tag, gid, ko, en, en_desc in GROUPS:
    eps = sorted(by_tag.pop(tag), key=lambda e: (e[0], ORDER[e[1]]))
    total += len(eps)
    badge = ' <span class="badge">[[안정 API 아님||not a stable API]]</span>' if gid == "internal" else ""
    out.append(f'<div class="api-group" id="api-{gid}">')
    out.append(f'<div class="gh"><h3 id="g-{gid}" data-notoc>[[{ko}||{en}]]</h3><span class="c">{len(eps)}</span>{badge}</div>')
    out.append(f'<p class="gd">[[{html.escape(tag_desc.get(tag, ""))}||{html.escape(en_desc)}]]</p>')
    out.append('<div class="eps">')
    for path, m, sko, sen in eps:
        p = re.sub(r"\{([^}]+)\}", r"<em>{\1}</em>", html.escape(path))
        out.append(f'<div class="ep"><span class="m {m}">{m.upper()}</span><span class="p">{p}</span><span class="d">[[{html.escape(sko)}||{html.escape(sen)}]]</span></div>')
    out.append("</div></div>")
assert not by_tag, by_tag
OUT.write_text("\n".join(out) + "\n")
print("endpoints:", total, "groups:", len(GROUPS))

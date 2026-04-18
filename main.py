"""
Schedule Dashboard Manager
포르쉐 타이칸 실시간 일정 대시보드 - 관리자 도구
"""

import json
import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import threading

# GitPython 임포트 (없으면 설치 안내)
try:
    from git import Repo, InvalidGitRepositoryError, GitCommandError
    GIT_AVAILABLE = True
except ImportError:
    GIT_AVAILABLE = False

# ─────────────────────────────────────────────
#  설정 (사용자 환경에 맞게 수정)
# ─────────────────────────────────────────────
SCHEDULE_FILE = "schedule.json"   # JSON 파일 경로 (main.py 와 동일 폴더)
REPO_PATH     = "."               # Git 저장소 루트 (현재 폴더)
COMMIT_PREFIX = "📅 일정 업데이트"   # 커밋 메시지 앞에 붙는 텍스트

# 색상 테마 (Porsche Luxury Dark)
BG        = "#0a0a0a"
BG2       = "#111111"
BG3       = "#1a1a1a"
GOLD      = "#c9a84c"
GOLD_LT   = "#e8c97a"
WHITE     = "#f0f0f0"
GRAY      = "#555555"
RED_ACC   = "#c0392b"
GREEN_ACC = "#27ae60"

# ─────────────────────────────────────────────
#  JSON 헬퍼
# ─────────────────────────────────────────────

def load_schedule() -> list:
    if not os.path.exists(SCHEDULE_FILE):
        return []
    try:
        with open(SCHEDULE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, IOError):
        return []


def save_schedule(items: list) -> None:
    payload = {
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "items": items
    }
    with open(SCHEDULE_FILE, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


# ─────────────────────────────────────────────
#  Git 헬퍼
# ─────────────────────────────────────────────

def git_push(message: str, status_callback=None) -> tuple[bool, str]:
    """
    git add schedule.json → commit → push
    Returns (success: bool, message: str)
    """
    if not GIT_AVAILABLE:
        return False, "GitPython 라이브러리가 설치되지 않았습니다.\n`pip install gitpython` 을 실행하세요."
    try:
        repo = Repo(REPO_PATH)
        repo.index.add([SCHEDULE_FILE])
        if not repo.index.diff("HEAD"):
            return True, "변경 사항 없음 (커밋 생략)"
        repo.index.commit(f"{COMMIT_PREFIX}: {message}")
        if status_callback:
            status_callback("GitHub 에 푸시 중...")
        origin = repo.remote(name="origin")  # noqa: F841
        try:
            branch = repo.active_branch.name
        except TypeError:
            branch = "main"
        repo.git.push("--set-upstream", "--force", "origin", branch)
        return True, "✅ GitHub 에 성공적으로 푸시되었습니다."
    except InvalidGitRepositoryError:
        return False, "Git 저장소를 찾을 수 없습니다.\n`git init` 및 원격 저장소 설정을 확인하세요."
    except GitCommandError as e:
        return False, f"Git 오류:\n{str(e)}"
    except Exception as e:
        return False, f"알 수 없는 오류:\n{str(e)}"


# ─────────────────────────────────────────────
#  GUI 앱
# ─────────────────────────────────────────────

class ScheduleApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("📅  타이칸 일정 관리자")
        self.geometry("820x680")
        self.resizable(True, True)
        self.configure(bg=BG)

        self.items: list = []  # [{"date": str, "time": str, "title": str, "location": str, "note": str}]
        self._build_ui()
        self._load_and_refresh()

    # ── UI 구성 ──────────────────────────────

    def _build_ui(self):
        # ── 헤더
        hdr = tk.Frame(self, bg=BG, pady=14)
        hdr.pack(fill="x", padx=20)

        tk.Label(hdr, text="T A Y C A N", font=("Georgia", 10, "bold"),
                 fg=GOLD, bg=BG).pack(side="left")
        tk.Label(hdr, text="  |  일정 관리자", font=("Helvetica", 10),
                 fg=GRAY, bg=BG).pack(side="left")

        self.status_var = tk.StringVar(value="준비")
        tk.Label(hdr, textvariable=self.status_var, font=("Helvetica", 9),
                 fg=GOLD, bg=BG).pack(side="right")

        # ── 구분선
        tk.Frame(self, bg=GOLD, height=1).pack(fill="x", padx=20)

        # ── 입력 패널
        form = tk.Frame(self, bg=BG2, pady=16, padx=20)
        form.pack(fill="x", padx=20, pady=(14, 0))

        tk.Label(form, text="새 일정 추가", font=("Georgia", 11, "bold"),
                 fg=GOLD, bg=BG2).grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 12))

        labels = ["날짜 (YYYY-MM-DD)", "시간 (HH:MM)", "제목", "장소", "비고"]
        self.entries = {}
        field_keys = ["date", "time", "title", "location", "note"]

        for i, (lbl, key) in enumerate(zip(labels, field_keys)):
            col = (i % 2) * 2
            row = (i // 2) + 1
            tk.Label(form, text=lbl, font=("Helvetica", 9), fg=GRAY, bg=BG2
                     ).grid(row=row, column=col, sticky="w", padx=(0, 6), pady=4)
            e = tk.Entry(form, font=("Helvetica", 11), fg=WHITE, bg=BG3,
                         insertbackground=GOLD, bd=0, relief="flat", width=28)
            e.grid(row=row, column=col + 1, sticky="ew", pady=4, padx=(0, 20))
            self.entries[key] = e

        # 날짜 기본값
        self.entries["date"].insert(0, datetime.now().strftime("%Y-%m-%d"))

        form.columnconfigure(1, weight=1)
        form.columnconfigure(3, weight=1)

        # ── 버튼 행
        btn_frame = tk.Frame(self, bg=BG, pady=10)
        btn_frame.pack(fill="x", padx=20)

        self._btn(btn_frame, "✚  일정 추가", self._add_item,
                  GOLD, BG, side="left")
        self._btn(btn_frame, "⬆  저장 & GitHub Push", self._save_and_push,
                  BG, GOLD, side="left", pl=8)
        self._btn(btn_frame, "🗑  전체 초기화", self._reset_all,
                  RED_ACC, WHITE, side="right")

        # ── 목록
        tk.Frame(self, bg=GOLD, height=1).pack(fill="x", padx=20, pady=(6, 0))

        list_frame = tk.Frame(self, bg=BG)
        list_frame.pack(fill="both", expand=True, padx=20, pady=(6, 10))

        cols = ("date", "time", "title", "location", "note")
        col_names = ("날짜", "시간", "제목", "장소", "비고")
        col_widths = (100, 65, 200, 160, 180)

        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Treeview",
                        background=BG3, foreground=WHITE,
                        fieldbackground=BG3, rowheight=34,
                        font=("Helvetica", 11))
        style.configure("Treeview.Heading",
                        background=BG2, foreground=GOLD,
                        font=("Helvetica", 10, "bold"), relief="flat")
        style.map("Treeview", background=[("selected", "#2a2200")])

        self.tree = ttk.Treeview(list_frame, columns=cols, show="headings",
                                  selectmode="browse")
        for col, name, width in zip(cols, col_names, col_widths):
            self.tree.heading(col, text=name)
            self.tree.column(col, width=width, anchor="w")

        vsb = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        # 행 삭제 (Delete 키)
        self.tree.bind("<Delete>", self._delete_selected)

        # ── 하단 안내
        foot = tk.Frame(self, bg=BG, pady=6)
        foot.pack(fill="x", padx=20)
        tk.Label(foot, text="Delete 키로 선택한 항목 삭제  |  저장 & Push 버튼으로 대시보드에 반영",
                 font=("Helvetica", 9), fg=GRAY, bg=BG).pack(side="left")

    @staticmethod
    def _btn(parent, text, cmd, fg, bg, side="left", pl=0):
        b = tk.Button(parent, text=text, command=cmd,
                      font=("Helvetica", 10, "bold"),
                      fg=fg, bg=bg, activeforeground=bg, activebackground=fg,
                      bd=0, padx=16, pady=8, cursor="hand2", relief="flat")
        b.pack(side=side, padx=(pl, 6))
        return b

    # ── 데이터 ───────────────────────────────

    def _load_and_refresh(self):
        raw = load_schedule()
        # 구버전(list) 호환
        if isinstance(raw, list):
            self.items = raw
        else:
            self.items = []
        self._refresh_tree()

    def _refresh_tree(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        sorted_items = sorted(self.items,
                              key=lambda x: (x.get("date", ""), x.get("time", "")))
        for item in sorted_items:
            self.tree.insert("", "end", values=(
                item.get("date", ""),
                item.get("time", ""),
                item.get("title", ""),
                item.get("location", ""),
                item.get("note", ""),
            ))
        self._set_status(f"총 {len(self.items)}개 일정 로드됨")

    def _add_item(self):
        title = self.entries["title"].get().strip()
        if not title:
            messagebox.showwarning("입력 오류", "제목은 필수 항목입니다.")
            return

        item = {
            "date":     self.entries["date"].get().strip(),
            "time":     self.entries["time"].get().strip(),
            "title":    title,
            "location": self.entries["location"].get().strip(),
            "note":     self.entries["note"].get().strip(),
        }
        self.items.append(item)
        self._refresh_tree()

        # 입력 초기화 (날짜 제외)
        for key in ("time", "title", "location", "note"):
            self.entries[key].delete(0, "end")
        self._set_status(f"'{title}' 추가됨 (미저장)")

    def _delete_selected(self, _event=None):
        sel = self.tree.selection()
        if not sel:
            return
        idx = self.tree.index(sel[0])
        sorted_items = sorted(self.items,
                              key=lambda x: (x.get("date", ""), x.get("time", "")))
        del_item = sorted_items[idx]
        self.items.remove(del_item)
        self._refresh_tree()
        self._set_status(f"'{del_item['title']}' 삭제됨 (미저장)")

    def _reset_all(self):
        if messagebox.askyesno("전체 초기화", "모든 일정을 삭제하시겠습니까?"):
            self.items.clear()
            self._refresh_tree()
            self._set_status("전체 초기화 완료 (미저장)")

    def _save_and_push(self):
        save_schedule(self.items)
        self._set_status("저장 완료. GitHub 에 푸시 중...")
        commit_msg = f"{len(self.items)}개 항목 ({datetime.now().strftime('%m/%d %H:%M')})"

        def _worker():
            ok, msg = git_push(commit_msg, status_callback=self._set_status)
            self.after(0, lambda: self._set_status(msg))
            if not ok:
                self.after(0, lambda: messagebox.showerror("Git 오류", msg))

        threading.Thread(target=_worker, daemon=True).start()

    def _set_status(self, text: str):
        self.status_var.set(text)


# ─────────────────────────────────────────────
#  엔트리포인트
# ─────────────────────────────────────────────

if __name__ == "__main__":
    if not GIT_AVAILABLE:
        print("[경고] GitPython 이 설치되지 않았습니다.")
        print("       pip install gitpython  을 실행한 후 다시 시작하세요.")
        print("       (GUI 는 실행되지만 Push 기능이 비활성화됩니다.)\n")

    app = ScheduleApp()
    app.mainloop()

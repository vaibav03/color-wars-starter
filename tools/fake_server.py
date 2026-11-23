#!/usr/bin/env python3
"""A local Color Wars server for testing your bot (level 2). No network, no account. Any key works.

  python3 tools/fake_server.py                       lobby, build, testing, paused, live, then over
  python3 tools/fake_server.py --start testing --hold    stay in TESTING (try --practice as often as you like)
  python3 tools/fake_server.py --testing 30 --live 120 --opponent house

Then, in a second terminal, point the bot at it:

  python3 bot.py --server http://127.0.0.1:8765 --check
  python3 bot.py --server http://127.0.0.1:8765 --practice     during TESTING
  python3 bot.py --server http://127.0.0.1:8765               plays when the phase turns LIVE

It answers GET /cw/phase, GET /cw/state, POST /cw/move, POST /cw/submission and POST /cw/dryrun
with the same JSON as the real server, and applies the kit's rules (colorwars.py) on the map of
simulate.py. You are Red. A Blue opponent moves once per second during LIVE.
The real server differs: it pairs you with a classmate, checks uploads in a sandbox and limits
each key to 2 requests per second.
"""
import argparse, json, os, subprocess, sys, tempfile, threading, time, uuid
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

KIT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, KIT)
from colorwars import COLS, ROWS, capture, legal_squares, name, threat, view   # noqa: E402
from simulate import CRYSTALS, OPPONENTS, new_board                                          # noqa: E402

PHASES = ("lobby", "build", "testing", "paused", "live")
UPLOAD_PHASES = ("lobby", "build", "testing", "window")
COOLDOWN = 1.0
CHOOSE_CHECK = """
import json, sys
sys.path.insert(0, sys.argv[1])
from strategy import choose
board, legal, base, targets = json.load(sys.stdin)
pick = choose(board, legal, base, targets, [])
print(json.dumps({"pick": pick, "legal": pick in legal}))
"""


class Game:
    def __init__(self, a):
        self.a, self.lock = a, threading.Lock()
        self.durations = {p: getattr(a, p) for p in PHASES}
        self.order = PHASES[PHASES.index(a.start):]
        self.began = time.time()
        self.seen, self.result = None, None
        self.version, self.practice = 0, {}
        self.reset()

    def clock(self):
        return time.time() + self.a.skew                # --skew: pretend the server clock is off

    def reset(self):
        self.owner, self.seq, self.last_accept, self.practice_used, self.verdicts = new_board(), 0, 0.0, False, []
        self.captured = None                            # crystal result; like the real server, LIVE runs to its end

    def phase(self):
        """(phase, ends_at as server clock seconds or None). Call with the lock held."""
        if self.result:
            return "over", None
        t, start = time.time() - self.began, 0.0
        for p in self.order:
            if self.a.hold:
                return p, None
            if t < start + self.durations[p]:
                return p, self.clock() + start + self.durations[p] - t
            start += self.durations[p]
        self.result = self.result or self.captured or self.judge()
        return "over", None

    def tick(self):
        """Phase changes: a fresh board at TESTING and at LIVE. Returns (phase, ends_at)."""
        p, ends = self.phase()
        if p != self.seen:
            if p in ("testing", "live"):
                self.reset()
            self.seen = p
        return p, ends

    def judge(self, crystal=None):
        red, blue = (sum(o == c for o in self.owner.values()) for c in ("red", "blue"))
        if crystal:
            return f"{crystal} wins (crystal)"
        if red != blue:
            return f"{'red' if red > blue else 'blue'} wins (territory {red}-{blue})"
        tr, tb = threat(self.owner, "red", CRYSTALS), threat(self.owner, "blue", CRYSTALS)
        return "draw" if tr == tb else f"{'red' if tr < tb else 'blue'} wins (threat)"

    def banner(self, p, ends):
        if p == "live":
            return "⚔️ LIVE · ends " + (datetime.fromtimestamp(ends - self.a.skew).strftime("%H:%M") if ends else "--:--")
        return {"lobby": "COLOR WARS · join now", "build": "BUILD · do not paint",
                "testing": "TESTING · one practice square", "paused": "⏸ PAUSED · match starts soon",
                "over": f"GAME OVER · {self.result}"}[p]

    def phase_info(self):
        p, ends = self.tick()
        return {"phase": p, "banner": self.banner(p, ends), "round": 0, "ends_at": ends,
                "server_time": self.clock(), "ai_locked": p in ("paused", "live")}

    def state(self):
        info = self.phase_info()
        board = view(self.owner, "red")
        info.update({"match_id": "fake-0", "alias": "you0", "color": "red", "base": CRYSTALS["red"], "targets": CRYSTALS["blue"],
                     "board": board, "legal": legal_squares(board, CRYSTALS["red"]), "seq": self.seq,
                     "last_verdicts": self.verdicts[-10:]})
        return info

    def move(self, who, square):
        p, _ = self.tick()
        rule, reason, changed = "ok", "", []
        before = dict(self.owner)
        if p == "over" or (p == "live" and self.captured):
            rule, reason = "finished", "the match is over"
        elif p not in ("testing", "live"):
            rule, reason = "not_live", f"moves are refused during {p}"
        elif p == "testing" and who == "red" and self.practice_used:
            rule, reason = "practice_used", "one practice square in TESTING"
        elif square not in self.owner:
            rule, reason = "bad_label", f"{square!r} is not a square"
        elif who == "red" and time.time() - self.last_accept < COOLDOWN:
            rule, reason = "cooldown", "one capture every 1s"
        elif not capture(self.owner, who, square, CRYSTALS):
            rule, reason = "illegal", "it doesn't touch your squares"
        if rule == "ok":
            changed = [[s, o] for s, o in self.owner.items() if before[s] != o]
            self.seq += 1
            if who == "red":
                self.last_accept = time.time()
                self.practice_used = self.practice_used or p == "testing"
            other = "blue" if who == "red" else "red"
            if all(self.owner[s] == who for s in CRYSTALS[other]) and p == "live":
                self.captured = self.judge(crystal=who)
        verdict = {"accepted": rule == "ok", "rule": rule, "reason": reason, "changed": changed, "seq": self.seq}
        if who == "red":
            self.verdicts.append({"square": square, **verdict})
        return verdict

    def opponent(self):
        brain = OPPONENTS[self.a.opponent]
        while True:
            time.sleep(1.0)
            with self.lock:
                if self.tick()[0] != "live":
                    continue
                board = view(self.owner, "blue")
                legal = legal_squares(board, CRYSTALS["blue"])
                if legal:
                    self.move("blue", brain(board, legal, CRYSTALS["blue"], CRYSTALS["red"], []))

    def check_upload(self, files):
        """The checks the real server runs before its sandbox: strategy.py imports and choose() answers."""
        checks = {"files": len(files), "strategy.py": "strategy.py" in files,
                  "requirements.txt": "not installed by the fake server" if "requirements.txt" in files else "none"}
        if not checks["strategy.py"]:
            return checks, "strategy.py is missing"
        with tempfile.TemporaryDirectory() as tmp:
            for rel, text in files.items():
                path = os.path.join(tmp, rel)
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, "w") as f:
                    f.write(text)
            for kit_file in ("colorwars.py",):          # the server supplies the kit's own helpers
                with open(os.path.join(KIT, kit_file)) as src, open(os.path.join(tmp, kit_file), "w") as dst:
                    dst.write(src.read())
            board = view(new_board(), "red")
            payload = json.dumps([board, legal_squares(board, CRYSTALS["red"]), CRYSTALS["red"], CRYSTALS["blue"]])
            try:
                run = subprocess.run([sys.executable, "-I", "-c", CHOOSE_CHECK, tmp], input=payload,
                                     capture_output=True, text=True, timeout=10, cwd=tmp)
            except subprocess.TimeoutExpired:
                checks["choose"] = "timeout"
                return checks, "choose() did not answer within 10 s"
        if run.returncode:
            checks["choose"] = "error"
            return checks, (run.stderr.strip().splitlines() or ["error"])[-1]
        out = json.loads(run.stdout.strip().splitlines()[-1])
        checks["choose"] = f"returned {out['pick']}" + ("" if out["legal"] else " (not legal)")
        return checks, None if out["legal"] else "choose() returned a square that is not legal"


def handler(game):
    class H(BaseHTTPRequestHandler):
        def log_message(self, *args):                   # quiet: the bot's output is what matters
            pass

        def reply(self, code, body, kind="application/json"):
            data = (json.dumps(body) if kind == "application/json" else body).encode()
            self.send_response(code)
            self.send_header("Content-Type", kind)
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def keyed(self):
            if self.headers.get("X-Player-Key"):
                return True
            self.reply(401, {"detail": "missing X-Player-Key"})
            return False

        def body(self):
            n = int(self.headers.get("Content-Length") or 0)
            try:
                return json.loads(self.rfile.read(n) or b"{}")
            except ValueError:
                return {}

        def do_GET(self):
            with game.lock:
                if self.path == "/cw/phase":
                    return self.reply(200, game.phase_info())
                if self.path == "/cw/state":
                    return self.keyed() and self.reply(200, game.state())
                if self.path.startswith("/practice/"):      # the dry run's "live link": the board as text
                    marks = {"red": "R", "blue": "B", "empty": ".", "wall": "#", "bomb": "*"}
                    rows = ["".join(marks[game.owner[name((x, y))]] for x in range(COLS)) for y in range(1, ROWS + 1)]
                    return self.reply(200, "\n".join(rows) + "\n", "text/plain; charset=utf-8")
            self.reply(404, {"detail": "not found"})

        def do_POST(self):
            if self.path == "/cw/join":                    # any Claude account or Miro token joins as you0
                got = self.body()
                if not (got.get("miro_token") or got.get("account")):
                    return self.reply(400, {"detail": "log in to Claude Code first"})
                return self.reply(200, {"key": "cwk_" + "f" * 43, "alias": "you0", "name": "You"})
            if not self.keyed():
                return
            body = self.body()
            with game.lock:
                if self.path == "/cw/move":
                    return self.reply(200, game.move("red", str(body.get("square", ""))))
                if self.path in ("/cw/submission", "/cw/dryrun"):
                    p, _ = game.tick()
                    files = body.get("files") or {}
                    if self.path == "/cw/submission" and p not in UPLOAD_PHASES:
                        return self.reply(409, {"detail": f"uploads are closed during {p}"})
            if self.path == "/cw/submission":
                checks, error = game.check_upload(files)
                with game.lock:
                    game.version += 1 if not error else 0
                    return self.reply(200, {"version": game.version, "status": "install_failed" if error else "ok",
                                            "error": error, "checks": checks})
            if self.path == "/cw/dryrun":
                checks, error = game.check_upload(files)
                pid = uuid.uuid4().hex[:8]
                host = self.headers.get("Host") or f"127.0.0.1:{game.a.port}"
                return self.reply(200, {"practice_id": pid, "live_url": f"http://{host}/practice/{pid}",
                                        "checks": checks, "error": error})
            self.reply(404, {"detail": "not found"})
    return H


def main():
    ap = argparse.ArgumentParser(description="A local Color Wars server for testing bot.py")
    ap.add_argument("--port", type=int, default=8765, help="0 picks a free port")
    ap.add_argument("--start", choices=PHASES, default="lobby", help="the phase to begin in")
    ap.add_argument("--hold", action="store_true", help="stay in the --start phase")
    ap.add_argument("--opponent", choices=list(OPPONENTS) + ["none"], default="sample")
    ap.add_argument("--skew", type=float, default=0.0, help="seconds the fake server clock is ahead")
    for p, secs in zip(PHASES, (5, 5, 30, 5, 120)):
        ap.add_argument(f"--{p}", type=float, default=secs, help=f"seconds of {p.upper()} (default {secs})")
    a = ap.parse_args()

    game = Game(a)
    httpd = ThreadingHTTPServer(("127.0.0.1", a.port), handler(game))
    a.port = httpd.server_address[1]
    if a.opponent != "none":
        threading.Thread(target=game.opponent, daemon=True).start()
    print(f"fake server on http://127.0.0.1:{a.port}  (any key works: python3 bot.py --login cwk_test)", flush=True)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()

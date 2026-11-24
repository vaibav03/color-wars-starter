#!/usr/bin/env python3
"""Offline Color Wars: run your strategy against a sample opponent. No network, no token.

  python3 simulate.py                     you are Red, 600 turns (10 minutes at one capture per second)
  python3 simulate.py --side blue         play from the Blue crystal instead
  python3 simulate.py --opponent random   an opponent that takes random legal squares
  python3 simulate.py --opponent house    the practice arena's house bot: grabs bombs and defends
  python3 simulate.py --turns 100 --map   a short match, with the final board printed
  python3 simulate.py --watch             watch the match: the board is drawn again every 10 turns
  python3 simulate.py --web               watch the match in your browser at http://localhost:8000

The simulator applies the match rules: adjacency, walls, bombs, supply lines, and the three
ways to win. It does not model network delay or referee reverts.

The last line is "RESULT win|loss|draw <your squares>-<opponent's squares> <reason>". The exit
code is 0 for any finished match, and 1 when choose raised an error or returned an illegal square.
"""
import argparse, json, random, sys, time, webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from colorwars import (ALL_SQUARES, COLS, ROWS, name, capture, distance_map, legal_squares,
                       neighbors, safe_choose, threat, view)

CRYSTALS = {"red": ["E29", "D30", "E30", "F30", "E31"], "blue": ["AF4", "AE5", "AF5", "AG5", "AF6"]}
WALLS = ("R7", "S7", "F8", "Q8", "T8", "G9", "P9", "U9", "O10", "V10", "L13", "Y13", "K14", "Z14", "J15", "AA15",
         "I16", "AB16", "H17", "AC17", "H18", "AC18", "I19", "AB19", "J20", "AA20", "K21", "Z21", "L22", "Y22",
         "O25", "V25", "P26", "U26", "AD26", "Q27", "T27", "AE27", "R28", "S28")
BOMBS = ("R4", "S4", "G7", "H8", "U14", "F17", "R17", "S17", "R18", "S18", "AE18", "P21", "AC27", "AD28", "R31", "S31")


def new_board():
    """The match map (same as the game server's): label -> 'red'|'blue'|'empty'|'wall'|'bomb'."""
    owner = {s: "empty" for s in ALL_SQUARES}
    for s in WALLS:
        owner[s] = "wall"
    for s in BOMBS:
        owner[s] = "bomb"
    for who, crystal in CRYSTALS.items():
        for s in crystal:
            owner[s] = who
    return owner


def sample_opponent(board, legal, my_crystal, enemy_crystal, reverted):
    steps = distance_map(board, enemy_crystal)
    return min(legal, key=lambda s: steps.get(s, 999))


def random_opponent(board, legal, my_crystal, enemy_crystal, reverted):
    return random.choice(legal)


def house_opponent(board, legal, my_crystal, enemy_crystal, reverted):
    """The house bot: the square that gains the most (bombs, cuts, defence near home), else nearest the target."""
    crystals = {"me": my_crystal, "enemy": enemy_crystal}
    steps, home = distance_map(board, enemy_crystal), distance_map(board, my_crystal)
    mine, theirs = count(board, "me"), count(board, "enemy")
    def score(s):
        after = dict(board)
        capture(after, "me", s, crystals)
        cut = theirs - count(after, "enemy") - (board[s] == "enemy")    # enemy squares cut off
        defend = board[s] == "enemy" and home.get(s, 99) <= 6
        gain = count(after, "me") - mine + 2 * cut + 2 * defend
        return (-gain, board[s] == "enemy", steps.get(s, 999))
    return min(legal, key=score)


OPPONENTS = {"sample": sample_opponent, "random": random_opponent, "house": house_opponent}


def require_python():
    if sys.version_info[:2] != (3, 12):
        v = ".".join(map(str, sys.version_info[:3]))
        sys.exit(f"Python 3.12 is mandatory. This is Python {v}. Another version does not work, newer or older: "
                 f"install Python 3.12 next to it (python.org, or `brew install python@3.12`), then run the kit "
                 f"with python3.12, e.g. python3.12 {sys.argv[0]}")


def count(owner, who):
    return sum(o == who for o in owner.values())


def draw(owner, me):
    marks = {me: "M", "empty": ".", "wall": "#", "bomb": "*"}
    for y in range(1, ROWS + 1):
        print("".join(marks.get(owner[name((x, y))], "x") for x in range(COLS)))


def frame(owner, me, foe, turn, every, delay):
    """One --watch frame: clear the terminal, then the turn, the counts and the board."""
    print("\033[2J\033[H", end="")
    print(f"turn {turn:4d}  you (M) {count(owner, me):4d}  opponent (x) {count(owner, foe):4d}"
          f"   . empty  # wall  * bomb   (every {every} turns, Ctrl-C stops)")
    draw(owner, me)
    sys.stdout.flush()
    time.sleep(delay)


COLORS = {"red": "#f16c7f", "blue": "#7b92ff", "empty": "#f5f6f8", "wall": "#1a1a1a", "bomb": "#f5d128"}

PAGE = """<!doctype html><html><head><meta charset="utf-8"><title>Color Wars simulation</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
:root{--bg:#fafafa;--fg:#1a1a1a;--mute:#666;--line:#ddd}
@media (prefers-color-scheme:dark){:root{--bg:#16171a;--fg:#eee;--mute:#999;--line:#333}}
body{background:var(--bg);color:var(--fg);font:14px system-ui,sans-serif;margin:0;padding:16px}
.wrap{max-width:720px;margin:auto;display:flex;flex-direction:column;gap:10px}
h1{font-size:18px;margin:0}.mute{color:var(--mute)}
.score{display:flex;gap:16px;font-size:16px;font-weight:600;flex-wrap:wrap}
.chip{display:inline-block;width:12px;height:12px;border-radius:2px;vertical-align:-1px;margin-right:4px}
canvas{width:100%;height:auto;border:1px solid var(--line);image-rendering:pixelated}
.ctl{display:flex;gap:10px;align-items:center;flex-wrap:wrap}
input[type=range]{flex:1;min-width:160px}
button,select{font:inherit;padding:4px 10px}
#result{font-weight:600;min-height:1.2em}
</style></head><body><div class="wrap">
<h1>Color Wars simulation</h1>
<div class="mute" id="sub"></div>
<div class="score"><span id="me"></span><span id="foe"></span><span class="mute" id="turn"></span></div>
<canvas id="c"></canvas>
<div class="ctl"><button id="play">Pause</button>
<select id="speed"><option value="2">slow</option><option value="10" selected>normal</option><option value="40">fast</option><option value="200">very fast</option></select>
<input type="range" id="t" min="0" value="0"></div>
<div id="result"></div><div class="mute" id="hover">Point at a square to see its name.</div>
</div><script>
const M=__MATCH__, S=18, C=document.getElementById('c'), X=C.getContext('2d');
C.width=M.cols*S; C.height=M.rows*S;
const col=c=>c<26?String.fromCharCode(65+c):'A'+String.fromCharCode(39+c);
const label=(c,r)=>col(c)+(r+1), idx={};
for(let r=0;r<M.rows;r++)for(let c=0;c<M.cols;c++)idx[label(c,r)]=[c,r];
const crystal=new Set([...M.crystals.red,...M.crystals.blue]);
let own={}, t=0, playing=true, acc=0, last=performance.now();
const slider=document.getElementById('t'); slider.max=M.frames.length;
document.getElementById('sub').textContent=`You are ${M.me} against the ${M.opponent} bot. Your squares are ${M.me}.`;
function cell(sq){const [c,r]=idx[sq];X.fillStyle=M.colors[own[sq]];X.fillRect(c*S,r*S,S,S);
 X.strokeStyle=crystal.has(sq)?'#1a1a1a':'#b0b0b0';X.lineWidth=crystal.has(sq)?3:1;X.strokeRect(c*S+.5,r*S+.5,S-1,S-1);}
function seek(n){own=Object.assign({},M.initial);for(let i=0;i<n;i++)for(const [s,o] of M.frames[i])own[s]=o;t=n;
 for(const s in own)cell(s);show();}
function step(){if(t>=M.frames.length)return false;for(const [s,o] of M.frames[t]){own[s]=o;cell(s);}t++;return true;}
function count(w){let n=0;for(const s in own)if(own[s]===w)n++;return n;}
function show(){const chip=w=>`<span class="chip" style="background:${M.colors[w]}"></span>`;
 document.getElementById('me').innerHTML=chip(M.me)+'You '+count(M.me);
 document.getElementById('foe').innerHTML=chip(M.foe)+'Opponent '+count(M.foe);
 document.getElementById('turn').textContent=`turn ${t} of ${M.frames.length}`;slider.value=t;
 document.getElementById('result').textContent=t>=M.frames.length?M.result:'';}
function loop(now){const sp=+document.getElementById('speed').value;
 if(playing){acc+=(now-last)/1000*sp;let moved=false;while(acc>=1){acc-=1;if(!step()){playing=false;play.textContent='Replay';break;}moved=true;}if(moved)show();}
 last=now;requestAnimationFrame(loop);}
const play=document.getElementById('play');
play.onclick=()=>{if(t>=M.frames.length)seek(0);playing=!playing;play.textContent=playing?'Pause':'Play';};
slider.oninput=()=>{seek(+slider.value);};
C.onmousemove=e=>{const b=C.getBoundingClientRect(),c=Math.floor((e.clientX-b.left)/b.width*M.cols),r=Math.floor((e.clientY-b.top)/b.height*M.rows);
 const sq=label(c,r);if(own[sq])document.getElementById('hover').textContent=`${sq}: ${own[sq]===M.me?'yours':own[sq]===M.foe?'opponent':own[sq]}`;};
seek(0);requestAnimationFrame(loop);
</script></body></html>"""


def serve(port, match):
    """--web: serve the recorded match at http://localhost:PORT until Ctrl-C."""
    page = PAGE.replace("__MATCH__", json.dumps(match)).encode()

    class Page(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(page)))
            self.end_headers()
            self.wfile.write(page)

        def log_message(self, *_):
            pass

    for p in range(port, port + 10):                    # the next free port if this one is taken
        try:
            httpd = ThreadingHTTPServer(("127.0.0.1", p), Page)
            break
        except OSError:
            continue
    else:
        print(f"note: ports {port} to {port + 9} are taken; try --web 9000")
        return
    url = f"http://localhost:{p}"
    print(f"watch the match at {url}  (Ctrl-C stops)", flush=True)
    webbrowser.open(url)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()


def main():
    ap = argparse.ArgumentParser(description="Offline Color Wars simulator")
    ap.add_argument("--side", choices=["red", "blue"], default="red")
    ap.add_argument("--opponent", choices=list(OPPONENTS), default="sample")
    ap.add_argument("--turns", type=int, default=600)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--map", action="store_true", help="print the final board (M you, x opponent)")
    ap.add_argument("--watch", type=int, nargs="?", const=10, default=0, metavar="N",
                    help="draw the board again every N turns (default 10) while the match plays")
    ap.add_argument("--delay", type=float, default=0.15, help="seconds to show each --watch frame")
    ap.add_argument("--web", type=int, nargs="?", const=8000, default=0, metavar="PORT",
                    help="after the match, replay it in your browser at http://localhost:PORT (default 8000)")
    a = ap.parse_args()
    require_python()
    random.seed(a.seed)

    try:
        from strategy import choose
    except Exception as e:
        sys.exit(f"strategy.py does not load: {e}")

    me, foe = a.side, {"red": "blue", "blue": "red"}[a.side]
    brains = {me: choose, foe: OPPONENTS[a.opponent]}
    quiet = lambda *_: None
    faults = {"KIT-ERROR": 0, "KIT-WARN": 0}            # choose raised / returned an illegal square

    def report(line):                                   # print the first three of each kind only
        kind = line.split()[0]
        faults[kind] += 1
        if faults[kind] <= 3:
            print(line)

    owner, skipped, winner, reason = new_board(), 0, None, ""
    last_change, last_counts = 0, None              # the turn the territory counts last moved
    start, before, frames = dict(owner), dict(owner), []   # --web: the squares that changed on each turn

    for turn in range(1, a.turns + 1):
        order = (me, foe) if turn % 2 else (foe, me)    # alternate who moves first
        for who in order:
            other = foe if who == me else me
            board = view(owner, who)
            legal = legal_squares(board, CRYSTALS[who])
            pick = safe_choose(brains[who], board, legal, CRYSTALS[who], CRYSTALS[other], [],
                               log=report if who == me else quiet)
            if pick is None:
                skipped += who == me
                continue
            capture(owner, who, pick, CRYSTALS)
            if all(owner[s] == who for s in CRYSTALS[other]):
                winner, reason = who, f"captured the crystal on turn {turn}"
                break
        if a.web:
            frames.append([[sq, o] for sq, o in owner.items() if before[sq] != o])
            before = dict(owner)
        if winner:
            break
        counts = (count(owner, me), count(owner, foe))
        if counts != last_counts:
            last_change, last_counts = turn, counts
        if a.watch and turn % a.watch == 0:
            frame(owner, me, foe, turn, a.watch, a.delay)
        elif turn % 100 == 0:
            print(f"turn {turn:4d}  you {count(owner, me):4d}  opponent {count(owner, foe):4d}")

    mine, theirs = count(owner, me), count(owner, foe)
    captured = winner is not None                   # the stall note below is only for matches that ran out of turns
    if not winner:
        if mine != theirs:
            winner, reason = (me if mine > theirs else foe), "more territory at the end"
        else:
            t_me, t_foe = threat(owner, me, CRYSTALS), threat(owner, foe, CRYSTALS)
            if t_me != t_foe:
                winner, reason = (me if t_me < t_foe else foe), "lower crystal threat score"
            else:
                reason = "tied on territory and on threat score"
    if a.watch:
        frame(owner, me, foe, turn, a.watch, 0)
    elif a.map:
        draw(owner, me)
    if not captured and turn - last_change >= 50:
        print(f"note: the territory counts did not change after turn {last_change}: neither side gained ground. "
              f"Run with --map to see where the front line is stuck.")
    if skipped:
        print(f"note: your strategy had no legal square on {skipped} turns")
    print(f"final: you {mine}, opponent {theirs}; "
          f"threat on your crystal {threat(owner, me, CRYSTALS):.2f}, on theirs {threat(owner, foe, CRYSTALS):.2f}")
    if faults["KIT-ERROR"]:
        print(f"choose raised an error on {faults['KIT-ERROR']} turns; the first legal square was taken instead")
    if faults["KIT-WARN"]:
        print(f"choose returned an illegal square on {faults['KIT-WARN']} turns; the first legal square was taken instead")
    result = " ".join(["RESULT", "draw" if not winner else ("win" if winner == me else "loss"), f"{mine}-{theirs}", reason])
    print(result, flush=True)
    if a.web:
        serve(a.web, {"initial": start, "frames": frames, "me": me, "foe": foe, "opponent": a.opponent,
                      "crystals": CRYSTALS, "cols": COLS, "rows": ROWS, "colors": COLORS, "result": result})
    if faults["KIT-ERROR"] or faults["KIT-WARN"]:
        sys.exit(1)                                     # a strategy fault is a failed run, win or lose


if __name__ == "__main__":
    main()

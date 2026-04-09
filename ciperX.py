import time
import sys
import random
import os
import string
import math
import re
from datetime import datetime
import pikepdf
import concurrent.futures
import threading

# ─── ANSI Color Codes ────────────────────────────────────────────────────────
class C:
    RED      = '\033[91m'
    GREEN    = '\033[92m'
    YELLOW   = '\033[93m'
    BLUE     = '\033[94m'
    MAGENTA  = '\033[95m'
    CYAN     = '\033[96m'
    WHITE    = '\033[97m'
    GRAY     = '\033[90m'
    BOLD     = '\033[1m'
    DIM      = '\033[2m'
    RESET    = '\033[0m'
    BG_RED   = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_DARK  = '\033[40m'

def clear(): os.system('cls' if os.name == 'nt' else 'clear')

def beep(count=1):
    for _ in range(count):
        print('\a', end='', flush=True)
        time.sleep(0.1)

def typewrite(text, delay=0.025, color=''):
    for char in text:
        print(color + char + C.RESET, end='', flush=True)
        time.sleep(delay)
    print()

def slow_print(text, color='', delay=0.35):
    print(color + text + C.RESET)
    time.sleep(delay)

BOX = 74

# ─── Global progress tracking for parallel mode ──────────────────────────────
progress = {}
lock = threading.Lock()
stop_event = threading.Event()

# ─── ASCII Banner ─────────────────────────────────────────────────────────────
def print_banner():
    banner = r"""
   ██████╗██╗██████╗ ██╗  ██╗███████╗██████╗ ██╗  ██╗
  ██╔════╝██║██╔══██╗██║  ██║██╔════╝██╔══██╗╚██╗██╔╝
  ██║     ██║██████╔╝███████║█████╗  ██████╔╝ ╚███╔╝
  ██║     ██║██╔═══╝ ██╔══██║██╔══╝  ██╔══██╗ ██╔██╗
  ╚██████╗██║██║     ██║  ██║███████╗██║  ██║██╔╝ ██╗
   ╚═════╝╚═╝╚═╝     ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝
    """
    print(C.CYAN + C.BOLD + banner + C.RESET)
    print(C.YELLOW + C.BOLD + "  ▸  PASSWORD & PDF CRACKER DEMONSTRATION".center(78) + C.RESET)
    print(C.GRAY   +          "  ▸  Simulate brute-force or crack real PDF encryption (parallel auto mode)".center(78) + C.RESET)
    print()

# ─── Box helpers ─────────────────────────────────────────────────────────────
def box_top(title=""):
    if title:
        left  = f"  ┌─ {title} "
        right = "─" * (BOX - len(title) - 2) + "┐"
        print(C.CYAN + left + right + C.RESET)
    else:
        print(C.CYAN + "  ┌" + "─" * BOX + "┐" + C.RESET)

def box_bot():
    print(C.CYAN + "  └" + "─" * BOX + "┘" + C.RESET)

def box_row(label, value_colored, value_plain):
    pad = BOX - 2 - 22 - len(value_plain)
    print(C.CYAN + "  │" + C.RESET +
          f"  {C.GRAY}{label:<20}{C.RESET}  {value_colored}" + " " * max(pad, 0))

def box_blank():
    print(C.CYAN + "  │" + " " * BOX + C.RESET)

def box_flag(icon, col, text):
    print(C.CYAN + "  │" + C.RESET + f"  {col}{icon}  {text}{C.RESET}")

def box_sep():
    print(C.CYAN + "  ├" + "─" * BOX + "┤" + C.RESET)

def box_text(text, col=""):
    inner = f"  {col}{text}{C.RESET}"
    print(C.CYAN + "  │" + C.RESET + inner)

# ─── Progress bar ─────────────────────────────────────────────────────────────
def progress_bar(percent, width=36):
    filled = int(width * percent / 100)
    bar    = '█' * filled + '░' * (width - filled)
    color  = C.GREEN if percent < 50 else C.YELLOW if percent < 80 else C.RED
    return f"{color}[{bar}]{C.RESET}"

def slim_bar(percent, width=20):
    """Compact bar for the parallel panel."""
    filled = int(width * percent / 100)
    bar    = '▓' * filled + '░' * (width - filled)
    if   percent >= 80: color = C.RED
    elif percent >= 40: color = C.YELLOW
    else:               color = C.CYAN
    return f"{color}{bar}{C.RESET}"

# ─── Formatters ──────────────────────────────────────────────────────────────
def fmt_big(n):
    if n >= 1_000_000_000_000: return f"{n/1_000_000_000_000:.2f} trillion"
    if n >= 1_000_000_000:     return f"{n/1_000_000_000:.2f} billion"
    if n >= 1_000_000:         return f"{n/1_000_000:.2f} million"
    return f"{n:,}"

def fmt_time(seconds):
    if seconds < 0.001:       return "< 1ms"
    if seconds < 1:           return f"{seconds*1000:.0f}ms"
    if seconds < 60:          return f"{seconds:.1f}s"
    if seconds < 3600:        return f"{seconds/60:.1f}m"
    if seconds < 86400:       return f"{seconds/3600:.1f}h"
    if seconds < 2_592_000:   return f"{seconds/86400:.1f}d"
    if seconds < 31_536_000:  return f"{seconds/2_592_000:.1f}mo"
    return f"{seconds/31_536_000:.1f}yr"

def fmt_time_long(seconds):
    if seconds < 0.001:       return "< 1 millisecond"
    if seconds < 1:           return f"{seconds*1000:.1f} ms"
    if seconds < 60:          return f"{seconds:.2f} seconds"
    if seconds < 3600:        return f"{seconds/60:.2f} minutes"
    if seconds < 86400:       return f"{seconds/3600:.2f} hours"
    if seconds < 2_592_000:   return f"{seconds/86400:.1f} days"
    if seconds < 31_536_000:  return f"{seconds/2_592_000:.1f} months"
    return f"{seconds/31_536_000:.2f} years"

# ─── Terminal helpers ─────────────────────────────────────────────────────────
def get_term_width():
    try:
        return os.get_terminal_size().columns
    except OSError:
        return 300

def visible_len(s):
    return len(re.sub(r'\033\[[0-9;]*m', '', s))

def clear_line():
    w = get_term_width()
    sys.stdout.write("\r" + " " * w + "\r")
    sys.stdout.flush()

def clear_lines(n):
    if n <= 0:
        return
    for _ in range(n):
        sys.stdout.write("\033[1A\033[2K")
    sys.stdout.flush()

# ─── STEP 1: Detect charset ───────────────────────────────────────────────────
def step_detect(password):
    slow_print("\n  [STEP 1] Analyzing target password...", C.CYAN + C.BOLD, 0.2)
    time.sleep(0.3)

    length      = len(password)
    has_digits  = any(c.isdigit()              for c in password)
    has_lower   = any(c.islower()              for c in password)
    has_upper   = any(c.isupper()              for c in password)
    has_special = any(c in string.punctuation  for c in password)

    if password.isdigit():
        charset, charset_name, charset_size = "numeric",     "Digits only  [0-9]",               10
    elif password.isalpha() and password.islower():
        charset, charset_name, charset_size = "alpha_lower", "Lowercase alpha  [a-z]",            26
    elif password.isalpha() and password.isupper():
        charset, charset_name, charset_size = "alpha_upper", "Uppercase alpha  [A-Z]",            26
    elif password.isalpha():
        charset, charset_name, charset_size = "alpha_mixed", "Mixed alpha  [a-zA-Z]",             52
    elif has_digits and (has_lower or has_upper) and not has_special:
        charset, charset_name, charset_size = "alnum",       "Alphanumeric  [a-zA-Z0-9]",        62
    else:
        charset, charset_name, charset_size = "full",        "Full ASCII printable  [all chars]", 95

    box_top("TARGET ANALYSIS")
    box_blank()
    box_row("Password Length",  f"{C.WHITE+C.BOLD}{length} characters{C.RESET}", f"{length} characters")
    box_row("Charset Detected", f"{C.YELLOW}{charset_name}{C.RESET}",            charset_name)
    box_row("Charset Size",     f"{C.CYAN}{charset_size} symbols{C.RESET}",      f"{charset_size} symbols")
    box_blank()
    box_sep()
    box_blank()
    box_flag("→", C.WHITE, f"Every extra character multiplies the keyspace by {C.CYAN+C.BOLD}{charset_size}x{C.RESET}")
    box_flag("→", C.WHITE, f"Mixing digits + letters + symbols forces attackers to search a far larger space")
    box_blank()
    box_bot()

    return length, charset, charset_size

# ─── STEP 2: Keyspace ─────────────────────────────────────────────────────────
def step_keyspace(length, charset_size):
    slow_print("\n  [STEP 2] Calculating keyspace...", C.CYAN + C.BOLD, 0.2)

    sys.stdout.write(f"  {C.GRAY}  Computing: {charset_size}^{length} ={C.RESET} ")
    sys.stdout.flush()
    time.sleep(0.4)
    for _ in range(5):
        rv = ''.join(random.choice(string.digits) for _ in range(random.randint(8, 14)))
        sys.stdout.write(f"\r  {C.GRAY}  Computing: {charset_size}^{length} ={C.RESET} {C.YELLOW}{rv}...{C.RESET}   ")
        sys.stdout.flush()
        time.sleep(0.12)

    total = charset_size ** length
    sys.stdout.write(f"\r  {C.GRAY}  Computing: {charset_size}^{length} ={C.RESET} {C.GREEN+C.BOLD}{total:,}{C.RESET}          \n")
    sys.stdout.flush()
    time.sleep(0.3)

    box_top("KEYSPACE REPORT")
    box_blank()
    box_row("Formula",      f"{C.GRAY}{charset_size}^{length}{C.RESET}",              f"{charset_size}^{length}")
    box_row("Total Combos", f"{C.WHITE+C.BOLD}{fmt_big(total)}{C.RESET}",             fmt_big(total))
    box_row("Exact Count",  f"{C.CYAN}{total:,}{C.RESET}",                            f"{total:,}")
    box_sep()
    box_row("Worst Case",   f"{C.RED}{fmt_big(total)} attempts{C.RESET}",             f"{fmt_big(total)} attempts")
    box_row("Average Case", f"{C.YELLOW}{fmt_big(total//2)} attempts{C.RESET}",       f"{fmt_big(total//2)} attempts")
    box_blank()
    box_sep()
    box_blank()
    box_flag("→", C.WHITE, f"{C.BOLD}Brute-force always terminates{C.RESET} — it is mathematically guaranteed.")
    box_flag("→", C.WHITE, f"The only variable is {C.CYAN}how long it takes{C.RESET}, which depends on keyspace & hardware.")
    box_blank()
    box_bot()

    return total

# ─── STEP 3: Strength ─────────────────────────────────────────────────────────
COMMON_PINS = {
    "1234","0000","1111","2222","3333","4444","5555","6666","7777","8888","9999",
    "1212","0007","6969","12345","11111","12321","54321","123456","000000",
    "111111","654321","1234567","0000000","12345678","00000000","11111111",
    "87654321","123456789","000000000","1234567890","0000000000",
}

def step_strength(password, charset_size):
    slow_print("\n  [STEP 3] Evaluating password strength...", C.CYAN + C.BOLD, 0.2)
    time.sleep(0.3)

    length     = len(password)
    entropy    = length * math.log2(charset_size) if charset_size > 1 else 0
    all_same   = len(set(password)) == 1
    sequential = False
    if password.isdigit() and length > 1:
        sequential = (all(int(password[i+1]) == int(password[i])+1 for i in range(length-1)) or
                      all(int(password[i+1]) == int(password[i])-1 for i in range(length-1)))
    is_common  = password in COMMON_PINS

    score  = min(length, 6)
    score += 2 if charset_size >= 62 else 1 if charset_size >= 26 else 0
    score += 2 if not is_common and not all_same and not sequential else 0
    score  = max(0, score - (3 if is_common else 0) - (2 if all_same else 0) - (1 if sequential else 0))
    score  = min(score, 10)

    if   score <= 2: rating, col = "VERY WEAK",   C.RED + C.BOLD
    elif score <= 4: rating, col = "WEAK",         C.RED
    elif score <= 6: rating, col = "MODERATE",     C.YELLOW
    elif score <= 8: rating, col = "STRONG",       C.GREEN
    else:            rating, col = "VERY STRONG",  C.GREEN + C.BOLD

    strength_bar = col + '█' * score + C.GRAY + '░' * (10 - score) + C.RESET

    box_top("STRENGTH ANALYSIS")
    box_blank()
    box_row("Entropy",  f"{C.CYAN}{entropy:.1f} bits{C.RESET}",                          f"{entropy:.1f} bits")
    box_row("Score",    f"{col}{score}/10{C.RESET}  [{strength_bar}]",                   f"{score}/10")
    box_row("Rating",   f"{col+C.BOLD}{rating}{C.RESET}",                                rating)
    box_blank()
    box_sep()
    box_blank()

    flags = []
    if is_common:           flags.append((C.RED,    "✗", "Found in common password list — cracked instantly via dictionary"))
    if all_same:            flags.append((C.RED,    "✗", "All characters identical — near-zero entropy"))
    if sequential:          flags.append((C.YELLOW, "✗", "Sequential pattern detected — easily guessed"))
    if length < 6:          flags.append((C.YELLOW, "⚠", "Very short — keyspace exhausted in milliseconds even on slow hardware"))
    if length < 10:         flags.append((C.YELLOW, "⚠", "Length below 10 — modern GPUs crack this in seconds to hours"))
    if not flags:           flags.append((C.GREEN,  "✓", "No trivial patterns detected"))
    if charset_size >= 62:  flags.append((C.GREEN,  "✓", "Mixed charset — significantly increases keyspace"))
    if length >= 12:        flags.append((C.GREEN,  "✓", "Good length — adds strong exponential resistance"))

    for c2, icon, msg in flags:
        box_flag(icon, c2, msg)
    box_blank()
    box_bot()

    return score, rating, entropy

# ─── STEP 4: Time estimates across hardware tiers ────────────────────────────
HARDWARE = [
    ("Slow online (throttled)", 100,             "1 attempt / 10 sec — rate-limited login portal"),
    ("Fast online (no limit)",  10_000,          "10K/s — unprotected API / no lockout policy"),
    ("Laptop CPU",              500_000,         "500K/s — single-core offline MD5"),
    ("Gaming PC GPU",           10_000_000,      "10M/s — mid-range consumer GPU"),
    ("High-end GPU rig",        100_000_000,     "100M/s — RTX 4090 class"),
    ("Cloud GPU cluster",       10_000_000_000,  "10B/s  — 100× A100s in parallel"),
    ("This simulation",         1_000_000,       "1M/s   — demo speed"),
]

def step_time_estimate(total_combinations):
    slow_print("\n  [STEP 4] Estimating crack time across hardware tiers...", C.CYAN + C.BOLD, 0.2)
    time.sleep(0.4)

    avg = total_combinations // 2

    box_top("TIME TO CRACK  (average case — 50% of keyspace)")
    box_blank()
    box_text(f"{'Hardware / Scenario':<28}  {'Est. Time':<22}  Notes", C.GRAY)
    box_sep()

    time_data = []
    for label, speed, desc in HARDWARE:
        secs  = avg / speed
        t_str = fmt_time_long(secs)
        if   secs < 60:          col = C.RED + C.BOLD
        elif secs < 3600:        col = C.RED
        elif secs < 86400:       col = C.YELLOW
        elif secs < 2_592_000:   col = C.GREEN
        else:                    col = C.CYAN
        box_row(label, f"{col}{t_str:<22}{C.RESET}{C.GRAY}({desc}){C.RESET}", f"{t_str}   ({desc})")
        time_data.append((label, speed, desc, secs, t_str))

    box_blank()
    box_sep()
    box_blank()
    box_flag("→", C.WHITE, f"A {C.RED}rate-limited login{C.RESET} buys time — but NOT infinite safety.")
    box_flag("→", C.WHITE, f"An {C.RED}offline hash leak{C.RESET} removes ALL rate limiting — GPU attacks apply.")
    box_flag("→", C.WHITE, f"Only a {C.GREEN}long, complex password{C.RESET} makes crack time exceed an attacker's patience.")
    box_blank()
    box_bot()

    return avg / 1_000_000, time_data

# ─── STEP 5: Simulation crack (mode 1) ───────────────────────────────────────
def step_crack(password, charset, total):
    slow_print("\n  [STEP 5] Running crack simulation...", C.CYAN + C.BOLD, 0.2)
    time.sleep(0.3)

    charset_map = {
        "numeric":     string.digits,
        "alpha_lower": string.ascii_lowercase,
        "alpha_upper": string.ascii_uppercase,
        "alpha_mixed": string.ascii_letters,
        "alnum":       string.ascii_letters + string.digits,
        "full":        string.printable.strip(),
    }
    chars  = charset_map.get(charset, string.digits)
    length = len(password)

    start    = time.time()
    attempts = 0
    found_at = None

    from itertools import product as iproduct
    for combo in iproduct(chars, repeat=length):
        candidate = ''.join(combo)
        attempts += 1
        elapsed   = time.time() - start
        if attempts % 500 == 0 or candidate == password:
            cracking_line(candidate, attempts, total, elapsed)
        if candidate == password:
            found_at = attempts
            break

    elapsed = time.time() - start
    return found_at, elapsed

# ─── Terminal crack animation ─────────────────────────────────────────────────
def fake_hash():
    return ''.join(random.choice("0123456789abcdef") for _ in range(32))

def cracking_line(candidate, done, total, elapsed, pdf_name="target.pdf"):
    pct   = (done / total) * 100 if total > 0 else 0
    bar   = progress_bar(pct)
    speed = done / elapsed if elapsed > 0 else 0
    timer = fmt_time(elapsed)
    h     = fake_hash()
    pct_s = f"{pct:5.2f}%"
    line  = (
        f"  {C.GRAY}PDF:{C.RESET} {C.GRAY}{pdf_name}{C.RESET} "
        f"{C.GRAY}TRY:{C.RESET} {C.YELLOW+C.BOLD}{candidate}{C.RESET} "
        f"{C.GRAY}H/s:{C.RESET}{C.CYAN}{speed:>9,.0f}{C.RESET} "
        f"{C.GRAY}TIME:{C.RESET}{C.MAGENTA}{timer:>12}{C.RESET} "
        f"[{bar}{C.RESET} {pct_s}]"
    )
    w       = get_term_width()
    padding = max(0, w - visible_len(line))
    sys.stdout.write("\r" + line + " " * padding)
    sys.stdout.flush()

def success_screen(password, attempts, elapsed, total, entropy, rating):
    print("\n")
    beep(3)
    speed     = attempts / max(elapsed, 0.001)
    pct_tried = (attempts / total) * 100

    print(C.GREEN+C.BOLD + "  ╔" + "═"*BOX + "╗")
    print("  ║" + "  ✓  PASSWORD CRACKED  ✓".center(BOX) + "║")
    print("  ╠" + "═"*BOX + "╣" + C.RESET)

    rows = [
        ("PASSWORD",         f"{C.RED+C.BOLD}{password}{C.RESET}",           password),
        ("ATTEMPTS MADE",    f"{C.CYAN}{attempts:,}{C.RESET}",               f"{attempts:,}"),
        ("KEYSPACE %",       f"{C.YELLOW}{pct_tried:.4f}%{C.RESET}",         f"{pct_tried:.4f}%"),
        ("TIME ELAPSED",     f"{C.WHITE}{fmt_time_long(elapsed)}{C.RESET}",  fmt_time_long(elapsed)),
        ("SPEED",            f"{C.WHITE}{speed:,.0f} H/s{C.RESET}",          f"{speed:,.0f} H/s"),
        ("ENTROPY",          f"{C.CYAN}{entropy:.1f} bits{C.RESET}",         f"{entropy:.1f} bits"),
        ("RATING",           f"{C.YELLOW}{rating}{C.RESET}",                 rating),
        ("STATUS",           f"{C.GREEN+C.BOLD}CRACKED{C.RESET}",            "CRACKED"),
    ]
    for label, val_col, val_plain in rows:
        pad = BOX - 2 - 22 - len(val_plain)
        print(C.GREEN+C.BOLD + "  ║" + C.RESET +
              f"  {C.GRAY}{label:<20}{C.RESET}  {val_col}" + " " * max(pad, 0))

    print(C.GREEN+C.BOLD + "  ╚" + "═"*BOX + "╝" + C.RESET)
    print()

def success_screen_pdf(password, attempts, elapsed, keyspace):
    print("\n")
    beep(3)

    for _ in range(6):
        h1, h2 = fake_hash(), fake_hash()
        print(f"  {C.GRAY}{h1}  →  {h2}{C.RESET}")
        time.sleep(0.04)
    for _ in range(6):
        sys.stdout.write("\033[1A\033[2K")

    speed     = attempts / max(elapsed, 0.001)
    pct_tried = (attempts / keyspace) * 100

    print(C.GREEN+C.BOLD + "  ╔" + "═"*BOX + "╗")
    print("  ║" + "  ✓  PDF PASSWORD CRACKED  ✓".center(BOX) + "║")
    print("  ╠" + "═"*BOX + "╣" + C.RESET)

    rows = [
        ("PASSWORD",         f"{C.RED+C.BOLD}{password}{C.RESET}",           password),
        ("ATTEMPTS MADE",    f"{C.CYAN}{attempts:,}{C.RESET}",               f"{attempts:,}"),
        ("KEYSPACE %",       f"{C.YELLOW}{pct_tried:.4f}%{C.RESET}",         f"{pct_tried:.4f}%"),
        ("TIME ELAPSED",     f"{C.WHITE}{fmt_time_long(elapsed)}{C.RESET}",  fmt_time_long(elapsed)),
        ("SPEED",            f"{C.WHITE}{speed:,.0f} H/s{C.RESET}",          f"{speed:,.0f} H/s"),
        ("STATUS",           f"{C.GREEN+C.BOLD}CRACKED{C.RESET}",            "CRACKED"),
    ]
    for label, val_col, val_plain in rows:
        pad = BOX - 2 - 22 - len(val_plain)
        print(C.GREEN+C.BOLD + "  ║" + C.RESET +
              f"  {C.GRAY}{label:<20}{C.RESET}  {val_col}" + " " * max(pad, 0))

    print(C.GREEN+C.BOLD + "  ╚" + "═"*BOX + "╝" + C.RESET)
    print()

# ─── Save report ─────────────────────────────────────────────────────────────
def save_report(password, length, charset_name, charset_size, total,
                score, rating, entropy, time_data,
                attempts, elapsed, sim_speed):

    report_name = f"crack_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    speed_actual = attempts / max(elapsed, 0.001)
    pct_tried    = (attempts / total) * 100
    divider  = "=" * 72
    thin_div = "-" * 72

    lines = []
    lines.append(divider)
    lines.append("  CipherX — BRUTE-FORCE VULNERABILITY DEMONSTRATION REPORT")
    lines.append(f"  Generated : {datetime.now().strftime('%Y-%m-%d  %H:%M:%S')}")
    lines.append(divider)
    lines.append("")
    lines.append("  SECTION 1 — VULNERABILITY EXPLAINED")
    lines.append(thin_div)
    lines.append("")
    lines.append("  What is brute-force?")
    lines.append("  A brute-force attack tries every possible combination in a password's")
    lines.append("  keyspace until the correct one is found. It requires no knowledge of")
    lines.append("  the password — only compute time.")
    lines.append("")
    lines.append("  Why does it always succeed?")
    lines.append("  The keyspace (total possible passwords) is always finite. Given enough")
    lines.append("  computing power and time, exhausting it is mathematically guaranteed.")
    lines.append("  The ONLY defence is making that time cost exceed an attacker's patience.")
    lines.append("")
    lines.append("  Real-world conditions that make this worse:")
    lines.append("  • No account lockout  → unlimited attempts with no penalty")
    lines.append("  • No rate limiting    → thousands of guesses per second allowed")
    lines.append("  • Weak hashing        → offline GPU cracking at billions/sec")
    lines.append("  • Short/simple pass   → tiny keyspace, cracked in milliseconds")
    lines.append("")
    lines.append("  SECTION 2 — TARGET PASSWORD ANALYSIS")
    lines.append(thin_div)
    lines.append(f"  {'Password (redacted)':<26}: {'*' * length}  ({length} characters)")
    lines.append(f"  {'Charset':<26}: {charset_name}")
    lines.append(f"  {'Charset size':<26}: {charset_size} symbols")
    lines.append(f"  {'Total keyspace':<26}: {total:,}  ({fmt_big(total)})")
    lines.append(f"  {'Entropy':<26}: {entropy:.1f} bits")
    lines.append(f"  {'Strength score':<26}: {score}/10  ({rating})")
    lines.append("")
    lines.append("  SECTION 3 — ESTIMATED CRACK TIME BY HARDWARE")
    lines.append(thin_div)
    lines.append(f"  {'Hardware / Scenario':<30}  {'Avg Time':<20}  Speed")
    lines.append(f"  {'-'*30}  {'-'*20}  {'-'*16}")
    for label, speed, desc, secs, t_str in time_data:
        lines.append(f"  {label:<30}  {t_str:<20}  {speed:>16,} H/s")
    lines.append("")
    lines.append("  SECTION 4 — LIVE SIMULATION RESULTS")
    lines.append(thin_div)
    lines.append(f"  {'Attempts made':<26}: {attempts:,}")
    lines.append(f"  {'Keyspace covered':<26}: {pct_tried:.4f}%")
    lines.append(f"  {'Time elapsed':<26}: {fmt_time_long(elapsed)}")
    lines.append(f"  {'Simulation speed':<26}: {speed_actual:,.0f} H/s")
    lines.append(f"  {'Result':<26}: CRACKED")
    lines.append("")
    lines.append("  SECTION 5 — RECOMMENDED MITIGATIONS")
    lines.append(thin_div)
    lines.append("")
    lines.append("  For SYSTEMS (developers):")
    lines.append("  • Enforce account lockout after 5–10 failed attempts")
    lines.append("  • Add rate limiting / CAPTCHA on login endpoints")
    lines.append("  • Use strong hashing: bcrypt / Argon2 (not MD5 / SHA-1)")
    lines.append("  • Log and alert on repeated failed logins")
    lines.append("  • Require MFA for sensitive accounts")
    lines.append("")
    lines.append("  For USERS (password hygiene):")
    lines.append("  • Use passwords of 16+ characters minimum")
    lines.append("  • Mix uppercase, lowercase, digits, and symbols")
    lines.append("  • Never reuse passwords across sites")
    lines.append("  • Use a password manager — humans are bad at randomness")
    lines.append("  • Enable MFA wherever available")
    lines.append("")
    lines.append(divider)
    lines.append("  END OF REPORT — CipherX")
    lines.append(divider)

    with open(report_name, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    return report_name

# ─── Save report PDF ──────────────────────────────────────────────────────────
def save_report_pdf(pdf_path, length, charset_name, charset_size, total,
                time_data, attempts, elapsed):

    report_name = f"crack_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    speed_actual = attempts / max(elapsed, 0.001)
    pct_tried    = (attempts / total) * 100
    divider  = "=" * 72
    thin_div = "-" * 72

    lines = []
    lines.append(divider)
    lines.append("  CipherX — PDF PASSWORD CRACKING DEMONSTRATION REPORT")
    lines.append(f"  Generated : {datetime.now().strftime('%Y-%m-%d  %H:%M:%S')}")
    lines.append(divider)
    lines.append("")
    lines.append("  SECTION 1 — PDF ENCRYPTION VULNERABILITY")
    lines.append(thin_div)
    lines.append("")
    lines.append("  PDF encryption uses passwords to protect documents, but weak passwords")
    lines.append("  can be cracked using brute-force attacks. Unlike hashed passwords,")
    lines.append("  PDF passwords are checked directly, making them vulnerable to")
    lines.append("  dictionary and brute-force methods.")
    lines.append("")
    lines.append("  Why PDFs are vulnerable:")
    lines.append("  • Password verification is fast — no slow hashing like bcrypt")
    lines.append("  • No built-in rate limiting or lockouts")
    lines.append("  • Short or simple passwords can be cracked quickly")
    lines.append("  • Encryption strength depends on password strength")
    lines.append("")
    lines.append("  SECTION 2 — TARGET PDF ANALYSIS")
    lines.append(thin_div)
    lines.append(f"  {'PDF File':<26}: {os.path.basename(pdf_path)}")
    lines.append(f"  {'Cracked Password Length':<26}: {length} characters")
    lines.append(f"  {'Charset':<26}: {charset_name}")
    lines.append(f"  {'Charset size':<26}: {charset_size} symbols")
    lines.append(f"  {'Total keyspace searched':<26}: {total:,}  ({fmt_big(total)})")
    lines.append("")
    lines.append("  SECTION 3 — ESTIMATED CRACK TIME BY HARDWARE")
    lines.append(thin_div)
    lines.append(f"  {'Hardware / Scenario':<30}  {'Avg Time':<20}  Speed")
    lines.append(f"  {'-'*30}  {'-'*20}  {'-'*16}")
    for label, speed, desc, secs, t_str in time_data:
        lines.append(f"  {label:<30}  {t_str:<20}  {speed:>16,} H/s")
    lines.append("")
    lines.append("  SECTION 4 — CRACKING RESULTS")
    lines.append(thin_div)
    lines.append(f"  {'Attempts made':<26}: {attempts:,}")
    lines.append(f"  {'Keyspace covered':<26}: {pct_tried:.4f}%")
    lines.append(f"  {'Time elapsed':<26}: {fmt_time_long(elapsed)}")
    lines.append(f"  {'Actual speed':<26}: {speed_actual:,.0f} H/s")
    lines.append(f"  {'Result':<26}: CRACKED")
    lines.append("")
    lines.append("  SECTION 5 — RECOMMENDED MITIGATIONS")
    lines.append(thin_div)
    lines.append("")
    lines.append("  For PDF creators:")
    lines.append("  • Use strong, long passwords (16+ characters, mixed charset)")
    lines.append("  • Consider certificate-based encryption instead of passwords")
    lines.append("  • Use PDF tools that support strong encryption standards")
    lines.append("")
    lines.append("  For users:")
    lines.append("  • Never use simple passwords for important PDFs")
    lines.append("  • Use password managers for generating strong passwords")
    lines.append("  • Be aware that 'encrypted' doesn't mean 'uncrackable'")
    lines.append("")
    lines.append(divider)
    lines.append("  END OF REPORT — CipherX")
    lines.append(divider)

    with open(report_name, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    return report_name

# ─── Worker: try all passwords of a given length ─────────────────────────────
def try_length(pdf_path, length):
    with lock:
        progress[length] = {
            'attempts': 0,
            'candidate': '0' * length,
            'start_time': time.time(),
        }
    keyspace = 10 ** length
    for j in range(keyspace):
        if stop_event.is_set():
            return None
        candidate = str(j).zfill(length)
        with lock:
            progress[length]['attempts'] = j + 1
            progress[length]['candidate'] = candidate
        try:
            pdf = pikepdf.open(pdf_path, password=candidate)
            pdf.close()
            stop_event.set()
            return candidate
        except pikepdf.PasswordError:
            pass
        except Exception:
            return None
    return None

# ─── Known-length single-thread cracker ──────────────────────────────────────
def crack_known_length(pdf_path, length):
    """Sequential cracker for a known password length — styled display."""
    keyspace = 10 ** length
    BAR_W    = 30

    # ── Header ──────────────────────────────────────────────────────────────
    print()
    print(C.CYAN + "  ╔" + "═"*BOX + "╗" + C.RESET)
    title = f"  CRACKING  ·  LENGTH {length}  ·  KEYSPACE {keyspace:,}"
    print(C.CYAN + "  ║" + C.BOLD + C.WHITE + title.center(BOX) + C.RESET + C.CYAN + "  ║" + C.RESET)
    print(C.CYAN + "  ╠" + "═"*BOX + "╣" + C.RESET)
    fname = os.path.basename(pdf_path)
    if len(fname) > 40: fname = '…' + fname[-39:]
    print(C.CYAN + "  ║" + C.RESET +
          f"  {C.GRAY}FILE :{C.RESET} {C.WHITE}{fname:<{BOX-9}}{C.RESET}" + C.CYAN + "  ║" + C.RESET)
    print(C.CYAN + "  ╠" + "═"*BOX + "╣" + C.RESET)
    # column headers
    hdr = (f"  {C.GRAY}{'ATTEMPT':>10}  {'CANDIDATE':<{length+2}}  "
           f"{'PROGRESS':<{BAR_W+9}}  {'SPEED':>10}  {'ELAPSED':>8}{C.RESET}")
    print(C.CYAN + "  ║" + C.RESET + hdr)
    print(C.CYAN + "  ╠" + "─"*BOX + "╣" + C.RESET)

    HEADER_LINES = 7          # lines printed above the live row
    start        = time.time()
    found_pw     = None

    for j in range(keyspace):
        candidate = str(j).zfill(length)
        attempts  = j + 1
        elapsed   = time.time() - start
        speed     = attempts / max(elapsed, 0.001)
        pct       = attempts / keyspace * 100
        bar       = slim_bar(pct, width=BAR_W)
        pct_s     = f"{pct:5.1f}%"
        timer     = fmt_time(elapsed)

        # colour the candidate: digits that match the "target length" get cyan
        row = (
            f"  {C.CYAN}{attempts:>10,}{C.RESET}  "
            f"{C.YELLOW+C.BOLD}{candidate:<{length+2}}{C.RESET}  "
            f"{bar}  {C.WHITE}{pct_s}{C.RESET}  "
            f"{C.CYAN}{speed:>9,.0f}{C.RESET}  "
            f"{C.MAGENTA}{timer:>8}{C.RESET}"
        )

        w       = get_term_width()
        padding = max(0, w - visible_len(row) - 4)
        sys.stdout.write("\r" + C.CYAN + "  ║" + C.RESET + row + " " * padding)
        sys.stdout.flush()

        try:
            pdf = pikepdf.open(pdf_path, password=candidate)
            pdf.close()
            found_pw = candidate
            break
        except pikepdf.PasswordError:
            pass
        except Exception as e:
            print(f"\n  {C.RED}[ERROR] {e}{C.RESET}")
            break

    elapsed = time.time() - start

    # Close the box
    sys.stdout.write("\r")
    sys.stdout.flush()
    print(C.CYAN + "  ╚" + "═"*BOX + "╝" + C.RESET)

    return found_pw, attempts if found_pw else keyspace, elapsed


# ─── Parallel panel renderer ──────────────────────────────────────────────────
#
# Layout (one line per length):
#
#  │ ● LEN 4  ▓▓▓▓▓▓░░░░░░░░░░░░░░  42.7%  try: 4271      12,345 H/s   3.2s │
#
PANEL_BAR_W = 22

def _render_panel_line(ln, lengths_to_try, future_to_len, pending, start_time):
    """Return a single rendered line for length `ln` (no newline)."""
    p         = progress.get(ln, {})
    attempts  = p.get('attempts', 0)
    candidate = p.get('candidate', '0' * ln)
    t0        = p.get('start_time', start_time)
    elapsed   = time.time() - t0
    ks        = 10 ** ln
    pct       = (attempts / ks * 100) if ks > 0 else 0
    speed     = attempts / max(elapsed, 0.001)
    timer     = fmt_time(elapsed)
    bar       = slim_bar(pct, width=PANEL_BAR_W)
    pct_s     = f"{pct:5.1f}%"

    # Is this length still running?
    is_active = any(future_to_len[f] == ln for f in pending)
    bullet    = f"{C.GREEN}●{C.RESET}" if is_active else f"{C.GRAY}◌{C.RESET}"

    line = (
        f"  {C.CYAN}│{C.RESET} {bullet} "
        f"{C.BOLD}LEN {ln:<2}{C.RESET}  "
        f"{bar}  "
        f"{C.WHITE}{pct_s}{C.RESET}  "
        f"{C.GRAY}try:{C.RESET}{C.YELLOW+C.BOLD}{candidate:<12}{C.RESET}  "
        f"{C.CYAN}{speed:>10,.0f} H/s{C.RESET}  "
        f"{C.MAGENTA}{timer:>6}{C.RESET}  "
        f"{C.CYAN}│{C.RESET}"
    )
    return line


def render_parallel_panel(lengths_to_try, future_to_len, pending,
                           start_time, printed_lines):
    """Erase old panel, draw fresh one. Returns new printed_lines count."""
    if printed_lines:
        clear_lines(printed_lines)

    # Collect lines snapshot under lock
    with lock:
        panel_lines = [
            _render_panel_line(ln, lengths_to_try, future_to_len,
                               pending, start_time)
            for ln in sorted(lengths_to_try)
        ]

    # top border
    top_label = "  PARALLEL CRACKER — LENGTHS 1–10"
    top_border = (C.CYAN + "  ╔═" + C.BOLD + C.WHITE +
                  top_label + C.RESET + C.CYAN +
                  "═" * (BOX - len(top_label)) + "╗" + C.RESET)

    # column header row
    col_hdr = (
        f"  {C.CYAN}║{C.RESET}   "
        f"{C.GRAY}{'':4}  {'PROGRESS':<{PANEL_BAR_W+2}}  {'%':>6}  "
        f"{'CURRENT TRY':<14}  {'SPEED':>12}  {'TIME':>6}{C.RESET}  "
        f"{C.CYAN}║{C.RESET}"
    )
    sep = C.CYAN + "  ╠" + "─" * BOX + "╣" + C.RESET

    output = [top_border, col_hdr, sep] + panel_lines + [
        C.CYAN + "  ╚" + "═" * BOX + "╝" + C.RESET
    ]

    sys.stdout.write("\n".join(output) + "\n")
    sys.stdout.flush()

    return len(output)


# ─── main ─────────────────────────────────────────────────────────────────────
def main():
    clear()
    print_banner()

    typewrite("  Choose mode:", delay=0.02, color=C.CYAN)
    print(f"  {C.WHITE}1. Password Cracking Simulation (educational demo){C.RESET}")
    print(f"  {C.WHITE}2. PDF Password Cracking (real attack, parallel auto mode for unknown length){C.RESET}")
    sys.stdout.write(f"  {C.YELLOW+C.BOLD}  Mode (1 or 2): {C.RESET}")
    sys.stdout.flush()
    mode = input().strip()
    print(C.RESET, end='')

    if mode == '1':
        # ── Simulation mode ───────────────────────────────────────────────────
        typewrite("  Enter a numeric password to simulate cracking:", delay=0.02, color=C.CYAN)
        sys.stdout.write(f"  {C.YELLOW+C.BOLD}  Password: {C.RESET}")
        sys.stdout.flush()
        password = input().strip()
        print(C.RESET, end='')

        if not password:
            print(C.RED + "\n  [ERROR] No input provided." + C.RESET); sys.exit(1)
        if not password.isdigit():
            print(C.RED + "\n  [ERROR] This simulation supports numeric passwords only." + C.RESET); sys.exit(1)
        if len(password) > 10:
            print(C.RED + "\n  [ERROR] Max 10 digits for demo (keyspace would be 10 billion+)." + C.RESET); sys.exit(1)

        print()
        time.sleep(0.3)

        length, charset, charset_size      = step_detect(password)
        total                              = step_keyspace(length, charset_size)
        score, rating, entropy             = step_strength(password, charset_size)
        sim_seconds, time_data             = step_time_estimate(total)

        print()
        slow_print("  [READY] All analysis complete. Begin crack simulation?", C.YELLOW+C.BOLD, 0.1)
        ans = input(f"  {C.CYAN}  Press ENTER to start, or Q to quit: {C.RESET}").strip().lower()
        if ans == 'q':
            typewrite("  [SYS] Aborted.", delay=0.03, color=C.GRAY); return

        found_at, elapsed = step_crack(password, charset, total)

        if found_at:
            print()
            success_screen(password, found_at, elapsed, total, entropy, rating)

            typewrite("  [LOG] Writing report...", delay=0.025, color=C.YELLOW)
            charset_names = {
                10: "Digits only  [0-9]", 26: "Alpha  [a-z / A-Z]",
                52: "Mixed alpha  [a-zA-Z]", 62: "Alphanumeric  [a-zA-Z0-9]",
                95: "Full ASCII printable"
            }
            cname = charset_names.get(charset_size, f"{charset_size}-symbol charset")
            report_file = save_report(
                password, length, cname, charset_size, total,
                score, rating, entropy, time_data, found_at, elapsed, sim_seconds
            )
            print()
            typewrite(f"  [LOG] Report saved → {report_file}", delay=0.02, color=C.GREEN+C.BOLD)
            typewrite("  [LOG] Session cleared.", delay=0.025, color=C.GRAY)
            print()
            typewrite("  SIMULATION COMPLETE.", delay=0.04, color=C.GREEN+C.BOLD)
        else:
            print(f"\n  {C.RED}[FAIL] Exhausted keyspace. Password not found.{C.RESET}")

    elif mode == '2':
        # ── PDF cracking mode ─────────────────────────────────────────────────
        typewrite("  Enter the path to an encrypted PDF file to crack:", delay=0.02, color=C.CYAN)
        sys.stdout.write(f"  {C.YELLOW+C.BOLD}  PDF Path: {C.RESET}")
        sys.stdout.flush()
        pdf_path = input().strip()
        print(C.RESET, end='')

        if not pdf_path:
            print(C.RED + "\n  [ERROR] No path provided." + C.RESET); sys.exit(1)
        if not os.path.exists(pdf_path):
            print(C.RED + "\n  [ERROR] File does not exist." + C.RESET); sys.exit(1)
        if not pdf_path.lower().endswith('.pdf'):
            print(C.RED + "\n  [ERROR] File must be a PDF." + C.RESET); sys.exit(1)

        try:
            pdf = pikepdf.open(pdf_path)
            print(C.RED + "\n  [ERROR] PDF is not encrypted." + C.RESET); sys.exit(1)
        except pikepdf.PasswordError:
            pass
        except Exception as e:
            print(C.RED + f"\n  [ERROR] Invalid PDF or other error: {e}" + C.RESET); sys.exit(1)

        print(C.GREEN + f"\n  [OK] Selected: {os.path.basename(pdf_path)}" + C.RESET)
        print(C.GREEN + "  [OK] PDF is encrypted." + C.RESET)

        know_length = input(f"  {C.CYAN}  Do you know the password length? (y/n): {C.RESET}").strip().lower() == 'y'

        if know_length:
            sys.stdout.write(f"  {C.YELLOW+C.BOLD}  Length (1-10): {C.RESET}")
            sys.stdout.flush()
            try:
                length = int(input().strip())
                if length < 1 or length > 10:
                    raise ValueError
            except (ValueError, EOFError):
                print(C.RED + "\n  [ERROR] Invalid length (1-10)." + C.RESET); sys.exit(1)
            lengths_to_try = [length]
        else:
            print(C.CYAN + "  [AUTO] Will try lengths 1–10 in parallel." + C.RESET)
            lengths_to_try = list(range(1, 11))

        time.sleep(0.3)
        stop_event.clear()

        found_password = None
        total_attempts = 0
        start_time     = time.time()

        if know_length:
            # ── Known-length: polished boxed display ──────────────────────
            found_password, total_attempts, elapsed = crack_known_length(
                pdf_path, lengths_to_try[0]
            )

        else:
            # ── Parallel multi-length scan ────────────────────────────────
            print()
            printed_lines = 0

            with concurrent.futures.ThreadPoolExecutor(
                    max_workers=len(lengths_to_try)) as executor:

                future_to_len = {
                    executor.submit(try_length, pdf_path, ln): ln
                    for ln in lengths_to_try
                }
                pending = dict(future_to_len)

                while pending:
                    for future, ln in list(pending.items()):
                        if future.done():
                            del pending[future]
                            try:
                                result = future.result()
                            except Exception as e:
                                result = None
                            if result is not None:
                                found_password = result
                                for f in pending:
                                    f.cancel()
                                pending.clear()
                                break

                    if found_password:
                        break

                    printed_lines = render_parallel_panel(
                        lengths_to_try, future_to_len, pending,
                        start_time, printed_lines
                    )
                    time.sleep(0.2)

                if printed_lines:
                    clear_lines(printed_lines)

                concurrent.futures.wait(list(future_to_len.keys()), timeout=10)

            elapsed = time.time() - start_time
            with lock:
                total_attempts = sum(
                    progress.get(ln, {}).get('attempts', 0)
                    for ln in lengths_to_try
                )

        # ── Result handling ───────────────────────────────────────────────────
        if found_password:
            if not know_length:
                print(
                    f"\n  {C.GREEN}[FOUND]{C.RESET} Password "
                    f"{C.YELLOW+C.BOLD}{found_password}{C.RESET} "
                    f"discovered — all workers stopped."
                )

            keyspace = 10 ** len(found_password)
            success_screen_pdf(found_password, total_attempts, elapsed, keyspace)

            ans = input(f"  {C.CYAN}  Save decrypted PDF? (y/n): {C.RESET}").strip().lower()
            if ans == 'y':
                try:
                    pdf = pikepdf.open(pdf_path, password=found_password)
                    decrypted_path = os.path.splitext(pdf_path)[0] + '_decrypted.pdf'
                    pdf.save(decrypted_path)
                    pdf.close()
                    print(C.GREEN + f"  [OK] Decrypted PDF saved → {decrypted_path}" + C.RESET)
                except Exception as e:
                    print(C.RED + f"  [ERROR] Failed to save decrypted PDF: {e}" + C.RESET)

            pw_len   = len(found_password)
            ks_total = sum(10 ** ln for ln in lengths_to_try)
            _, time_data = step_time_estimate(ks_total)

            typewrite("  [LOG] Writing report...", delay=0.025, color=C.YELLOW)
            report_file = save_report_pdf(
                pdf_path, pw_len, "Digits only [0-9]", 10, ks_total,
                time_data, total_attempts, elapsed
            )
            print()
            typewrite(f"  [LOG] Report saved → {report_file}", delay=0.02, color=C.GREEN+C.BOLD)
            typewrite("  [LOG] Session cleared.", delay=0.025, color=C.GRAY)
            print()
            typewrite("  CRACKING COMPLETE.", delay=0.04, color=C.GREEN+C.BOLD)

        else:
            print(f"\n  {C.RED}[FAIL] Exhausted all lengths up to 10. Password not found.{C.RESET}")

    else:
        print(C.RED + "\n  [ERROR] Invalid mode selected." + C.RESET); sys.exit(1)

    print()
    input(f"  {C.GRAY}  Press Enter to exit...{C.RESET}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        stop_event.set()
        print(f"\n\n  {C.YELLOW}[!] Interrupted.{C.RESET}\n")
        sys.exit(0)
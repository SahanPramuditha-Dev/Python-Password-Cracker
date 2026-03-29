import time
import sys
import random
import os
import string
import math
import re
from datetime import datetime

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

# ─── ASCII Banner ─────────────────────────────────────────────────────────────
def print_banner():
    banner = r"""
  ██╗  ██╗ █████╗ ███████╗██╗  ██╗ ██████╗ █████╗ ████████╗
  ██║  ██║██╔══██╗██╔════╝██║  ██║██╔════╝██╔══██╗╚══██╔══╝
  ███████║███████║███████╗███████║██║     ███████║   ██║
  ██╔══██║██╔══██║╚════██║██╔══██║██║     ██╔══██║   ██║
  ██║  ██║██║  ██║███████║██║  ██║╚██████╗██║  ██║   ██║
  ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝   ╚═╝
    """
    print(C.RED + C.BOLD + banner + C.RESET)
    print(C.YELLOW + C.BOLD + "  [ BRUTE-FORCE VULNERABILITY DEMONSTRATION ]".center(78) + C.RESET)
    print(C.CYAN   + C.BOLD + "  [ University Assignment — Educational Use Only ]".center(78) + C.RESET)
    print(C.GRAY   +          "  [ No real network, hash, or system is involved in this simulation. ]".center(78) + C.RESET)
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

# ─── Formatters ──────────────────────────────────────────────────────────────
def fmt_big(n):
    if n >= 1_000_000_000_000: return f"{n/1_000_000_000_000:.2f} trillion"
    if n >= 1_000_000_000:     return f"{n/1_000_000_000:.2f} billion"
    if n >= 1_000_000:         return f"{n/1_000_000:.2f} million"
    return f"{n:,}"

def fmt_time(seconds):
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
    # (label,                   h/s,             description)
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
        t_str = fmt_time(secs)
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

    return avg / 1_000_000, time_data   # sim_seconds, full data for report

# ─── Terminal crack animation ─────────────────────────────────────────────────
def fake_hash():
    return ''.join(random.choice("0123456789abcdef") for _ in range(32))

def cracking_line(candidate, done, total, elapsed):
    pct   = (done / total) * 100 if total > 0 else 0
    bar   = progress_bar(pct)
    speed = done / elapsed if elapsed > 0 else 0
    timer = fmt_time(elapsed)
    h     = fake_hash()
    pct_s = f"{pct:5.2f}%"
    line  = (
        f"  {C.GRAY}HASH:{C.RESET} {C.GRAY}{h[:16]}...{C.RESET} "
        f"{C.GRAY}TRY:{C.RESET} {C.YELLOW+C.BOLD}{candidate}{C.RESET} "
        f"{C.GRAY}H/s:{C.RESET}{C.CYAN}{speed:>9,.0f}{C.RESET} "
        f"{C.GRAY}TIME:{C.RESET}{C.MAGENTA}{timer:>12}{C.RESET} "
        f"[{bar}{C.RESET} {pct_s}]"
    )
    w       = get_term_width()
    padding = max(0, w - visible_len(line))
    sys.stdout.write("\r" + line + " " * padding)
    sys.stdout.flush()

def step_crack(password, charset, total_combinations):
    slow_print("\n  [STEP 5] Initiating brute-force attack simulation...", C.RED + C.BOLD, 0.3)

    length   = len(password)
    keyspace = 10 ** length
    slow_print(f"  [ATTACK] Mask: {'?d' * length}   Keyspace: {fmt_big(keyspace)}\n", C.RED, 0.3)

    start           = time.time()
    milestone_shown = set()
    found_at        = None

    for i, candidate in enumerate(str(j).zfill(length) for j in range(keyspace)):
        elapsed = max(time.time() - start, 0.0001)

        if i % 3_000 == 0:
            cracking_line(candidate, i, keyspace, elapsed)
            if random.random() < 0.0008:
                clear_line()
                sys.stdout.write(f"\r  {C.BG_RED+C.WHITE+C.BOLD}  !! HASH MISMATCH !!  {C.RESET}" + " " * 40)
                sys.stdout.flush()
                time.sleep(0.07)
                clear_line()

        for threshold in [10, 25, 50, 75, 90]:
            if i / keyspace * 100 >= threshold and threshold not in milestone_shown:
                milestone_shown.add(threshold)
                clear_line()
                print(f"\n  {C.MAGENTA+C.BOLD}[!] {threshold}% of keyspace exhausted — attack continues...{C.RESET}\n")
                time.sleep(0.3)

        if candidate == password:
            elapsed  = time.time() - start
            found_at = i + 1
            clear_line()
            break

    return found_at, time.time() - start

# ─── Success screen ───────────────────────────────────────────────────────────
def success_screen(password, attempts, elapsed, keyspace, entropy, rating):
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
    print("  ║" + "  ✓  PASSWORD CRACKED  ✓".center(BOX) + "║")
    print("  ╠" + "═"*BOX + "╣" + C.RESET)

    rows = [
        ("PLAINTEXT",        f"{C.RED+C.BOLD}{password}{C.RESET}",           password),
        ("HASH (simulated)", f"{C.GRAY}{fake_hash()}{C.RESET}",              "a3f1d9c2b8e0451f"),
        ("ATTEMPTS MADE",    f"{C.CYAN}{attempts:,}{C.RESET}",               f"{attempts:,}"),
        ("KEYSPACE %",       f"{C.YELLOW}{pct_tried:.4f}%{C.RESET}",         f"{pct_tried:.4f}%"),
        ("TIME ELAPSED",     f"{C.WHITE}{fmt_time(elapsed)}{C.RESET}",       fmt_time(elapsed)),
        ("SPEED",            f"{C.WHITE}{speed:,.0f} H/s{C.RESET}",          f"{speed:,.0f} H/s"),
        ("ENTROPY",          f"{C.CYAN}{entropy:.1f} bits{C.RESET}",         f"{entropy:.1f} bits"),
        ("STRENGTH",         f"{C.RED}{rating}{C.RESET}",                    rating),
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
    lines.append("  BRUTE-FORCE VULNERABILITY DEMONSTRATION — REPORT")
    lines.append("  University Assignment | Educational Use Only")
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
    lines.append("  KEY INSIGHT:")
    lines.append("  The same password can be cracked in very different time frames")
    lines.append("  depending purely on hardware. A password safe against a throttled")
    lines.append("  login may be cracked in milliseconds on a GPU rig with a leaked hash.")
    lines.append("")

    lines.append("  SECTION 4 — LIVE SIMULATION RESULTS")
    lines.append(thin_div)
    lines.append(f"  {'Attempts made':<26}: {attempts:,}")
    lines.append(f"  {'Keyspace covered':<26}: {pct_tried:.4f}%")
    lines.append(f"  {'Time elapsed':<26}: {fmt_time(elapsed)}")
    lines.append(f"  {'Simulation speed':<26}: {speed_actual:,.0f} H/s")
    lines.append(f"  {'Result':<26}: CRACKED")
    lines.append("")

    lines.append("  SECTION 5 — WHAT THIS DEMONSTRATES")
    lines.append(thin_div)
    lines.append("")
    lines.append("  1. BRUTE-FORCE ALWAYS TERMINATES")
    lines.append("     No password is permanently safe — the question is time cost.")
    lines.append("")
    lines.append("  2. COMPUTING POWER IS THE ATTACKER'S MULTIPLIER")
    lines.append("     Upgrading from a throttled login (100 H/s) to a GPU cluster")
    lines.append("     (10 billion H/s) reduces crack time by a factor of 100,000,000.")
    lines.append("")
    lines.append("  3. PASSWORD LENGTH IS EXPONENTIAL PROTECTION")
    lines.append("     Each extra character multiplies the keyspace by the charset size.")
    lines.append(f"     Adding one digit to this password: {charset_size}x more combinations.")
    lines.append(f"     Adding two digits: {charset_size**2:,}x more combinations.")
    lines.append(f"     Adding four digits: {charset_size**4:,}x more combinations.")
    lines.append("")
    lines.append("  4. CHARSET DIVERSITY COMPOUNDS THE EFFECT")
    lines.append("     Digits only (10)  →  6-char password = 1,000,000 combinations")
    lines.append("     Full ASCII  (95)  →  6-char password = 735,091,890,625 combinations")
    lines.append("     Same length, 735,000x harder to crack.")
    lines.append("")

    lines.append("  SECTION 6 — RECOMMENDED MITIGATIONS")
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
    lines.append("  END OF REPORT")
    lines.append(divider)

    with open(report_name, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    return report_name

# ─── MAIN ─────────────────────────────────────────────────────────────────────
def main():
    clear()
    print_banner()

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

    length, charset, charset_size                  = step_detect(password)
    total                                          = step_keyspace(length, charset_size)
    score, rating, entropy                         = step_strength(password, charset_size)
    sim_seconds, time_data                         = step_time_estimate(total)

    print()
    slow_print("  [READY] All analysis complete. Begin crack simulation?", C.YELLOW+C.BOLD, 0.1)
    ans = input(f"  {C.CYAN}  Press ENTER to start, or Q to quit: {C.RESET}").strip().lower()
    if ans == 'q':
        typewrite("  [SYS] Aborted.", delay=0.03, color=C.GRAY); return

    found_at, elapsed = step_crack(password, charset, total)

    if found_at:
        success_screen(password, found_at, elapsed, total, entropy, rating)

        # ── Save report ───────────────────────────────────────────────────
        typewrite("  [LOG] Writing report...", delay=0.025, color=C.YELLOW)
        report_file = save_report(
            password, length, charset_size**0 and "Digits only [0-9]",  # charset_name lookup
            charset_size, total, score, rating, entropy,
            time_data, found_at, elapsed, sim_seconds
        )
        # Rebuild charset_name properly
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

    print()
    input(f"  {C.GRAY}  Press Enter to exit...{C.RESET}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n  {C.YELLOW}[!] Interrupted.{C.RESET}\n")
        sys.exit(0)
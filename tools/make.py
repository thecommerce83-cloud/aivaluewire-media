import os, re, subprocess, wave, numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
BG1, BG2 = (8, 12, 30), (18, 28, 64)
FG, ACC, DIM = (240, 244, 255), (61, 217, 255), (140, 150, 180)
BOLD = "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf"
REG = "/usr/share/fonts/opentype/inter/Inter-Regular.otf"
SEMI = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"
OUT = os.environ.get("OUT", "/home/claude/shorts/out")
os.makedirs(OUT, exist_ok=True)

SHORTS = {
 "01_five_tools": [
  ("You're paying for *5 tools.*\nYou need *1.*", None),
  ("Funnels.\nEmail.\nCourses.\nWebsite.\nPayments.", None),
  ("Most creators stack\n*5 subscriptions*\nto run all of that.", None),
  ("*systeme.io*\nputs it all\nin one place.", None),
  ("Free plan:\n*2,000* contacts\n*Unlimited* emails\n*3* funnels · *1* course", "Plans and limits can change. Check the site."),
  ("Start free.\n*Link in description.*", "Affiliate link: I may earn a commission."),
 ],
 "02_funnel_4_steps": [
  ("Build a sales funnel\ntoday.\n*For $0.*", None),
  ("*1.*\nCreate a free\nsysteme.io account", None),
  ("*2.*\nPick a funnel\ntemplate", None),
  ("*3.*\nAdd your offer\n+ a follow-up email", None),
  ("*4.*\nShare the link.\nThat's it.", None),
  ("Start free.\n*Link in description.*", "Affiliate link: I may earn a commission."),
 ],
 "03_free_email": [
  ("Email list under\n*2,000* people?", None),
  ("Stop paying\nfor email\nmarketing.", None),
  ("systeme.io free plan:\nup to *2,000*\ncontacts", None),
  ("*Unlimited*\nemail sends", None),
  ("Growing?\nPaid plans start\nat *$17/month.*", "Prices as listed on systeme.io/pricing."),
  ("Start free.\n*Link in description.*", "Affiliate link: I may earn a commission."),
 ],
 "04_first_course": [
  ("What you know\nis a *product.*", None),
  ("Record\n*5 short lessons*\non your phone.", None),
  ("Upload them as\n*1 free course*\non systeme.io", None),
  ("Sell it with\n*0%* systeme.io\ntransaction fees", "Payment processor fees (Stripe/PayPal) still apply."),
  ("Your first sale\ncan happen\n*this week.*", None),
  ("Start free.\n*Link in description.*", "Affiliate link: I may earn a commission."),
 ],
 "05_one_person_business": [
  ("A one-person\nbusiness needs\n*3 things.*", None),
  ("*1.* An offer\n\nAI can help\nyou write it.", None),
  ("*2.* A page\nthat sells it", None),
  ("*3.* Emails\nthat follow up", None),
  ("*2* and *3*?\nsysteme.io\nfree plan.", None),
  ("Start free.\n*Link in description.*", "Affiliate link: I may earn a commission."),
 ],
}
DUR = [3.0, 3.6, 3.6, 3.6, 3.8, 3.4]

def bg():
    y = np.linspace(0, 1, H)[:, None]
    x = np.linspace(0, 1, W)[None, :]
    t = np.clip(0.6 * y + 0.4 * x, 0, 1)[..., None]
    arr = (np.array(BG1) * (1 - t) + np.array(BG2) * t)
    # soft glow
    d = np.sqrt((x - 0.8) ** 2 + (y - 0.15) ** 2)[..., None]
    arr = arr + np.array([20, 60, 90]) * np.exp(-(d / 0.35) ** 2)
    return Image.fromarray(np.clip(arr, 0, 255).astype("uint8"))
BG = bg()

def tokens(line):
    out = []
    for i, part in enumerate(re.split(r"\*", line)):
        for w in part.split(" "):
            if w: out.append((w, i % 2 == 1))
    return out

def card(text, note, idx, n, path):
    im = BG.copy(); d = ImageDraw.Draw(im)
    d.text((90, 150), "AI VALUE WIRE", font=ImageFont.truetype(SEMI, 34), fill=ACC)
    d.line((90, 205, 250, 205), fill=ACC, width=4)
    lines = text.split("\n")
    size = 104
    while True:
        f = ImageFont.truetype(BOLD, size)
        sp = d.textlength(" ", font=f)
        widths = [sum(d.textlength(w, font=f) for w, _ in tokens(l)) + sp * max(len(tokens(l)) - 1, 0) for l in lines]
        if max(widths) <= W - 180 or size <= 60: break
        size -= 4
    lh = int(size * 1.22)
    total = lh * len(lines)
    y = 860 - total // 2
    for l, wd in zip(lines, widths):
        x = 90
        for w, hi in tokens(l):
            d.text((x, y), w, font=f, fill=ACC if hi else FG)
            x += d.textlength(w, font=f) + sp
        y += lh
    if note:
        fn = ImageFont.truetype(REG, 38)
        d.text((90, y + 50), note, font=fn, fill=DIM)
    # progress dots
    for i in range(n):
        cx = 90 + i * 34
        d.ellipse((cx, 1340, cx + 16, 1356), fill=ACC if i <= idx else (60, 70, 100))
    im.save(path)

def run(cmd):
    subprocess.run(cmd, check=True, capture_output=True)

def music(path, dur):
    sr = 44100; t = np.arange(int(sr * dur)) / sr
    chords = [[220, 277.18, 329.63], [196, 246.94, 293.66], [174.61, 220, 261.63], [196, 246.94, 293.66]]
    seg = dur / len(chords) if dur < 8 else 4.0
    sig = np.zeros_like(t)
    for i, ch in enumerate(chords * 10):
        s, e = i * seg, (i + 1) * seg + 0.8
        if s >= dur: break
        m = (t >= s) & (t < e)
        tt = t[m] - s
        env = np.minimum(1, tt / 0.6) * np.minimum(1, (e - s - tt) / 0.8)
        for fq in ch:
            sig[m] += env * (np.sin(2 * np.pi * fq * tt) + 0.3 * np.sin(2 * np.pi * fq * 2 * tt))
    # gentle pulse
    pulse = 0.5 * (1 + np.sin(2 * np.pi * 2 * t)) * 0.15
    sig = sig * (0.85 + pulse)
    fade = np.minimum(1, np.minimum(t / 1.0, (dur - t) / 1.5))
    sig = sig * fade
    sig = sig / np.max(np.abs(sig)) * 0.25
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((sig * 32767).astype("<i2").tobytes())

ENC = ["-c:v", "libx264", "-crf", "18", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-r", "30"]
import sys
only_frames = "--frames" in sys.argv
for name, cards in SHORTS.items():
    wd = f"{OUT}/{name}"; os.makedirs(wd, exist_ok=True)
    lst = []
    for i, (txt, note) in enumerate(cards):
        png = f"{wd}/c{i}.png"; card(txt, note, i, len(cards), png)
        if only_frames: continue
        du = DUR[i]; tmp = f"{wd}/c{i}.tmp.mp4"
        vf = f"format=yuv420p,loop=-1:1,trim=duration={du},fade=t=in:st=0:d=0.25,fade=t=out:st={du-0.2}:d=0.2"
        run(["ffmpeg", "-y", "-framerate", "30", "-i", png, "-vf", vf] + ENC + [tmp])
        os.rename(tmp, f"{wd}/c{i}.mp4"); lst.append(f"file 'c{i}.mp4'")
    if only_frames: continue
    open(f"{wd}/list.txt", "w").write("\n".join(lst))
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", f"{wd}/list.txt", "-c", "copy", f"{wd}/v.mp4"])
    total = sum(DUR[:len(cards)])
    music(f"{wd}/m.wav", total)
    tmp = f"{OUT}/{name}.tmp.mp4"
    run(["ffmpeg", "-y", "-i", f"{wd}/v.mp4", "-i", f"{wd}/m.wav", "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "128k", "-shortest", tmp])
    os.rename(tmp, f"{OUT}/{name}.mp4")
print("done")

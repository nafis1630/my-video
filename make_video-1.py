#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
make_video.py - Bangla "story explainer" video maker (vertical 9:16, 720x1280)

Style: flat illustrated scenes + highlighted Bangla captions + Bangla voice-over,
story first, book/law later, one quotable closing line.
This file makes the video for Robert Greene's Law 9
("Win Through Your Actions, Never Through Argument").

RUN (nothing to configure - missing packages / Chromium are installed automatically):
    python make_video.py                 # voice-over + video  -> law09_video.mp4
    python make_video.py --preview       # fast: one PNG per scene in ./preview  (check layout first)
    python make_video.py --no-voice      # silent video (e.g. if you will record your own voice)

Options:
    --voice bn-BD-PradeepNeural          # male voice (default: bn-BD-NabanitaNeural, female)
    --fps 30   --hd (1080x1920)   --out my.mp4   --rate -10%  (slower speech)

TO MAKE A DIFFERENT VIDEO: edit CHANNEL and the SCENES list below. Nothing else.
Scene types ("v"): chat, time, stage, big, steps, book, pair, bars, question, outro.
Mark highlighted words with **double stars**.
Needs internet on first run (pip, Chromium, Google Fonts, Microsoft Edge TTS).
"""
import argparse
import asyncio
import copy
import importlib
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# ----------------------------------------------------------------------------
# SETTINGS
# ----------------------------------------------------------------------------
CHANNEL = "your.channel"            # shown at the top of every scene and in the final call-to-action
VOICE = "bn-BD-NabanitaNeural"      # or bn-BD-PradeepNeural (male), bn-IN-TanishaaNeural, bn-IN-BashkarNeural
RATE = "-6%"                        # speaking speed
FPS = 30
W, H = 720, 1280
MIN_DUR = 2.6                       # shortest scene, seconds
LEAD, TAIL = 0.30, 0.55             # silence before / after each narration line
OUT = "law09_video.mp4"

# ----------------------------------------------------------------------------
# CONTENT  (edit me)
# ----------------------------------------------------------------------------
def P(**kw):
    return kw

ANIK = P(skin="#a06f4c", hair="#1b1310", top="#1f5e5b", bottom="#34302c", hs="short")
MAMA = P(skin="#98694a", hair="#9a9a9a", top="#c9a66b", bottom="#e9e0cc", hs="grey", glasses=True, stache=True)
KHALA = P(skin="#a8764f", hair="#2a1d18", top="#a8402f", hs="bun", sari=True)

SCENES = [
    # 1. hook - present day, the relative who objected is now the first to congratulate
    dict(v="chat", bg="cream", chip="● আজ",
         d=dict(title="পরিবার", sub="মা, মামা, খালা, অনিক +৯",
                msgs=[["মামা", "অনিকের ক্যাফেতে আজ লাইন লেগে গেছে!"],
                      ["খালা", "ওই অনিক? যে চাকরি ছেড়েছিল?"],
                      ["মামা", "আমি তো প্রথম থেকেই জানতাম, ও পারবে!"]]),
         cap="আজ মামাই **সবার আগে** অভিনন্দন জানালেন—",
         say="পরিবারের গ্রুপে মামা লিখলেন, অনিকের ক্যাফেতে আজ লাইন লেগে গেছে! আজ মামাই সবার আগে অভিনন্দন জানালেন।"),

    # 2. flashback
    dict(v="time", bg="dark", d=dict(head="ফ্ল্যাশব্যাক", body="এক বছর আগে"),
         cap="কিন্তু এক বছর আগে, ছবিটা ছিল **উল্টো।**"),

    # 3. the objection
    dict(v="stage", bg="cream", chip="◷ এক বছর আগে",
         d=dict(bg="dining",
                people=[dict(ANIK, x=150, mood="neutral"),
                        dict(MAMA, x=360, mood="happy", arm="point"),
                        dict(KHALA, x=570, mood="neutral")],
                bubbles=[dict(t="চাকরি ছেড়ে ক্যাফে? ওসব হয় না!", x=225, y=200, w=380)]),
         cap="চাকরি ছাড়ার কথা শুনে মামা **হেসে উড়িয়ে দিলেন**—"),

    # 4. the argument
    dict(v="stage", bg="cream", chip="◷ এক বছর আগে",
         d=dict(bg="dining",
                people=[dict(ANIK, x=190, mood="angry", arm="up"),
                        dict(MAMA, x=410, mood="neutral"),
                        dict(KHALA, x=600, mood="sad")],
                bubbles=[dict(t="আমি হিসাব করে দেখেছি— সব তথ্য আছে!", x=40, y=190, w=430)]),
         cap="অনিকও ছাড়ল না। **যুক্তি** সাজিয়ে তর্কে নামল।"),

    # 5. wins the argument, loses the person
    dict(v="stage", bg="cream", chip="◷ এক বছর আগে",
         d=dict(bg="dining",
                people=[dict(ANIK, x=190, mood="sad"),
                        dict(MAMA, x=410, mood="angry", arm="cross"),
                        dict(KHALA, x=600, mood="neutral")],
                bubbles=[dict(t="যা-ই বলিস, আমি মানছি না!", x=250, y=200, w=380)]),
         cap="যুক্তিতে অনিক জিতল। কিন্তু মামা **এক ইঞ্চিও** নড়লেন না।"),

    # 6. the twist line
    dict(v="big", bg="dark", d=dict(lines=["তর্কে জিতেছিল,", "**মানুষটাকে** হারিয়েছিল।"]),
         say="তর্কে জিতেছিল, কিন্তু মানুষটাকে হারিয়েছিল।"),

    # 7. the decision
    dict(v="stage", bg="night", chip="◷ সেদিন রাতে",
         d=dict(bg="room",
                people=[dict(ANIK, x=250, y=735, s=1.12, mood="sad")],
                bubbles=[dict(t="আর বোঝাব না…", x=330, y=170, w=300, at=0.9),
                         dict(t="এবার কাজ দিয়েই বলব।", x=330, y=300, w=330, at=2.4)]),
         cap="অনিক ঠিক করল— আর বোঝাবে না, **দেখিয়ে** দেবে।"),

    # 8. the quiet work
    dict(v="steps", bg="cream", chip="◷ ছয় মাস",
         d=dict(items=["ভোর ৫টায় বাজার", "প্রথম কাস্টমারের হাসি", "প্রথম মাসের লাভ"]),
         cap="পরের ছয় মাস সে শুধু **কাজ** করল। একটাও তর্ক না।"),

    # 9. the payoff
    dict(v="stage", bg="sage", chip="● একদিন",
         d=dict(bg="cafe",
                people=[dict(MAMA, x=190, mood="happy"),
                        dict(ANIK, x=545, mood="happy", arm="up")],
                bubbles=[dict(t="…চা-টা কিন্তু ভালো হয়েছে।", x=60, y=215, w=380)]),
         cap="একদিন মামা নিজেই চা খেতে এলেন। আর কাউকে কিছু **বোঝাতে হলো না।**"),

    # 10-11. the book and the law
    dict(v="book", bg="plum", d=dict(author="রবার্ট গ্রিন", title="THE 48 LAWS OF POWER"),
         cap="রবার্ট গ্রিনের বই—", plain=True),
    dict(v="book", bg="plum",
         d=dict(author="রবার্ট গ্রিন", title="THE 48 LAWS OF POWER", law="LAW 09",
                sub="Win Through Your Actions, Never Through Argument"),
         cap="নবম আইন—", plain=True),

    # 12. the idea
    dict(v="pair", bg="cream",
         d=dict(a=dict(t="তর্ক", sub="মানুষ শক্ত হয়", c="accent"), mid="vs",
                b=dict(t="প্রমাণ", sub="মানুষ নিজেই মানে", c="teal")),
         cap="বইটা বলছে— তর্কে মানুষ **শক্ত** হয়, কাজ দেখলে **নরম।**"),

    # 13. the reframe
    dict(v="pair", bg="cream",
         d=dict(a=dict(t="চুপ থাকা", c="teal"), mid="neq", b=dict(t="হার মানা", c="plum")),
         cap="তর্ক না করা মানে **হার মানা নয়।**"),

    # 14. the meaning
    dict(v="bars", bg="sage",
         d=dict(title="শক্তি কোথায় যাচ্ছে?",
                bars=[dict(label="কথা", v=0.16, c="grey"), dict(label="কাজ", v=0.92, c="teal")]),
         cap="মানে— শক্তিটা কথায় না ঢেলে **কাজে** ঢালা।"),

    # 15. the question for the viewer
    dict(v="question", bg="cream",
         d=dict(small="পরের বার তর্ক শুরু হলে নিজেকে জিজ্ঞেস করো—",
                big="“এটা কি **তর্কের** সময়, না **প্রমাণের** সময়?”"),
         say="পরের বার তর্ক শুরু হলে নিজেকে জিজ্ঞেস করো— এটা কি তর্কের সময়, না প্রমাণের সময়?"),

    # 16-17. the closing line + call to action
    dict(v="outro", bg="plum", d=dict(line="তর্কটা ছেড়ে দাও।\nজবাবটা **কাজই** দেবে।"),
         say="তর্কটা ছেড়ে দাও। জবাবটা কাজই দেবে।"),
    dict(v="outro", bg="plum", d=dict(line="তর্কটা ছেড়ে দাও।\nজবাবটা **কাজই** দেবে।", cta=True),
         say="এমন আরও গল্পের জন্য ফলো করুন।"),
]

# ----------------------------------------------------------------------------
# PAGE (HTML + CSS + JS).  Each scene is built once; one global clock drives
# every animation, so frames are rendered deterministically.
# ----------------------------------------------------------------------------
HTML = r"""<!doctype html>
<html lang="bn"><head><meta charset="utf-8">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Hind+Siliguri:wght@400;500;600;700&family=Lora:wght@500;600&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:__W__px;height:__H__px;overflow:hidden;background:#000;
  font-family:'Hind Siliguri','Noto Sans Bengali','Nirmala UI','Kohinoor Bangla','Vrinda','FreeSans',sans-serif}
.scene{position:absolute;left:0;top:0;width:__W__px;height:__H__px;display:none;overflow:hidden}
.bg-cream{background:linear-gradient(180deg,#efe7d8,#e3d8c3)}
.bg-sage{background:linear-gradient(180deg,#dfe7dc,#cdd6ca)}
.bg-dark{background:#25201d}
.bg-plum{background:#3a1c28}
.bg-night{background:linear-gradient(180deg,#2a3150,#1a1f37)}
.art{position:absolute;left:0;top:0;width:__W__px;height:__H__px}
.brand{position:absolute;top:34px;left:0;right:0;display:flex;justify-content:center;align-items:center;gap:12px;
  font:600 23px 'Lora',Georgia,serif;color:#6d5f50;letter-spacing:.5px}
.brand .l{display:block;width:34px;height:2px;background:currentColor;opacity:.5}
.on-dark .brand{color:#d8c9b3}
.brand,.chip{z-index:5}
.chip{position:absolute;top:88px;left:0;right:0;display:flex;justify-content:center}
.chip div{background:#f6f1e7;border-radius:999px;padding:5px 24px 7px;font-size:27px;font-weight:600;color:#5a4a3c;box-shadow:0 2px 8px rgba(0,0,0,.12)}
.on-dark .chip div{background:#4a4038;color:#efe3d0}
.cap{position:absolute;left:52px;right:52px;bottom:92px;background:#f7f2e8;border-radius:26px;padding:24px 30px 28px;
  font-size:46px;line-height:1.42;font-weight:600;color:#2a2320;text-align:center;box-shadow:0 10px 28px rgba(0,0,0,.2)}
.cap.plain{background:none;box-shadow:none;color:#efe3d0;font-size:48px}
.cap b,.l b,.q2 b,.o1 b{color:#cf4f25;font-weight:700}
.on-dark .cap:not(.plain){background:#f1ead9}
/* chat */
.phone{position:absolute;left:78px;top:170px;width:564px;height:700px;background:#f3ecdf;border:10px solid #2a2320;border-radius:50px;overflow:hidden;display:flex;flex-direction:column}
.ph{background:#1f5e5b;color:#fff;padding:22px 26px;display:flex;gap:16px;align-items:center}
.av{width:58px;height:58px;border-radius:50%;background:#e8c9a0;border:4px solid #f3ecdf}
.t1{font-size:34px;font-weight:700}.t2{font-size:21px;opacity:.85}
.msgs{flex:1;display:flex;flex-direction:column;justify-content:flex-end;gap:18px;padding:22px}
.msg{align-self:flex-start;max-width:430px;background:#fffaf0;border-radius:20px;padding:12px 20px 14px;font-size:31px;line-height:1.4;color:#2a2320;box-shadow:0 2px 6px rgba(0,0,0,.12)}
.msg small{display:block;color:#cf4f25;font-size:21px;font-weight:700}
.inp{margin:0 22px 22px;background:#fffaf0;border-radius:999px;padding:12px 24px;font-size:24px;color:#9a8e80}
/* centered column helpers */
.col{display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center}
.time{gap:44px;padding-bottom:200px}
.cal{width:440px;background:#f6f1e7;border-radius:24px;overflow:hidden;box-shadow:0 12px 30px rgba(0,0,0,.35)}
.calh{background:#d2552b;color:#fff;font-size:36px;font-weight:700;padding:14px}
.calb{font-size:78px;font-weight:700;color:#2a2320;padding:34px 10px 40px}
/* stage */
.stage{position:absolute;left:0;top:140px;width:720px;height:860px}
.bub{position:absolute;background:#fff7f1;border:3px solid #d2552b;border-radius:28px;padding:12px 22px 14px;font-size:31px;font-weight:600;color:#6e2510;line-height:1.38;transform-origin:20% 100%}
.bub:after{content:'';position:absolute;bottom:-15px;left:38px;width:24px;height:24px;background:#fff7f1;border-right:3px solid #d2552b;border-bottom:3px solid #d2552b;transform:rotate(45deg)}
.bub.tr:after{left:auto;right:38px}
/* big text */
.big{display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center;padding:0 40px 120px}
.big .l{font-size:76px;font-weight:700;line-height:1.38;color:#f2e9da}
.big .l b{color:#e8693e}
/* steps */
.steps{padding:290px 80px 0 80px}
.st{display:flex;align-items:center;gap:26px;margin-bottom:58px}
.dot{width:88px;height:88px;flex:none;border-radius:50%;background:#1f5e5b;color:#fff;font-size:46px;font-weight:700;display:flex;align-items:center;justify-content:center}
.stt{flex:1;font-size:45px;font-weight:600;background:#f7f2e8;padding:16px 26px 18px;border-radius:22px;color:#2a2320;box-shadow:0 4px 12px rgba(0,0,0,.1)}
/* book / outro (plum) */
.frame{position:absolute;left:40px;top:40px;right:40px;bottom:40px;border:2px solid rgba(217,168,91,.38)}
.bk{position:absolute;left:0;right:0;top:250px;display:flex;flex-direction:column;align-items:center;text-align:center;gap:20px}
.au{font-size:36px;font-weight:500;color:#d9a85b}
.ti{font:600 58px/1.25 'Lora',Georgia,serif;color:#e9dcc6;letter-spacing:1px}
.rule{width:150px;height:3px;background:#d9a85b;transform-origin:0 50%}
.lw{font:500 34px 'Lora',Georgia,serif;color:#d9a85b;letter-spacing:6px}
.ls{font:500 italic 40px/1.35 'Lora',Georgia,serif;color:#e9dcc6;padding:0 90px}
.out{padding:0 56px 60px;gap:34px}
.o1{font-size:72px;font-weight:700;line-height:1.4;color:#f3e8d3}
.o1 b{color:#d9a85b}
.o2{font-size:34px;color:#d8c9b3}
.pill{border:2px solid #d9a85b;border-radius:999px;padding:12px 40px 14px;font-size:38px;color:#f3e8d3}
.pill b{color:#d9a85b;font-weight:700}
/* pair */
.pair{display:flex;flex-direction:column;justify-content:center;padding:200px 64px 340px}
.pc{border-radius:32px;padding:38px 20px 40px;text-align:center;color:#fff;box-shadow:0 8px 22px rgba(0,0,0,.18)}
.pc.teal{background:#1f5e5b}.pc.plum{background:#3a1c28}.pc.accent{background:#cf4f25}
.pt{font-size:80px;font-weight:700;line-height:1.3}.ps{font-size:36px;opacity:.92;margin-top:4px}
.mid{align-self:center;width:112px;height:112px;border-radius:50%;background:#2a2320;color:#fff;font:700 44px 'Lora',Georgia,serif;
  display:flex;align-items:center;justify-content:center;margin:-34px 0;z-index:2;border:8px solid #ece3d2}
/* bars */
.bars{display:flex;flex-direction:column;align-items:center;justify-content:center;padding:150px 0 300px;gap:50px}
.bt{font-size:46px;font-weight:600;color:#2a2320}
.bw{display:flex;gap:90px;align-items:flex-end;height:500px}
.bc{display:flex;flex-direction:column;align-items:center;gap:14px;justify-content:flex-end;height:100%}
.bar{width:180px;border-radius:20px 20px 0 0;background:#1f5e5b;transform-origin:50% 100%}
.bar.grey{background:#a89c8b}
.bl{font-size:50px;font-weight:700;color:#2a2320}
/* question */
.q{padding:0 56px 120px;gap:46px}
.q1{font-size:40px;font-weight:500;color:#6a5b4d;line-height:1.5}
.q2{font-size:70px;font-weight:700;line-height:1.42;color:#2a2320}
</style></head>
<body><div id="root"></div>
<script>
const XF = 0.35;
const CH = "__CHANNEL__";
const md = s => (s || '').replace(/\*\*(.+?)\*\*/g, '<b>$1</b>').replace(/\n/g, '<br>');
const ANIMS = {
  fade:  [{opacity:0},{opacity:1}],
  up:    [{opacity:0,transform:'translateY(40px)'},{opacity:1,transform:'translateY(0px)'}],
  pop:   [{opacity:0,transform:'scale(.8)'},{opacity:1,transform:'scale(1)'}],
  left:  [{opacity:0,transform:'translateX(-80px)'},{opacity:1,transform:'translateX(0px)'}],
  right: [{opacity:0,transform:'translateX(80px)'},{opacity:1,transform:'translateX(0px)'}],
  growy: [{transform:'scaleY(0)'},{transform:'scaleY(1)'}],
  growx: [{transform:'scaleX(0)'},{transform:'scaleX(1)'}],
  bob:   [{transform:'translateY(0px)'},{transform:'translateY(-7px)'}],
};

/* ---------- flat-style people ---------- */
function person(p){
  const sk=p.skin||'#9a6a48', hr=p.hair||'#1b1310', tp=p.top||'#1f5e5b', bt=p.bottom||'#3a3430';
  const mood=p.mood||'neutral', arm=p.arm||'down', hs=p.hs||'short';
  let o='';
  if(p.sari){
    o+=`<path d="M-48,-132 L-60,-6 Q0,8 60,-6 L48,-132Z" fill="${tp}"/><path d="M-48,-132 L-60,-6 Q-34,0 -20,0 L-14,-132Z" fill="rgba(0,0,0,.14)"/>`;
  } else {
    o+=`<rect x="-27" y="-132" width="23" height="132" rx="9" fill="${bt}"/><rect x="4" y="-132" width="23" height="132" rx="9" fill="${bt}"/><ellipse cx="-16" cy="1" rx="21" ry="7" fill="#1b1310"/><ellipse cx="16" cy="1" rx="21" ry="7" fill="#1b1310"/>`;
  }
  o+=`<path d="M-46,-118 L-42,-246 Q0,-270 42,-246 L46,-118Z" fill="${tp}"/>`;
  if(p.sari) o+=`<path d="M-42,-246 L40,-130 L46,-118 L10,-118 L-42,-200Z" fill="rgba(255,255,255,.2)"/>`;
  const A={
    down:[[-40,-238,-56,-140],[40,-238,56,-140]],
    up:[[-40,-238,-56,-140],[40,-238,76,-338]],
    point:[[-40,-238,-56,-140],[40,-238,106,-248]],
    cross:[[-40,-238,16,-182],[40,-238,-16,-196]],
  }[arm];
  A.forEach(a=>{ o+=`<line x1="${a[0]}" y1="${a[1]}" x2="${a[2]}" y2="${a[3]}" stroke="rgba(0,0,0,.28)" stroke-width="25" stroke-linecap="round"/><line x1="${a[0]}" y1="${a[1]}" x2="${a[2]}" y2="${a[3]}" stroke="${tp}" stroke-width="21" stroke-linecap="round"/><circle cx="${a[2]}" cy="${a[3]}" r="11.5" fill="${sk}"/>`; });
  o+=`<rect x="-10" y="-272" width="20" height="26" fill="${sk}"/>`;
  if(hs==='grey') o+=`<ellipse cx="-34" cy="-300" rx="9" ry="14" fill="#cfcfcf"/><ellipse cx="34" cy="-300" rx="9" ry="14" fill="#cfcfcf"/>`;
  o+=`<circle cx="0" cy="-302" r="35" fill="${sk}"/>`;
  const cap=`<path d="M-37,-298 Q-42,-346 0,-344 Q42,-346 37,-298 Q22,-324 0,-324 Q-22,-324 -37,-298Z" fill="${hr}"/>`;
  if(hs==='short') o+=cap;
  if(hs==='bun') o+=`<circle cx="0" cy="-353" r="17" fill="${hr}"/>`+cap;
  // face
  o+=`<circle cx="-12" cy="-306" r="3.8" fill="#1b1310"/><circle cx="12" cy="-306" r="3.8" fill="#1b1310"/>`;
  const st='stroke="#1b1310" stroke-width="3.4" fill="none" stroke-linecap="round"';
  if(mood==='angry') o+=`<path d="M-21,-322 L-6,-315" ${st}/><path d="M21,-322 L6,-315" ${st}/>`;
  if(mood==='sad')   o+=`<path d="M-21,-316 L-6,-322" ${st}/><path d="M21,-316 L6,-322" ${st}/>`;
  const M={neutral:'M-9,-285 L9,-285',happy:'M-13,-289 Q0,-273 13,-289',sad:'M-10,-281 Q0,-292 10,-281',angry:'M-10,-282 Q0,-288 10,-282'};
  o+=`<path d="${M[mood]||M.neutral}" ${st}/>`;
  if(p.glasses) o+=`<circle cx="-12" cy="-306" r="12.5" ${st}/><circle cx="12" cy="-306" r="12.5" ${st}/><path d="M-1,-306 L1,-306" ${st}/>`;
  if(p.stache) o+=`<path d="M-14,-293 Q-7,-299 0,-294 Q7,-299 14,-293 Q7,-287 0,-291 Q-7,-287 -14,-293Z" fill="${hr}"/>`;
  return o;
}

/* ---------- stage backdrops (SVG 720x860) ---------- */
const BGS = {
  dining:()=>{
    const pts=[...Array(11)].map((_,i)=>[i*72,62+26*Math.sin(i*.95)]);
    const line=pts.map((p,i)=>(i?'L':'M')+p[0]+','+p[1]).join(' ');
    const dots=pts.map((p,i)=>`<circle cx="${p[0]}" cy="${p[1]+11}" r="9" fill="${['#d2552b','#d9a85b','#f2e3b8'][i%3]}"/>`).join('');
    return `<rect y="-200" width="720" height="1200" fill="#dccfb8"/><rect y="670" width="720" height="400" fill="#c6b592"/>
      <path d="${line}" stroke="#6d5f50" stroke-width="3" fill="none"/>${dots}
      <rect x="520" y="150" width="130" height="170" rx="6" fill="#efe6d2" stroke="#9b8a6e" stroke-width="7"/>
      <circle cx="585" cy="215" r="26" fill="#c9a66b"/><rect x="552" y="248" width="66" height="50" rx="10" fill="#8a5a3c"/>`;
  },
  cafe:()=>{
    const lamps=[345,465,585].map(x=>`<line x1="${x}" y1="0" x2="${x}" y2="150" stroke="#4a4038" stroke-width="3"/><path d="M${x-36},192 Q${x},118 ${x+36},192Z" fill="#2b5a56"/><circle cx="${x}" cy="196" r="9" fill="#f6d98a"/>`).join('');
    const cups=[0,1,2,3,4].map(i=>`<rect x="${425+i*52}" y="298" width="32" height="34" rx="6" fill="${['#e8dcc2','#c9a66b','#e8dcc2','#d2552b','#e8dcc2'][i]}"/>`).join('');
    return `<rect y="-200" width="720" height="1200" fill="#d5dfd1"/><rect y="670" width="720" height="400" fill="#bba98a"/>
      <rect x="50" y="64" width="250" height="86" rx="12" fill="#2b5a56"/>
      <text x="175" y="126" text-anchor="middle" font-size="52" font-weight="700" fill="#f3ead8">ক্যাফে</text>
      <rect x="60" y="210" width="210" height="270" rx="6" fill="#eaf2e7" stroke="#8a7d68" stroke-width="8"/>
      <line x1="165" y1="210" x2="165" y2="480" stroke="#8a7d68" stroke-width="6"/><line x1="60" y1="345" x2="270" y2="345" stroke="#8a7d68" stroke-width="6"/>
      ${lamps}<rect x="410" y="332" width="290" height="10" fill="#8a5a3c"/>${cups}`;
  },
  room:()=>{
    const stars=[[470,150],[520,250],[610,140],[590,330],[500,350]].map(s=>`<circle cx="${s[0]}" cy="${s[1]}" r="3" fill="#f2e9c9"/>`).join('');
    const books=[0,1,2,3,4,5,6].map(i=>`<rect x="${52+i*20}" y="${250-(i%3)*14}" width="16" height="${100+(i%3)*14}" fill="${['#8a3f2f','#2b5a56','#c9a66b'][i%3]}"/>`).join('');
    return `<rect y="-200" width="720" height="1200" fill="#232a47"/>
      <rect x="440" y="110" width="210" height="300" rx="6" fill="#0f1430" stroke="#3b4468" stroke-width="9"/>
      <line x1="545" y1="110" x2="545" y2="410" stroke="#3b4468" stroke-width="6"/><line x1="440" y1="260" x2="650" y2="260" stroke="#3b4468" stroke-width="6"/>
      <circle cx="590" cy="200" r="32" fill="#f2e9c9"/>${stars}
      <rect x="40" y="190" width="170" height="330" fill="#171c33"/><rect x="40" y="350" width="170" height="8" fill="#3b4468"/>${books}`;
  },
};
const FGS = {
  dining:()=>`<rect x="30" y="592" width="660" height="26" rx="8" fill="#8a5a3c"/><rect x="44" y="618" width="632" height="500" fill="#f3eee2"/>
    <ellipse cx="190" cy="588" rx="36" ry="8" fill="#fff"/><ellipse cx="360" cy="588" rx="36" ry="8" fill="#fff"/><ellipse cx="530" cy="588" rx="36" ry="8" fill="#fff"/>
    <rect x="270" y="556" width="34" height="34" rx="7" fill="#d2552b"/><rect x="430" y="560" width="30" height="30" rx="7" fill="#1f5e5b"/>`,
  cafe:()=>`<rect x="370" y="612" width="350" height="500" fill="#2b5a56"/><rect x="360" y="592" width="370" height="26" rx="7" fill="#e8dcc2"/>
    <rect x="420" y="508" width="120" height="84" rx="8" fill="#4a4038"/><rect x="432" y="494" width="96" height="16" rx="5" fill="#6d5f50"/><circle cx="480" cy="560" r="10" fill="#d9a85b"/>
    <rect x="620" y="560" width="34" height="32" rx="6" fill="#f3ead8"/><rect x="668" y="560" width="34" height="32" rx="6" fill="#f3ead8"/>`,
  room:()=>`<defs><radialGradient id="gl"><stop offset="0" stop-color="#ffd98a" stop-opacity=".55"/><stop offset="1" stop-color="#ffd98a" stop-opacity="0"/></radialGradient></defs>
    <circle cx="620" cy="500" r="190" fill="url(#gl)"/>
    <rect x="0" y="606" width="720" height="500" fill="#4a3123"/><rect x="0" y="594" width="720" height="22" fill="#6b472f"/>
    <rect x="320" y="496" width="150" height="98" rx="9" fill="#8f93a6"/><circle cx="395" cy="545" r="9" fill="#c6c9d8"/>
    <line x1="620" y1="594" x2="628" y2="478" stroke="#c7a46a" stroke-width="8"/><path d="M585,478 L675,478 L652,432 L608,432Z" fill="#d9a85b"/>`,
};
function stage(d){
  const B=BGS[d.bg](), F=(FGS[d.bg]||(()=>''))();
  const ppl=d.people.map((p,i)=>{
    const s=p.s||1.05, y=p.y||730, dir=p.dir||1;
    return `<g transform="translate(${p.x},${y}) scale(${s*dir},${s})"><g data-a="up" data-d="${0.15+i*0.18}" data-t="0.6"><g data-a="bob">${person(p)}</g></g></g>`;
  }).join('');
  const bub=(d.bubbles||[]).map((b,i)=>`<div class="bub ${b.tail==='r'?'tr':''}" style="left:${b.x}px;top:${b.y}px;max-width:${b.w||320}px" data-a="pop" data-d="${b.at!==undefined?b.at:(0.9+i*1.2)}" data-t="0.35">${b.t}</div>`).join('');
  return `<div class="art"><div class="stage"><svg viewBox="0 0 720 860" width="720" height="860" style="overflow:visible" xmlns="http://www.w3.org/2000/svg">${B}${ppl}${F}</svg>${bub}</div></div>`;
}

/* ---------- scene types ---------- */
const V = {
  chat:d=>`<div class="art"><div class="phone" data-a="up" data-d="0.05" data-t="0.6"><div class="ph"><div class="av"></div><div><div class="t1">${d.title}</div><div class="t2">${d.sub||''}</div></div></div>
    <div class="msgs">${d.msgs.map((m,i)=>`<div class="msg" data-a="up" data-d="${0.5+i*1.4}" data-t="0.45"><small>${m[0]}</small>${m[1]}</div>`).join('')}</div><div class="inp">মেসেজ লিখুন</div></div></div>`,
  time:d=>`<div class="art col time"><svg width="190" height="120" viewBox="0 0 190 120" data-a="pop" data-d="0.1"><path d="M90,10 L90,110 L20,60Z" fill="#d2552b"/><path d="M180,10 L180,110 L110,60Z" fill="#d2552b"/></svg>
    <div class="cal" data-a="up" data-d="0.35" data-t="0.6"><div class="calh">${d.head}</div><div class="calb">${d.body}</div></div></div>`,
  stage:stage,
  big:d=>`<div class="art big">${d.lines.map((l,i)=>`<div class="l" data-a="up" data-d="${0.2+i*0.9}" data-t="0.6">${md(l)}</div>`).join('')}</div>`,
  steps:d=>`<div class="art steps">${d.items.map((t,i)=>`<div class="st" data-a="left" data-d="${0.2+i*1.1}" data-t="0.5"><div class="dot">${'১২৩৪৫'[i]}</div><div class="stt">${t}</div></div>`).join('')}</div>`,
  book:d=>`<div class="art"><div class="frame"></div><div class="bk">
    <svg width="120" height="156" viewBox="0 0 120 156" data-a="pop" data-d="0.1"><rect x="4" y="2" width="112" height="150" rx="7" fill="#efe3c9"/><rect x="4" y="2" width="16" height="150" rx="5" fill="#d8c9a6"/>
      <circle cx="68" cy="66" r="24" fill="none" stroke="#3a1c28" stroke-width="4"/><path d="M68,30 V102 M32,66 H104" stroke="#3a1c28" stroke-width="3.5"/></svg>
    <div class="au" data-a="fade" data-d="0.4">${d.author}</div>
    <div class="ti" data-a="up" data-d="0.6" data-t="0.6">THE 48 LAWS<br>OF POWER</div>
    ${d.law?`<div class="rule" data-a="growx" data-d="1.0" data-t="0.5"></div><div class="lw" data-a="fade" data-d="1.2">${d.law}</div><div class="ls" data-a="up" data-d="1.45" data-t="0.6">${d.sub}</div>`:''}
    </div></div>`,
  pair:d=>{
    const card=(c,dl,dir)=>`<div class="pc ${c.c}" data-a="${dir}" data-d="${dl}" data-t="0.55"><div class="pt">${c.t}</div>${c.sub?`<div class="ps">${c.sub}</div>`:''}</div>`;
    const neq='<svg width="62" height="62" viewBox="0 0 64 64"><g stroke="#fff" stroke-width="6" stroke-linecap="round"><path d="M12,24 H52 M12,42 H52 M41,8 L23,58"/></g></svg>';
    return `<div class="art pair">${card(d.a,0.2,'left')}<div class="mid" data-a="pop" data-d="0.9" data-t="0.4">${d.mid==='neq'?neq:d.mid}</div>${card(d.b,1.3,'right')}</div>`;
  },
  bars:d=>`<div class="art bars"><div class="bt" data-a="fade" data-d="0.1">${d.title}</div><div class="bw">${d.bars.map((b,i)=>`<div class="bc"><div class="bar ${b.c||''}" style="height:${Math.round(b.v*420)}px" data-a="growy" data-d="${0.5+i*0.9}" data-t="0.9"></div><div class="bl">${b.label}</div></div>`).join('')}</div></div>`,
  question:d=>`<div class="art col q"><div class="q1" data-a="fade" data-d="0.1">${d.small}</div><div class="q2" data-a="up" data-d="1.2" data-t="0.7">${md(d.big)}</div></div>`,
  outro:d=>`<div class="art col out"><div class="frame"></div><div class="o1" data-a="up" data-d="0.15" data-t="0.7">${md(d.line)}</div>
    ${d.cta?`<div class="rule" data-a="growx" data-d="0.5"></div><div class="o2" data-a="fade" data-d="0.8">এমন আরও গল্পের জন্য</div><div class="pill" data-a="pop" data-d="1.1" data-t="0.4">ফলো করুন <b>${CH}</b></div>`:''}</div>`,
};

/* ---------- timeline ---------- */
const BG={cream:'bg-cream',sage:'bg-sage',dark:'bg-dark',plum:'bg-plum',night:'bg-night'};
const SC=[];
function sceneHTML(s){
  const brand=`<div class="brand"><span class="l"></span>${CH}<span class="l"></span></div>`;
  const chip=s.chip?`<div class="chip" data-a="fade" data-d="0.1"><div>${s.chip}</div></div>`:'';
  const cap=s.cap?`<div class="cap ${s.plain?'plain':''}" data-a="up" data-d="${s.capAt!==undefined?s.capAt:0.3}" data-t="0.55">${md(s.cap)}</div>`:'';
  return brand+chip+V[s.v](s.d||{})+cap;
}
window.build=(scenes)=>{
  const root=document.getElementById('root'); root.innerHTML=''; SC.length=0;
  scenes.forEach((s,i)=>{
    const el=document.createElement('div');
    el.className='scene '+(BG[s.bg]||'bg-cream')+(['dark','plum','night'].includes(s.bg)?' on-dark':'');
    el.innerHTML=sceneHTML(s); root.appendChild(el);
    const anims=[];
    const add=(kf,opts)=>{const a=(opts.node||el).animate(kf,opts); a.pause(); anims.push(a);};
    el.querySelectorAll('[data-a]').forEach(n=>{
      const type=n.dataset.a;
      const o={node:n,duration:(+(n.dataset.t||0.55))*1000,delay:(+(n.dataset.d||0))*1000,fill:'both',easing:'cubic-bezier(.22,.8,.3,1)'};
      if(type==='bob'){o.duration=1700;o.delay=0;o.iterations=Infinity;o.direction='alternate';o.easing='ease-in-out';}
      add(ANIMS[type],o);
    });
    const art=el.querySelector('.art');
    if(art) add([{transform:'scale(1)'},{transform:'scale(1.035)'}],{node:art,duration:s.dur*1000,fill:'both',easing:'linear'});
    if(i>0) add([{opacity:0},{opacity:1}],{node:el,duration:XF*1000,fill:'both',easing:'linear'});
    SC.push({el,start:s.start,end:s.start+s.dur,anims});
  });
};
window.setTime=(t)=>{
  SC.forEach(sc=>{
    const vis=t>=sc.start&&t<sc.end+XF;
    sc.el.style.display=vis?'block':'none';
    if(vis){const ms=(t-sc.start)*1000; sc.anims.forEach(a=>{a.currentTime=ms;});}
  });
};
window.loadFonts=async()=>{
  await Promise.all(['400','500','600','700'].map(w=>document.fonts.load(w+' 40px "Hind Siliguri"','অআকখগ।')));
  await document.fonts.load('600 40px "Lora"','THE 48 LAWS');
  await document.fonts.ready; return true;
};
</script></body></html>
"""

# ----------------------------------------------------------------------------
# PIPELINE
# ----------------------------------------------------------------------------
def say(msg):
    print(msg, flush=True)


def ensure(mod, pip_name, required=True):
    """Import a module, pip-installing it first if missing."""
    try:
        return importlib.import_module(mod)
    except ImportError:
        pass
    say(f"[setup] installing {pip_name} ...")
    r = subprocess.run([sys.executable, "-m", "pip", "install", "-q", pip_name])
    if r.returncode == 0:
        importlib.invalidate_caches()
        try:
            return importlib.import_module(mod)
        except ImportError:
            pass
    if required:
        sys.exit(f"Could not install '{pip_name}'. Create a virtual env and retry:\n"
                 f"  python -m venv venv && (activate it) && pip install {pip_name}")
    return None


def get_ffmpeg():
    m = ensure("imageio_ffmpeg", "imageio-ffmpeg", required=False)
    if m:
        try:
            return m.get_ffmpeg_exe()
        except Exception:
            pass
    exe = shutil.which("ffmpeg")
    if not exe:
        sys.exit("ffmpeg not found. Run:  pip install imageio-ffmpeg   (or install ffmpeg)")
    return exe


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        sys.exit(f"Command failed: {' '.join(map(str, cmd[:3]))} ...\n{r.stderr[-800:]}")
    return r


def media_seconds(ffmpeg, path):
    r = subprocess.run([ffmpeg, "-i", str(path)], capture_output=True, text=True, encoding="utf-8", errors="replace")
    m = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", r.stderr)
    if not m:
        raise RuntimeError(f"cannot read duration of {path}")
    h, mi, s = m.groups()
    return int(h) * 3600 + int(mi) * 60 + float(s)


def plain_text(s):
    s = re.sub(r"\*\*", "", s or "")
    s = re.sub(r"[“”\"]", "", s)
    s = re.sub(r"\s*[—–]\s*", ", ", s)
    return re.sub(r"\s+", " ", s).strip(" ,")


def narration(scene):
    d = scene.get("d", {})
    raw = scene.get("say") or scene.get("cap") or " ".join(d.get("lines", [])) or d.get("line", "")
    return plain_text(raw)


def tts_to_file(text, path, voice, rate):
    """Bangla text -> mp3 with Microsoft Edge neural voices (free, needs internet)."""
    edge_tts = ensure("edge_tts", "edge-tts")
    asyncio.run(edge_tts.Communicate(text, voice, rate=rate).save(str(path)))


def synth_all(scenes, tmp, voice, rate, ffmpeg):
    try:
        for i, s in enumerate(scenes):
            text = narration(s)
            if not text:
                continue
            path = tmp / f"s{i:02d}.mp3"
            for attempt in range(3):
                try:
                    tts_to_file(text, path, voice, rate)
                    break
                except Exception:
                    if attempt == 2:
                        raise
            s["_audio"] = path
            s["_alen"] = media_seconds(ffmpeg, path)
            say(f"[voice] scene {i + 1}/{len(scenes)}  {s['_alen']:.1f}s")
        return True
    except Exception as e:
        say(f"[warn] voice-over failed ({type(e).__name__}: {e}). Making a silent video instead.")
        for s in scenes:
            s.pop("_audio", None)
            s.pop("_alen", None)
        return False


def plan_timing(scenes, voiced):
    t = 0.0
    for s in scenes:
        text = narration(s)
        if voiced and "_alen" in s:
            dur = s["_alen"] + LEAD + TAIL
        else:
            dur = 0.085 * len(text) + 1.5
        s["dur"] = round(max(MIN_DUR, dur), 3)
        s["start"] = round(t, 3)
        t += s["dur"]
    return t


def build_voice_track(scenes, tmp, ffmpeg):
    parts = []
    for i, s in enumerate(scenes):
        out = tmp / f"p{i:02d}.wav"
        dur = f"{s['dur']:.3f}"
        if "_audio" in s:
            af = f"adelay={int(LEAD * 1000)}:all=1,apad=whole_dur={dur}"
            run([ffmpeg, "-y", "-loglevel", "error", "-i", str(s["_audio"]), "-af", af,
                 "-t", dur, "-ar", "44100", "-ac", "2", str(out)])
        else:
            run([ffmpeg, "-y", "-loglevel", "error", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
                 "-t", dur, str(out)])
        parts.append(out)
    lst = tmp / "list.txt"
    lst.write_text("".join(f"file '{p.as_posix()}'\n" for p in parts), encoding="utf-8")
    voice = tmp / "voice.wav"
    run([ffmpeg, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(voice)])
    return voice


def launch_chromium(p):
    try:
        return p.chromium.launch()
    except Exception as e:
        if "install" not in str(e).lower() and "executable" not in str(e).lower():
            raise
        say("[setup] downloading Chromium (one time, ~150 MB) ...")
        subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium"])
        return p.chromium.launch()


def open_page(p, scenes, hd):
    browser = launch_chromium(p)
    page = browser.new_page(viewport={"width": W, "height": H}, device_scale_factor=1.5 if hd else 1)
    html = HTML.replace("__W__", str(W)).replace("__H__", str(H)).replace("__CHANNEL__", CHANNEL)
    try:
        page.set_content(html, wait_until="networkidle", timeout=25000)
    except Exception:
        say("[warn] web fonts may not have loaded (offline?). Falling back to system fonts.")
    page.evaluate("s => window.build(s)", scenes)
    try:
        page.evaluate("window.loadFonts()")
    except Exception:
        pass
    page.wait_for_timeout(300)
    return browser, page


def render_preview(scenes, hd):
    from playwright.sync_api import sync_playwright
    out = Path("preview")
    out.mkdir(exist_ok=True)
    with sync_playwright() as p:
        browser, page = open_page(p, scenes, hd)
        for i, s in enumerate(scenes):
            page.evaluate("t => window.setTime(t)", s["start"] + max(0.1, s["dur"] - 0.1))
            page.screenshot(path=str(out / f"scene_{i + 1:02d}.png"))
        browser.close()
    say(f"Preview images saved in ./{out}/ - check them, then run without --preview.")


def render_video(scenes, total, out_path, fps, hd, voice_wav, ffmpeg):
    from playwright.sync_api import sync_playwright
    n = max(1, round(total * fps))
    cmd = [ffmpeg, "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(fps), "-c:v", "mjpeg", "-i", "-"]
    if voice_wav:
        cmd += ["-i", str(voice_wav)]
    cmd += ["-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(fps)]
    if voice_wav:
        cmd += ["-c:a", "aac", "-b:a", "160k", "-shortest"]
    cmd += ["-movflags", "+faststart", str(out_path)]
    enc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    with sync_playwright() as p:
        browser, page = open_page(p, scenes, hd)
        for i in range(n):
            page.evaluate("t => window.setTime(t)", i / fps)
            enc.stdin.write(page.screenshot(type="jpeg", quality=92))
            if i % fps == 0:
                print(f"\r[render] {i / fps:5.1f}s / {total:.1f}s", end="", flush=True)
        browser.close()
    enc.stdin.close()
    enc.wait()
    print()
    if enc.returncode != 0:
        sys.exit("ffmpeg failed while encoding.")


def main(argv=None):
    ap = argparse.ArgumentParser(description="Bangla story-explainer video maker")
    ap.add_argument("--preview", action="store_true", help="only save one PNG per scene (fast)")
    ap.add_argument("--no-voice", action="store_true", help="silent video")
    ap.add_argument("--voice", default=VOICE)
    ap.add_argument("--rate", default=RATE)
    ap.add_argument("--fps", type=int, default=FPS)
    ap.add_argument("--hd", action="store_true", help="1080x1920 output (slower)")
    ap.add_argument("--out", default=OUT)
    args = ap.parse_args(argv)
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    ensure("playwright", "playwright")
    ffmpeg = get_ffmpeg()
    scenes = copy.deepcopy(SCENES)
    tmp = Path(tempfile.mkdtemp(prefix="bnvideo_"))

    voiced = not (args.no_voice or args.preview)
    if voiced:
        voiced = synth_all(scenes, tmp, args.voice, args.rate, ffmpeg)
    total = plan_timing(scenes, voiced)
    say(f"[plan] {len(scenes)} scenes, {total:.1f} s")

    if args.preview:
        render_preview(scenes, args.hd)
        return
    voice_wav = build_voice_track(scenes, tmp, ffmpeg) if voiced else None
    render_video(scenes, total, args.out, args.fps, args.hd, voice_wav, ffmpeg)
    say(f"Done -> {Path(args.out).resolve()}")


if __name__ == "__main__":
    main()

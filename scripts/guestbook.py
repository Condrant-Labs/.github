"""Adds a guestbook entry to profile/README.md from a GitHub issue.
Input comes from strangers, so everything is sanitised: no links, HTML or markdown.
"""
import datetime
import os
import pathlib
import re

README = pathlib.Path("profile/README.md")
START, END = "<!-- GUESTBOOK:START -->", "<!-- GUESTBOOK:END -->"
MAX_ROWS = 15

user = os.environ.get("GB_USER", "")
if not re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})", user):
    raise SystemExit("unexpected username")

body = os.environ.get("GB_BODY") or ""
lines = [l for l in body.splitlines() if l.strip() and not l.strip().lower().startswith("write your message")]
msg = " ".join(lines)
msg = re.sub(r"(https?://|www\.)\S+", "", msg, flags=re.I)      # no links
msg = re.sub(r"\S+\.(com|net|org|io|xyz|ru|in|co)\b\S*", "", msg, flags=re.I)
msg = re.sub(r"[<>\[\]()`|*_~#\\@{}&=]", "", msg)                # no html/markdown/mentions
msg = "".join(ch for ch in msg if ch.isprintable())
msg = re.sub(r"\s+", " ", msg).strip()[:100] or "said hi 👋"

text = README.read_text(encoding="utf-8")
s = text.index(START) + len(START)
e = text.index(END)
rows = [l for l in text[s:e].splitlines() if l.startswith("| [@")]
today = datetime.date.today().isoformat()
rows.insert(0, f"| [@{user}](https://github.com/{user}) | {msg} | {today} |")
rows = rows[:MAX_ROWS]
block = "\n\n| visitor | message | signed |\n|:--|:--|:--|\n" + "\n".join(rows) + "\n\n"
README.write_text(text[:s] + block + text[e:], encoding="utf-8")
print(f"signed: @{user}: {msg}")

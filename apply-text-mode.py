"""Apply the `jarvis text` + `jarvis text-float` features to a fresh upstream OpenJarvis checkout.

Run from the build repo root, after `git clone ... upstream`:
    python apply-text-mode.py

- Copies text_cmd.py and text_float_cmd.py into upstream/src/openjarvis/cli/
- Adds the import + cli.add_command registration to upstream
  src/openjarvis/cli/__init__.py, only if not already present.
  Uses anchor strings (not line numbers), so it survives upstream drift.
- Exits non-zero if an anchor is missing, so the build fails loudly
  instead of silently shipping an exe without the text commands.
"""
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
UPSTREAM = ROOT / "upstream"
SRC = UPSTREAM / "src" / "openjarvis" / "cli"
INIT = SRC / "__init__.py"
TEXT_CMD = SRC / "text_cmd.py"

IMPORT_ANCHOR = "    from openjarvis.cli.telemetry_cmd import telemetry\n"
IMPORT_LINES = [
    "    from openjarvis.cli.text_cmd import text\n",
    "    from openjarvis.cli.text_float_cmd import text_float\n",
]
ADD_ANCHOR = '    cli.add_command(chat, "chat")\n'
ADD_LINES = [
    '    cli.add_command(text, "text")\n',
    '    cli.add_command(text_float, "text-float")\n',
]


def main() -> int:
    if not INIT.is_file():
        print(f"ERROR: {INIT} not found — did the upstream clone fail?", file=sys.stderr)
        return 1
    shutil.copy2(ROOT / "text_cmd.py", TEXT_CMD)
    print(f"Copied text_cmd.py -> {TEXT_CMD}")
    shutil.copy2(ROOT / "text_float_cmd.py", SRC / "text_float_cmd.py")
    print(f"Copied text_float_cmd.py -> {SRC / 'text_float_cmd.py'}")

    text = INIT.read_text(encoding="utf-8")
    changed = False
    for line in IMPORT_LINES:
        if line.strip() not in text:
            if IMPORT_ANCHOR not in text:
                print("ERROR: import anchor not found in cli/__init__.py", file=sys.stderr)
                return 1
            text = text.replace(IMPORT_ANCHOR, IMPORT_ANCHOR + line, 1)
            changed = True
    for line in ADD_LINES:
        if line.strip() not in text:
            if ADD_ANCHOR not in text:
                print("ERROR: add_command anchor not found in cli/__init__.py", file=sys.stderr)
                return 1
            text = text.replace(ADD_ANCHOR, ADD_ANCHOR + line, 1)
            changed = True
    if changed:
        INIT.write_text(text, encoding="utf-8")
        print("Registered `jarvis text` and `jarvis text-float` in cli/__init__.py")
    else:
        print("`jarvis text` / `jarvis text-float` already registered, nothing to change")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

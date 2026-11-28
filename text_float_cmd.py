"""``jarvis text-float`` — floating text window, bottom-right, always on top.

No microphone. A small window stays in the right-bottom corner of the
screen the whole time. Type in the box at the bottom, press Enter or
Send, and Jarvis answers in the same window.

Usage:
    jarvis text-float
    jarvis text-float -m <model-id>

Tkinter is imported lazily, inside the command, so ``--help`` and the
rest of the CLI work on machines without a display. On Windows the
standard Tkinter library is included with Python.
"""

from __future__ import annotations

import threading

import click


def _window_geometry(root, *, width: int = 380, height: int = 520) -> str:
    """Bottom-right corner, 16 px from the right and bottom edges."""
    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()
    x = max(0, screen_w - width - 16)
    y = max(0, screen_h - height - 60)
    return f"{width}x{height}+{x}+{y}"


def _resolve_engine_and_model(config, engine_key, model_name, console):
    """Resolve engine + model the same way ``jarvis chat`` does."""
    from openjarvis.cli._model_switch import resolve_chat_cli_model
    from openjarvis.engine import get_engine
    from openjarvis.intelligence import register_builtin_models

    register_builtin_models()
    resolved = get_engine(config, engine_key)
    if resolved is None:
        return None, None, "No inference engine available."
    engine_name, engine = resolved
    model = resolve_chat_cli_model(
        console=console,
        config=config,
        engine=engine,
        engine_name=engine_name,
        cli_model=model_name,
        chat_variant="chat",
    )
    if not model:
        return None, None, "No model available."
    return engine, model, None


@click.command(name="text-float")
@click.option("-e", "--engine", "engine_key", default=None, help="Engine backend.")
@click.option(
    "-m",
    "--model",
    "model_name",
    default=None,
    help="Model id. Omit to use the configured default model.",
)
@click.option(
    "--pick-model",
    "pick_model",
    is_flag=True,
    default=False,
    help="Show the model list before opening the window.",
)
def text_float(engine_key, model_name, pick_model) -> None:
    """Floating text window — bottom-right, always on top, no mic."""
    try:
        import tkinter as tk
        from tkinter import scrolledtext
    except Exception as exc:  # pragma: no cover - display-dependent
        click.echo(f"Could not open a window (Tkinter unavailable): {exc}", err=True)
        raise SystemExit(1)

    from rich.console import Console

    from openjarvis.core.config import load_config
    from openjarvis.core.types import Message, Role

    console = Console(stderr=True)
    config = load_config()

    if pick_model:
        click.echo("Note: --pick-model is ignored in the floating window; using the configured default model.")
    engine, model, error = _resolve_engine_and_model(
        config, engine_key, model_name, console
    )
    if error:
        click.echo(f"Error: {error}", err=True)
        raise SystemExit(1)

    history: list[Message] = []
    if config.agent.default_system_prompt:
        history.append(Message(role=Role.SYSTEM, content=config.agent.default_system_prompt))

    root = tk.Tk()
    root.title("Jarvis — text")
    root.geometry(_window_geometry(root))
    root.attributes("-topmost", True)
    root.configure(bg="#111827")

    history_box = scrolledtext.ScrolledText(
        root, wrap=tk.WORD, state="disabled", bg="#111827", fg="#e5e7eb",
        font=("Segoe UI", 10), padx=10, pady=10,
    )
    history_box.pack(fill=tk.BOTH, expand=True)

    entry_frame = tk.Frame(root, bg="#111827")
    entry_frame.pack(fill=tk.X, padx=8, pady=8)
    entry = tk.Entry(entry_frame, font=("Segoe UI", 10), bg="#1f2937", fg="#ffffff", insertbackground="white")
    entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
    send_btn = tk.Button(entry_frame, text="Send", bg="#2563eb", fg="white", font=("Segoe UI", 10, "bold"))
    send_btn.pack(side=tk.RIGHT, padx=(6, 0))

    def _append(who: str, text: str) -> None:
        history_box.configure(state="normal")
        history_box.insert(tk.END, f"{who}: {text}\n\n")
        history_box.configure(state="disabled")
        history_box.see(tk.END)

    def _ask(user_text: str) -> None:
        history.append(Message(role=Role.USER, content=user_text))
        try:
            result = engine.generate(history, model=model)
            content = result.get("content", "") if isinstance(result, dict) else str(result)
        except Exception as exc:
            content = f"Error: {exc}"
        if content:
            history.append(Message(role=Role.ASSISTANT, content=content))
        root.after(0, lambda: (_append("Jarvis", content or "(no reply)"), send_btn.configure(state="normal"), entry.configure(state="normal")))

    def _send(_event=None) -> None:
        user_text = entry.get().strip()
        if not user_text:
            return
        if user_text.lower() in ("/quit", "/exit", "/q"):
            root.destroy()
            return
        entry.delete(0, tk.END)
        entry.configure(state="disabled")
        send_btn.configure(state="disabled")
        _append("You", user_text)
        _append("Jarvis", "…")
        threading.Thread(target=_ask, args=(user_text,), daemon=True).start()

    send_btn.configure(command=_send)
    entry.bind("<Return>", _send)
    _append("Jarvis", "Hi — type below, no mic needed. I stay in the bottom-right corner.")
    entry.focus_set()
    root.mainloop()


__all__ = ["text_float", "_window_geometry"]

"""``jarvis text`` — text-only chat, no microphone needed.

Faizan has no mic, so this is a first-class text mode: type your
message, press Enter, read the reply. It is the same interactive
multi-turn chat as ``jarvis chat``, with voice I/O forced OFF —
no mic input, no silence detection, no text-to-speech.

Usage:
    jarvis text
    jarvis text -m <model-id>
    jarvis text --model deepseek-v4-flash

Type /quit or /exit to end the session, /help inside chat for commands.
"""

from __future__ import annotations

import click

from openjarvis.cli._runtime_panel import runtime_cli_options
from openjarvis.cli.chat_cmd import chat as chat_cmd


@click.command(name="text")
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
    help="Show the model list before chat.",
)
@click.option("-a", "--agent", "agent_name", default=None, help="Agent type.")
@click.option("--tools", default=None, help="Comma-separated tool names.")
@click.option("--system", "system_prompt", default=None, help="Custom system prompt.")
@click.option(
    "--persona",
    "persona_name",
    default=None,
    help="Named persona dir under ~/.openjarvis/personas/<name>/ (pass 'none' to disable).",
)
@runtime_cli_options
@click.pass_context
def text(
    ctx: click.Context,
    engine_key,
    model_name,
    pick_model,
    agent_name,
    tools,
    system_prompt,
    persona_name,
    num_ctx,
    num_gpu,
    skip_runtime_panel,
) -> None:
    """Text-only chat — type your message, no microphone needed.

    Same chat as ``jarvis chat``, with voice forced OFF.
    """
    click.echo("TEXT MODE — No microphone needed. Type your message and press Enter.")
    click.echo("Type /quit to exit.")
    ctx.invoke(
        chat_cmd,
        engine_key=engine_key,
        model_name=model_name,
        pick_model=pick_model,
        agent_name=agent_name,
        tools=tools,
        system_prompt=system_prompt,
        persona_name=persona_name,
        voice_mode=False,
        num_ctx=num_ctx,
        num_gpu=num_gpu,
        skip_runtime_panel=skip_runtime_panel,
    )


__all__ = ["text"]

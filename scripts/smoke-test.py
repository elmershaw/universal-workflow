"""Install the plugin in clean Codex and Claude Code profiles."""

import argparse
import json
import os
from pathlib import Path
import re
import subprocess
from tempfile import TemporaryDirectory
from threading import Timer
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parents[1]
PLUGIN_ID = "universal-workflow@universal-workflow"
SKILLS = {"research", "grill-with-docs", "implement", "review", "retro"}


def run(args, cwd, env=None):
    result = subprocess.run(
        args, cwd=cwd, env=env, capture_output=True, text=True, timeout=150
    )
    if result.returncode:
        raise RuntimeError(f"{args} exited {result.returncode}\n{result.stdout}{result.stderr}")
    return result.stdout


def codex_skills(cwd, env):
    with subprocess.Popen(
        ["codex", "app-server"],
        cwd=cwd,
        env=env,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True,
    ) as server:
        timer = Timer(30, server.kill)
        timer.start()

        def send(message):
            server.stdin.write(json.dumps(message) + "\n")
            server.stdin.flush()

        def request(request_id, method, params):
            send({"id": request_id, "method": method, "params": params})
            for line in server.stdout:
                reply = json.loads(line)
                if reply.get("id") == request_id:
                    if "error" in reply:
                        raise RuntimeError(f"Codex {method} failed: {reply['error']}")
                    return reply["result"]
            raise RuntimeError(f"Codex app-server ended before replying to {method}")

        try:
            request(1, "initialize", {"clientInfo": {"name": "workflow-smoke-test", "version": "1"}})
            send({"method": "initialized"})
            result = request(2, "skills/list", {"cwds": [str(cwd)], "forceReload": True})
            return {
                skill["name"]
                for workspace in result["data"]
                for skill in workspace["skills"]
                if skill.get("pluginId") == PLUGIN_ID and skill["enabled"]
            }
        finally:
            timer.cancel()
            server.kill()


def require_skills(client, discovered, expected):
    if discovered != expected:
        raise RuntimeError(
            f"{client} skill mismatch. Expected {sorted(expected)}, found {sorted(discovered)}."
        )
    print(f"{client} installed the plugin and discovered all five skills.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--marketplace", help="Install from this marketplace instead of archiving HEAD.")
    options = parser.parse_args()

    with TemporaryDirectory(prefix="universal-workflow-smoke-") as directory:
        temporary = Path(directory).resolve()
        checkout = temporary / "checkout"
        checkout.mkdir()
        source = options.marketplace
        if source is None:
            archive = temporary / "package.zip"
            run(["git", "archive", "--format=zip", f"--output={archive}", "HEAD"], ROOT)
            with ZipFile(archive) as package:
                package.extractall(checkout)
            source = str(checkout)

        env = {**os.environ, "GIT_TERMINAL_PROMPT": "0"}
        codex_profile = temporary / "codex"
        codex_profile.mkdir()
        codex_env = {**env, "CODEX_HOME": str(codex_profile)}
        run(["codex", "plugin", "marketplace", "add", source], checkout, codex_env)
        run(["codex", "plugin", "add", PLUGIN_ID], checkout, codex_env)
        require_skills(
            "Codex",
            codex_skills(checkout, codex_env),
            {f"universal-workflow:{name}" for name in SKILLS},
        )

        claude_profile = temporary / "claude"
        claude_profile.mkdir()
        claude_env = {**env, "CLAUDE_CONFIG_DIR": str(claude_profile)}
        run(["claude", "plugin", "marketplace", "add", source], checkout, claude_env)
        run(["claude", "plugin", "install", PLUGIN_ID], checkout, claude_env)
        details = run(["claude", "plugin", "details", PLUGIN_ID], checkout, claude_env)
        inventory = re.search(r"^  Skills \(\d+\)[ \t]+(.+)$", details, re.MULTILINE)
        if inventory is None:
            raise RuntimeError(f"Claude Code did not report a skill inventory.\n{details}")
        require_skills("Claude Code", set(inventory[1].split(", ")), SKILLS)


if __name__ == "__main__":
    main()

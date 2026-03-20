import argparse
import os
import shutil
import subprocess
import sys

REQUIRED_SECRETS = [
    "DATABASE_URL",
    "DATABASE_URL_DIRECT",
    "REDIS_URL",
    "GROQ_API_KEY",
    "OPENAI_API_KEY",
    "SUPABASE_SERVICE_ROLE_KEY",
    "API_KEY",
]


def _run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, capture_output=True, text=True, check=False)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate required GitHub Actions secrets.")
    parser.add_argument("--repo", default=os.getenv("GITHUB_REPOSITORY", ""))
    args = parser.parse_args()

    if shutil.which("gh") is None:
        print("ERROR: GitHub CLI (gh) is not installed.")
        return 2

    cmd = ["gh", "secret", "list"]
    if args.repo:
        cmd.extend(["--repo", args.repo])

    result = _run(cmd)
    if result.returncode != 0:
        print("ERROR: Unable to list GitHub secrets.")
        print(result.stderr.strip() or result.stdout.strip())
        return result.returncode

    existing = set()
    for line in result.stdout.splitlines():
        parts = line.split("\t", 1)
        if parts and parts[0].strip():
            existing.add(parts[0].strip())

    missing = [name for name in REQUIRED_SECRETS if name not in existing]
    if missing:
        print("Missing required secrets:")
        for name in missing:
            print(f"- {name}")
        return 1

    print("All required secrets are present.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

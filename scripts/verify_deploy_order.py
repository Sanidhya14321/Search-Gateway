from pathlib import Path


REQUIRED_PATHS = [
    "alembic/versions/006_add_hnsw_index.py",
    "alembic/versions/007_enable_rls.py",
    "scripts/rembed_chunks.py",
    "scripts/check_github_secrets.py",
    "scripts/check_costs.py",
    ".github/workflows/weekly_cleanup.yml",
]


def main() -> int:
    project_root = Path(__file__).resolve().parents[1]
    missing = []
    for relative in REQUIRED_PATHS:
        if not (project_root / relative).exists():
            missing.append(relative)

    if missing:
        print("Deploy-order prerequisites missing:")
        for item in missing:
            print(f"- {item}")
        return 1

    print("Deploy order checklist:")
    print("1. Apply Alembic migrations to head")
    print("2. Re-embed chunks when embedding model changes")
    print("3. Validate GitHub secrets")
    print("4. Deploy backend service")
    print("5. Deploy frontend service")
    print("6. Run post-deploy cost check")
    print("VERIFY: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

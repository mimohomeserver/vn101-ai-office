from __future__ import annotations

import getpass
import json
import os
from pathlib import Path


PROJECT_ID = "vn101-ai-office"
OWNER_FIREBASE_UID = "Oa8i2qQMMFbeKcKFiG1rFdxbuv92"
DATABASE_NAME = "vn101_ai_office"


def dotenv_value(value: str) -> str:
    """Encode a value as a double-quoted python-dotenv value."""
    return json.dumps(value, ensure_ascii=False)


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    print("VN101 AI Office - local secret setup")
    print("Secrets are entered/read locally and are never printed by this script.\n")

    default_path = root / "service-account.json"
    raw_path = input(f"Firebase Service Account JSON path [{default_path}]: ").strip()
    json_path = Path(raw_path).expanduser() if raw_path else default_path
    if not json_path.is_absolute():
        json_path = (Path.cwd() / json_path).resolve()
    if not json_path.is_file():
        raise SystemExit(f"File not found: {json_path}")

    try:
        service_account = json.loads(json_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"Could not read valid JSON: {exc}") from None

    if service_account.get("type") != "service_account":
        raise SystemExit("The JSON file is not a Firebase service-account key.")
    if service_account.get("project_id") != PROJECT_ID:
        raise SystemExit(
            "Firebase project_id does not match the configured project "
            f"({PROJECT_ID}). Check that you downloaded the key from the correct project."
        )

    mongo_uri = getpass.getpass("Paste MongoDB Atlas URI (input hidden): ").strip()
    if not mongo_uri.startswith("mongodb"):
        raise SystemExit("MongoDB URI must start with mongodb:// or mongodb+srv://.")
    if "<password>" in mongo_uri or "YOUR_PASSWORD" in mongo_uri:
        raise SystemExit("Replace the password placeholder with your real Atlas password.")
    if not mongo_uri:
        raise SystemExit("MongoDB URI is required.")

    env_path = root / "backend" / ".env"
    if env_path.exists():
        confirm = input(".env already exists. Replace it? Type YES to continue: ").strip()
        if confirm != "YES":
            raise SystemExit("Cancelled. Existing .env was not changed.")

    lines = [
        "APP_NAME=" + dotenv_value("VN101 AI Office"),
        "APP_ENV=" + dotenv_value("development"),
        "API_PREFIX=" + dotenv_value("/api/v1"),
        "MONGODB_URI=" + dotenv_value(mongo_uri),
        "MONGODB_DATABASE=" + dotenv_value(DATABASE_NAME),
        "MONGODB_SERVER_SELECTION_TIMEOUT_MS=3000",
        "FIREBASE_PROJECT_ID=" + dotenv_value(PROJECT_ID),
        "FIREBASE_SERVICE_ACCOUNT_JSON=" + dotenv_value(
            json.dumps(service_account, separators=(",", ":"), ensure_ascii=False)
        ),
        "OWNER_FIREBASE_UID=" + dotenv_value(OWNER_FIREBASE_UID),
        "",
    ]
    env_path.write_text("\n".join(lines), encoding="utf-8")
    try:
        os.chmod(env_path, 0o600)
    except OSError:
        pass

    print(f"\nCreated local environment file: {env_path}")
    print("The secrets were not displayed. Keep .env and the service-account JSON out of Git.")
    print("Next: run the backend tests, then start the API locally.")


if __name__ == "__main__":
    main()

"""Constants for Gitea Config Sync."""

DOMAIN = "gitea_sync"
PLATFORMS = []

# Config entry keys
CONF_URL = "url"
CONF_TOKEN = "token"
CONF_OWNER = "owner"
CONF_REPO = "repo"
CONF_BRANCH = "branch"
CONF_INCLUDE_PATHS = "include_paths"
CONF_EXCLUDE_PATHS = "exclude_paths"
CONF_AUTO_SYNC_INTERVAL = "auto_sync_interval"
CONF_SYNC_ON_START = "sync_on_start"
CONF_WATCH_FILES = "watch_files"
CONF_COMMIT_MESSAGE_PREFIX = "commit_message_prefix"

# Defaults
DEFAULT_BRANCH = "main"
DEFAULT_INCLUDE_PATHS = "*.yaml,*.json"
DEFAULT_EXCLUDE_PATHS = "secrets.yaml,.storage/,*.log,home-assistant_v2.db"
DEFAULT_AUTO_SYNC_INTERVAL = 0
DEFAULT_SYNC_ON_START = True
DEFAULT_WATCH_FILES = True
DEFAULT_COMMIT_MESSAGE_PREFIX = "HA Auto-Sync"

# Services
SERVICE_SYNC_NOW = "sync_now"
SERVICE_SYNC_FILE = "sync_file"

# Events
EVENT_SYNC_STARTED = f"{DOMAIN}_sync_started"
EVENT_SYNC_COMPLETED = f"{DOMAIN}_sync_completed"
EVENT_SYNC_FAILED = f"{DOMAIN}_sync_failed"

# Sensor attributes
ATTR_LAST_SYNC = "last_sync"
ATTR_LAST_COMMIT = "last_commit"
ATTR_FILES_SYNCED = "files_synced"
ATTR_SYNC_STATUS = "sync_status"

SYNC_STATUS_IDLE = "idle"
SYNC_STATUS_RUNNING = "running"
SYNC_STATUS_SUCCESS = "success"
SYNC_STATUS_FAILED = "failed"

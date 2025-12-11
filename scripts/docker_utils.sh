#!/bin/bash

# Function to detect the host path of the current workspace
detect_host_path() {
    # If HOST_PROJECT_ROOT is already set and not ".", use it
    if [ -n "$HOST_PROJECT_ROOT" ] && [ "$HOST_PROJECT_ROOT" != "." ]; then
        echo "Using existing HOST_PROJECT_ROOT: $HOST_PROJECT_ROOT" >&2
        return
    fi

    # Check if we are inside a Docker container
    if [ -f /.dockerenv ] || grep -q "docker" /proc/1/cgroup 2>/dev/null; then
        echo "Detected Docker environment. Attempting to find host path..." >&2
        
        # Get the container ID (hostname)
        CONTAINER_ID=$(hostname)
        
        # Inspect self to find the bind mount for /workspace
        # We look for a mount where Destination is /workspace
        HOST_PATH=$(docker inspect "$CONTAINER_ID" --format '{{range .Mounts}}{{if eq .Destination "/workspace"}}{{.Source}}{{end}}{{end}}')
        
        if [ -n "$HOST_PATH" ]; then
            echo "Found host path: $HOST_PATH" >&2
            export HOST_PROJECT_ROOT="$HOST_PATH"
        else
            echo "WARNING: Could not detect host path for /workspace. Defaulting to current directory." >&2
            export HOST_PROJECT_ROOT="."
        fi
    else
        # Not in Docker (or detection failed), assume local execution
        echo "Running locally. Using current directory." >&2
        export HOST_PROJECT_ROOT="."
    fi
}

# Run detection
detect_host_path

# Generate pgadmin servers.json from template if it exists
if [ -f "infrastructure/pgadmin/servers.json.template" ]; then
    echo "Generating infrastructure/pgadmin/servers.json..." >&2
    # Load .env variables
    set -a
    [ -f .env ] && . .env
    set +a
    
    # Use python to expand variables (handles special characters better than sed)
    python3 -c 'import os; print(os.path.expandvars(open("infrastructure/pgadmin/servers.json.template").read()))' > infrastructure/pgadmin/servers.json
fi

# Execute the passed command
exec "$@"

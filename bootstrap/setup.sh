    #!/usr/bin/env bash
    # bootstrap/setup.sh
    #
    # This script bootstraps a local‑only ML governance environment on
    # macOS or Linux.  It installs Python 3.11, Git, Docker and other
    # dependencies using Homebrew on macOS or apt on Debian/Ubuntu.  The
    # script is idempotent: installed packages are upgraded when
    # necessary and left untouched otherwise.  Homebrew’s behaviour to
    # upgrade a formula if it exists and is outdated is noted in its
    # manual, while `apt-get upgrade` installs the
    # newest versions of installed packages without removing anything.
    
    set -euo pipefail
    
    OS="$(uname -s)"
    
    install_macos() {
        if ! command -v brew >/dev/null 2>&1; then
            echo "Installing Homebrew…"
            /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        fi
        echo "Updating Homebrew…"
        brew update
    
        # Packages required.  Homebrew will upgrade a formula if it is
        # already installed and out of date.
        local pkgs=(git python@3.11 docker pip-tools)
        for pkg in "${pkgs[@]}"; do
            if brew ls --versions "$pkg" >/dev/null; then
                echo "$pkg already installed; upgrading if necessary."
                brew upgrade "$pkg" || true
            else
                echo "Installing $pkg…"
                brew install "$pkg"
            fi
        done
        # Start Docker Desktop once installed.
        if ! pgrep -f Docker.app >/dev/null 2>&1; then
            open -a Docker
            echo "Starting Docker Desktop…"
        fi
    }
    
    install_debian() {
        echo "Updating apt…"
        sudo apt-get update
        # Install python3.11 and related packages.  The apt manual notes
        # that `apt-get upgrade` installs new versions while leaving
        # installed packages untouched.
        sudo apt-get install -y python3.11 python3.11-venv python3-pip git docker.io
        # Install pip-tools for deterministic lock generation.
        python3.11 -m pip install --user pip-tools
        # Enable and start the Docker service
        sudo systemctl enable --now docker.service
    }
    
    check_python_version() {
        local required_major=3
        local required_minor=11
        local pyver
        pyver=$(python3 --version 2>&1 || true)
        if [[ $pyver =~ Python[[:space:]]([0-9]+)\.([0-9]+)\.([0-9]+) ]]; then
            local major=${BASH_REMATCH[1]}
            local minor=${BASH_REMATCH[2]}
            if (( major > required_major || (major == required_major && minor >= required_minor) )); then
                echo "Detected Python $major.$minor."
            else
                echo "Python 3.11 or newer is required; detected $major.$minor" >&2
                exit 1
            fi
        else
            echo "Unable to determine Python version." >&2
            exit 1
        fi
    }
    
    check_docker_version() {
        # Validate that Docker Desktop version is >= 4.41 to mitigate
        # CVE‑2025‑3224.  On Linux this check is
        # advisory because docker.io packages may use a different versioning
        # scheme.
        if command -v docker >/dev/null 2>&1; then
            local ver
            ver=$(docker version --format '{{.Client.Version}}' || true)
            if [[ $ver =~ ([0-9]+)\.([0-9]+) ]]; then
                local major=${BASH_REMATCH[1]}
                local minor=${BASH_REMATCH[2]}
                if (( major > 4 || (major == 4 && minor >= 41) )); then
                    echo "Docker version $ver detected."
                else
                    echo "Docker version $ver is out of date; please upgrade to >= 4.41." >&2
                fi
            fi
        else
            echo "Docker is not installed or not found in PATH." >&2
        fi
    }
    
    main() {
        case "$OS" in
            Darwin)
                install_macos
                ;;
            Linux)
                install_debian
                ;;
            *)
                echo "Unsupported operating system: $OS" >&2
                exit 1
                ;;
        esac
        check_python_version
        check_docker_version
        echo "Bootstrap completed successfully."
    }
    
    main "$@"
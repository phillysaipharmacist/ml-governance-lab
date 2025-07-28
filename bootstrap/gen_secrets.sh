    #!/usr/bin/env bash
    # bootstrap/gen_secrets.sh
    #
    # Generate random secrets for Grafana and PostgreSQL.  Secrets are
    # written to the config directory and will be consumed by
    # docker-compose via the secrets mechanism.  If the files already
    # exist, the script leaves them untouched.  The secrets pattern
    # follows the Grafana documentation which allows the admin password
    # to be read from a file using GF_SECURITY_ADMIN_PASSWORD_FILE:contentReference[oaicite:11]{index=11}.
    
    set -euo pipefail
    
    mkdir -p "$(dirname "$0")/../config"
    
    GRAFANA_SECRET_FILE="$(dirname "$0")/../config/grafana_admin_password.txt"
    POSTGRES_SECRET_FILE="$(dirname "$0")/../config/postgres_password.txt"
    
    generate_secret() {
        local file=$1
        if [[ ! -f $file ]]; then
            # Use openssl to generate 32 hexadecimal characters.  Longer
            # secrets improve entropy for authentication.
            openssl rand -hex 16 > "$file"
            chmod 600 "$file"
            echo "Created secret $file"
        else
            echo "Secret $file already exists; leaving unchanged."
        fi
    }
    
    generate_secret "$GRAFANA_SECRET_FILE"
    generate_secret "$POSTGRES_SECRET_FILE"
    
    echo "Secrets generated."
#!/usr/bin/env bash
# nomos-template bootstrap — run once after cloning
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "==> Installing Nomos..."
pip install nomos

echo ""
echo "==> Next steps:"
echo ""
echo "  1. Edit governance.yml with your platform's conventions"
echo "  2. Replace constitution.md with your platform principles"
echo "  3. Add ADRs in adrs/global/"
echo "  4. Add Gherkin checks in features/<your-domain>/"
echo ""
echo "  Start the server:"
echo "    nomos --repo $REPO_DIR"
echo ""
echo "  Validate a name:"
echo "    nomos-validate --server http://localhost:8080 topic your.topic.name"
echo ""
echo "  Connect Claude Code — add to your project's .mcp.json:"
echo '    {"mcpServers":{"nomos":{"type":"http","url":"http://localhost:8080/mcp"}}}'
echo ""
echo "  See examples/ for complete domain implementations (Kafka, REST API)."

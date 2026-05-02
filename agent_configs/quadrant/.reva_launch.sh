source /home/mila/e/elarabim/code/x-reviewer-agent/agent_configs/quadrant/.reva_env.sh
rm -f /home/mila/e/elarabim/code/x-reviewer-agent/agent_configs/quadrant/.reva_env.sh
#!/usr/bin/env bash
set -o pipefail
_timeout() {
    # Usage: _timeout SECONDS COMMAND [ARGS...]
    local secs=$1; shift
    "$@" &
    local pid=$!
    (
        sleep "$secs"
        kill -TERM "$pid" 2>/dev/null
        sleep 10
        kill -KILL "$pid" 2>/dev/null
    ) &
    local watcher=$!
    wait "$pid"
    local rc=$?
    kill "$watcher" 2>/dev/null
    wait "$watcher" 2>/dev/null
    return $rc
}

_load_agent_env() {
    if [ -f .env ]; then
        set -a
        . ./.env
        set +a
    fi
    if [ -f .api_key ]; then
        COALESCENCE_API_KEY=$(tr -d '\r\n' < .api_key)
        export COALESCENCE_API_KEY
    fi
    # Agents run from agent_configs/<name>/, so ../../bin is the repo's bin/
    # dir. Prepend it so tools shipped in the repo (e.g. a static jq binary)
    # are reachable from the agent's shell on compute nodes that lack them.
    if [ -d ../../bin ]; then
        PATH="$(cd ../../bin && pwd):$PATH"
        export PATH
    fi
}

SESSION_TIMEOUT=600

while true; do
    _load_agent_env
    OFFSET=$(wc -c < agent.log 2>/dev/null || echo 0)
    if [ -f last_session_id ] && [ -s last_session_id ]; then
        SESSION_ID=$(cat last_session_id)
        _timeout "${SESSION_TIMEOUT}" claude --resume "$SESSION_ID" -p "$(cat initial_prompt.txt)" --dangerously-skip-permissions --output-format stream-json --verbose --mcp-config '{"mcpServers":{"paperlantern":{"type":"http","url":"https://mcp.paperlantern.ai/chat/mcp?key=pl_cd1099cd5b35f6c193f9"},"koala":{"type":"http","url":"https://koala.science/mcp","headers":{"Authorization":"Bearer '"$COALESCENCE_API_KEY"'"}}}}' 2>&1 | tee -a agent.log
        RESUME_RC=$?
        if [ $RESUME_RC -ne 0 ]; then
            echo "[reva] resume failed (rc=$RESUME_RC), starting fresh session..."
            rm -f last_session_id
            _timeout "${SESSION_TIMEOUT}" claude -p "$(cat initial_prompt.txt)" --dangerously-skip-permissions --output-format stream-json --verbose --mcp-config '{"mcpServers":{"paperlantern":{"type":"http","url":"https://mcp.paperlantern.ai/chat/mcp?key=pl_cd1099cd5b35f6c193f9"},"koala":{"type":"http","url":"https://koala.science/mcp","headers":{"Authorization":"Bearer '"$COALESCENCE_API_KEY"'"}}}}' 2>&1 | tee -a agent.log
        fi
    else
        _timeout "${SESSION_TIMEOUT}" claude -p "$(cat initial_prompt.txt)" --dangerously-skip-permissions --output-format stream-json --verbose --mcp-config '{"mcpServers":{"paperlantern":{"type":"http","url":"https://mcp.paperlantern.ai/chat/mcp?key=pl_cd1099cd5b35f6c193f9"},"koala":{"type":"http","url":"https://koala.science/mcp","headers":{"Authorization":"Bearer '"$COALESCENCE_API_KEY"'"}}}}' 2>&1 | tee -a agent.log
    fi
    tail -c "+$((OFFSET+1))" agent.log | python3 -c "
import sys, json
for line in sys.stdin:
    try:
        d = json.loads(line)
        if d.get('type') == 'system' and d.get('subtype') == 'init' and 'session_id' in d:
            print(d['session_id'])
            break
    except Exception:
        pass
" > last_session_id 2>/dev/null
    EXIT_CODE=$?
    echo "[reva] agent exited ($EXIT_CODE), restarting in 5s..."
    sleep 5
done

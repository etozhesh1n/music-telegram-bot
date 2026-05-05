@echo off
setlocal
set "ANTHROPIC_AUTH_TOKEN=sk-e5996adb51e16e20-aa68fa-029349af"
set "ANTHROPIC_BASE_URL=http://localhost:20128/v1"
set "CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS=1"

set "ANTHROPIC_MODEL=kr/claude-sonnet-4.5"

echo Starting Claude Code via Omniroute
claude

endlocal

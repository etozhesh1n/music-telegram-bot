@echo off
setlocal

echo Starting Omniroute server...
start "Omniroute Server" omniroute

echo Waiting for Omniroute to initialize...
timeout /t 3 /nobreak >nul

set "ANTHROPIC_AUTH_TOKEN=sk-e5996adb51e16e20-aa68fa-029349af"
set "ANTHROPIC_BASE_URL=http://localhost:20128/v1"
set "CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS=1"

echo Starting Claude Code via Omniroute
claude --model=kr/claude-opus-4.7

endlocal

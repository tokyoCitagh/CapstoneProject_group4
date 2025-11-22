#!/bin/bash
# Script to push to GitHub after fixing credentials

echo "=========================================="
echo "GitHub Push Helper"
echo "=========================================="
echo ""
echo "Current status:"
git status --short
echo ""
echo "Attempting to push..."
echo ""

# Try to push
git push

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Push failed. This is likely due to GitHub credentials."
    echo ""
    echo "To fix this issue, you have 3 options:"
    echo ""
    echo "Option 1: Use GitHub Desktop (Easiest)"
    echo "  1. Open GitHub Desktop app"
    echo "  2. Sign in with tokyoCitagh account"
    echo "  3. Push from there"
    echo ""
    echo "Option 2: Use Personal Access Token"
    echo "  1. Go to: https://github.com/settings/tokens"
    echo "  2. Generate new token (classic)"
    echo "  3. Give it 'repo' permissions"
    echo "  4. Run: git push"
    echo "  5. When prompted for password, paste the token"
    echo ""
    echo "Option 3: Set up SSH Key"
    echo "  1. Run: ssh-keygen -t ed25519 -C 'your_email@example.com'"
    echo "  2. Run: cat ~/.ssh/id_ed25519.pub"
    echo "  3. Copy the output"
    echo "  4. Go to: https://github.com/settings/ssh/new"
    echo "  5. Add the key"
    echo "  6. Run: git remote set-url origin git@github.com:tokyoCitagh/CapstoneProject_group4.git"
    echo "  7. Run: git push"
    echo ""
else
    echo ""
    echo "✅ Push successful!"
    echo ""
    echo "Your changes are now deploying to Railway!"
    echo "Check deployment at: https://railway.app"
    echo ""
fi

#!/usr/bin/env bash

set -Eeuo pipefail

REPO_DIR="${HOME}/.user_config"
STOW_DIR="${REPO_DIR}"
TARGET_DIR="${HOME}"
PACKAGE="home"

REMOTE_NAME="origin"
REMOTE_URL="git@github.com:RedneckTech/My_DotFiles.git"

error() {
    printf 'Error: %s\n' "$*" >&2
    exit 1
}

for command_name in stow git; do
    command -v "$command_name" >/dev/null 2>&1 ||
        error "'${command_name}' is not installed."
done

[[ -d "${REPO_DIR}" ]] ||
    error "Dotfiles directory not found: ${REPO_DIR}"

[[ -d "${REPO_DIR}/.git" ]] ||
    error "${REPO_DIR} is not a Git repository."

echo "Previewing Stow changes..."
echo

stow -nRv \
    -d "$STOW_DIR" \
    -t "$TARGET_DIR" \
    "$PACKAGE"

echo
read -r -p "Apply these Stow changes? [y/N] " approval

case "$approval" in
    y|Y|yes|YES|Yes)
        ;;
    *)
        echo "Cancelled. No changes were applied."
        exit 0
        ;;
esac

echo
echo "Applying Stow changes..."

stow -Rv \
    -d "$STOW_DIR" \
    -t "$TARGET_DIR" \
    "$PACKAGE"

cd "$REPO_DIR"

echo
echo "Configuring Git remote..."

if git remote get-url "$REMOTE_NAME" >/dev/null 2>&1; then
    current_remote="$(git remote get-url "$REMOTE_NAME")"

    if [[ "$current_remote" != "$REMOTE_URL" ]]; then
        echo "Changing ${REMOTE_NAME} remote to:"
        echo "  ${REMOTE_URL}"
        git remote set-url "$REMOTE_NAME" "$REMOTE_URL"
    fi
else
    git remote add "$REMOTE_NAME" "$REMOTE_URL"
fi

branch="$(git branch --show-current)"

[[ -n "$branch" ]] ||
    error "The Git repository is in detached HEAD state."

echo
echo "Current Git changes:"
git status --short

git add --all

if git diff --cached --quiet; then
    echo
    echo "No local changes need to be committed."
else
    default_message="Update dotfiles $(date '+%Y-%m-%d %H:%M:%S')"

    echo
    read -r -p "Commit message [${default_message}]: " commit_message
    commit_message="${commit_message:-$default_message}"

    git commit -m "$commit_message"
fi

echo
echo "Fetching remote changes..."

git fetch "$REMOTE_NAME"

if git show-ref \
    --verify \
    --quiet \
    "refs/remotes/${REMOTE_NAME}/${branch}"; then
    echo "Updating local ${branch} branch..."
    git pull --rebase "$REMOTE_NAME" "$branch"
else
    echo "Remote branch ${branch} does not exist yet."
fi

echo
echo "Pushing ${branch} to GitHub over SSH..."

git push --set-upstream "$REMOTE_NAME" "$branch"

echo
echo "Dotfiles updated and pushed successfully."

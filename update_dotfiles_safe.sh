#!/usr/bin/env bash

set -Eeuo pipefail

REPO_DIR="${HOME}/.user_config"
STOW_DIR="${REPO_DIR}"
TARGET_DIR="${HOME}"
PACKAGE="home"

REMOTE_NAME="origin"
REMOTE_URL="git@github.com:RedneckTech/My_DotFiles.git"

# Backups made before --adopt are stored outside the Git repository.
STATE_DIR="${XDG_STATE_HOME:-${HOME}/.local/state}/dotfiles-stow"

error() {
    printf 'Error: %s\n' "$*" >&2
    exit 1
}

confirm() {
    local prompt="$1"
    local reply

    read -r -p "${prompt} [y/N] " reply || return 1
    [[ "$reply" =~ ^([yY]|[yY][eE][sS])$ ]]
}

run_stow_capture() {
    # Store the result in STOW_OUTPUT and STOW_STATUS without letting
    # `set -e` terminate the script before we can inspect conflicts.
    set +e
    STOW_OUTPUT="$(stow "$@" 2>&1)"
    STOW_STATUS=$?
    set -e
}

backup_item() {
    local source_path="$1"
    local backup_root="$2"
    local relative_path="$3"
    local destination_path="${backup_root}/${relative_path}"

    if [[ -e "$source_path" || -L "$source_path" ]]; then
        mkdir -p "$(dirname "$destination_path")"
        cp -a -- "$source_path" "$destination_path"
    fi
}

handle_stow_conflicts() {
    local -a conflicts=()
    local relative_path
    local backup_dir
    local target_path
    local package_path

    mapfile -t conflicts < <(
        printf '%s\n' "$STOW_OUTPUT" |
            sed -nE \
                's/^[[:space:]]*\*[[:space:]]+existing target is neither a link nor a directory:[[:space:]]+//p' |
            sort -u
    )

    if (( ${#conflicts[@]} == 0 )); then
        printf '%s\n' "$STOW_OUTPUT" >&2
        error "Stow failed with a conflict type this script cannot safely adopt automatically."
    fi

    echo
    echo "Stow found ${#conflicts[@]} existing regular file(s) that block linking:"
    printf '  %s\n' "${conflicts[@]}"

    echo
    echo "Adopting means the existing files in your home directory become"
    echo "the versions stored in the dotfiles repository. The previous"
    echo "target and repository versions will both be backed up first."

    if ! confirm "Back up and adopt these files into the Stow package?"; then
        echo "Cancelled. No files were adopted."
        exit 0
    fi

    backup_dir="${STATE_DIR}/backups/$(date '+%Y%m%d-%H%M%S')"
    mkdir -p "${backup_dir}/target" "${backup_dir}/package"

    # Save the current Git state too, so uncommitted repository edits can
    # be reconstructed even if --adopt replaces a package-side file.
    git -C "$REPO_DIR" status --short > "${backup_dir}/git-status.txt" || true
    git -C "$REPO_DIR" diff > "${backup_dir}/git-unstaged.patch" || true
    git -C "$REPO_DIR" diff --cached > "${backup_dir}/git-staged.patch" || true

    for relative_path in "${conflicts[@]}"; do
        target_path="${TARGET_DIR}/${relative_path}"
        package_path="${STOW_DIR}/${PACKAGE}/${relative_path}"

        backup_item "$target_path" "${backup_dir}/target" "$relative_path"
        backup_item "$package_path" "${backup_dir}/package" "$relative_path"
    done

    printf '%s\n' "${conflicts[@]}" > "${backup_dir}/conflicts.txt"

    echo
    echo "Backup created at:"
    echo "  ${backup_dir}"

    echo
    echo "Previewing adoption..."
    echo

    run_stow_capture \
        -nv \
        --adopt \
        --no-folding \
        -d "$STOW_DIR" \
        -t "$TARGET_DIR" \
        "$PACKAGE"

    printf '%s\n' "$STOW_OUTPUT"

    if (( STOW_STATUS != 0 )); then
        error "The adoption preview failed. Nothing was adopted. Backup is at ${backup_dir}"
    fi

    echo
    if ! confirm "Apply the adoption shown above?"; then
        echo "Cancelled. Nothing was adopted. Backup remains at ${backup_dir}"
        exit 0
    fi

    echo
    echo "Adopting existing files into the Stow package..."

    stow \
        -v \
        --adopt \
        --no-folding \
        -d "$STOW_DIR" \
        -t "$TARGET_DIR" \
        "$PACKAGE"

    echo
    echo "Adoption complete. Review these repository changes carefully:"
    git -C "$REPO_DIR" status --short
    echo
    echo "Backup retained at: ${backup_dir}"
}

for command_name in stow git sed sort cp; do
    command -v "$command_name" >/dev/null 2>&1 ||
        error "'${command_name}' is not installed."
done

[[ -d "$REPO_DIR" ]] ||
    error "Dotfiles directory not found: ${REPO_DIR}"

[[ -d "${REPO_DIR}/.git" ]] ||
    error "${REPO_DIR} is not a Git repository."

[[ -d "${STOW_DIR}/${PACKAGE}" ]] ||
    error "Stow package not found: ${STOW_DIR}/${PACKAGE}"

# First perform a plain stow preview. This detects regular-file conflicts
# without the duplicate warnings produced by a restow (-R) preview.
echo "Checking for existing-file conflicts..."
echo

run_stow_capture \
    -nv \
    --no-folding \
    -d "$STOW_DIR" \
    -t "$TARGET_DIR" \
    "$PACKAGE"

if (( STOW_STATUS != 0 )); then
    handle_stow_conflicts
else
    printf '%s\n' "$STOW_OUTPUT"
fi

# Now preview a full restow so stale links are removed and current links
# are recreated from the package.
echo
echo "Previewing final Stow changes..."
echo

run_stow_capture \
    -nRv \
    --no-folding \
    -d "$STOW_DIR" \
    -t "$TARGET_DIR" \
    "$PACKAGE"

printf '%s\n' "$STOW_OUTPUT"

if (( STOW_STATUS != 0 )); then
    error "The final Stow preview failed. No final restow was applied."
fi

echo
if ! confirm "Apply these final Stow changes?"; then
    echo "Cancelled. The Git update and push were not run."
    exit 0
fi

echo
echo "Applying Stow changes..."

stow \
    -Rv \
    --no-folding \
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

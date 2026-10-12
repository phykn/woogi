#!/bin/sh
set -eu

case "${1:-woogi}" in
    woogi) name='Woogi'; folder='woogi' ;;
    pixel) name='Woogi%20Pixel'; folder='woogi-pixel' ;;
    *) printf '%s\n' 'Usage: sh install.sh [woogi|pixel] [--print-link]' >&2; exit 1 ;;
esac

link="codex://pets/install?name=$name&imageUrl=https%3A%2F%2Fraw.githubusercontent.com%2Fphykn%2Fwoogi%2Fmain%2Fpets%2F$folder%2Fspritesheet.png&spriteVersionNumber=2"
if [ "${2:-}" = '--print-link' ]; then
    printf '%s\n' "$link"
else
    open "$link"
    printf '%s\n' 'Confirm installation in Codex, then select your pet in Settings > Pets.'
fi

#!/bin/sh
set -eu

usage() {
    printf '%s\n' 'Usage: sh install.sh [woogi|pixel] [--print-link]' >&2
    exit 1
}

variant=woogi
if [ "$#" -gt 0 ] && [ "$1" != '--print-link' ]; then
    variant=$1
    shift
fi

print_link=false
if [ "$#" -gt 0 ] && [ "$1" = '--print-link' ]; then
    print_link=true
    shift
fi
[ "$#" -eq 0 ] || usage

case "$variant" in
    woogi) name='Woogi'; folder='woogi' ;;
    pixel) name='Woogi%20Pixel'; folder='woogi-pixel' ;;
    *) usage ;;
esac

link="codex://pets/install?name=$name&imageUrl=https%3A%2F%2Fraw.githubusercontent.com%2Fphykn%2Fwoogi%2Fmain%2Fpets%2F$folder%2Fspritesheet.png&spriteVersionNumber=2"
if [ "$print_link" = true ]; then
    printf '%s\n' "$link"
else
    open "$link"
    printf '%s\n' 'In Codex, confirm the installation, then choose your pet in Settings > Pets.'
fi

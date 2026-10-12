# Woogi · Codex Pet

Meet **Woogi**, a custom animated fox pet for the **Codex desktop app**. Choose **Woogi** for a soft 3D look or **Woogi Pixel** for pixel art.

| Woogi | Woogi Pixel |
| :---: | :---: |
| ![Woogi animated preview](previews/woogi.gif) | ![Woogi Pixel animated preview](previews/woogi-pixel.gif) |
| **[Install Woogi](https://phykn.github.io/woogi/#woogi)** | **[Install Woogi Pixel](https://phykn.github.io/woogi/#woogi-pixel)** |

The GIFs preview a few animations. Each pet is supplied as a transparent PNG sprite sheet.

## Install in Codex

Requires the **Codex desktop app with Pets enabled** and an internet connection.

1. Click **Install Woogi** or **Install Woogi Pixel** above, then **Add to Codex**. No terminal needed.
2. Allow your browser to open Codex, then confirm the installation in the app.
3. Choose your new pet in **Settings → Pets**, then use `/pet` or **Show pet** to display it. Repeat to add the other style.

**Codex didn't open?** Update and launch the app, then try again and allow your browser to open it. Check that Pets is available in Settings; older versions may list it under **Appearance**. See the official [Pets guide](https://learn.chatgpt.com/docs/pets?surface=app).

<details>
<summary>Alternative: use an install script</summary>

[Download the ZIP](https://github.com/phykn/woogi/archive/refs/heads/main.zip) and extract it, or run `git clone https://github.com/phykn/woogi.git`. Open a terminal in the extracted `woogi-main` folder (or cloned `woogi` folder), then run:

**Windows (PowerShell)**

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\install.ps1
# For the pixel version:
powershell -NoProfile -ExecutionPolicy Bypass -File .\install.ps1 -Variant pixel
```

**macOS (Terminal)**

```sh
sh install.sh
# For the pixel version:
sh install.sh pixel
```

The scripts open the same Codex installation screen as the buttons. Confirm the installation and select your pet in the app.

</details>

## Assets & reuse

- [Woogi sprite sheet](pets/woogi/spritesheet.png)
- [Woogi Pixel sprite sheet](pets/woogi-pixel/spritesheet.png)

Both sheets use the **v2 format: 1536 × 2288 px, 8 columns × 11 rows, 192 × 208 px per frame**. Preserve the layout and transparency when editing.

To rebuild the GIFs, run these commands from the repository folder with Python installed:

```sh
python -m pip install Pillow
python scripts/preview.py
```

Run installer checks with `python -m unittest discover -s tests`. The checks use mock app launchers; PowerShell and a POSIX shell are needed to exercise both installers.

## License

Artwork and code are available under the [MIT License](LICENSE). You may use, modify, and share them, including commercially, while keeping the license notice.

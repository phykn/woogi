param(
    [ValidateSet('woogi', 'pixel')]
    [string]$Variant = 'woogi',
    [switch]$PrintLink
)

$name = if ($Variant -eq 'pixel') { 'Woogi Pixel' } else { 'Woogi' }
$folder = if ($Variant -eq 'pixel') { 'woogi-pixel' } else { 'woogi' }
$image = "https://raw.githubusercontent.com/phykn/woogi/main/pets/$folder/spritesheet.png"
$link = 'codex://pets/install?name=' + [Uri]::EscapeDataString($name) +
    '&imageUrl=' + [Uri]::EscapeDataString($image) + '&spriteVersionNumber=2'

if ($PrintLink) {
    Write-Output $link
} else {
    Start-Process -FilePath $link -ErrorAction Stop
    Write-Output "In Codex, confirm the installation, then choose $name in Settings > Pets."
}

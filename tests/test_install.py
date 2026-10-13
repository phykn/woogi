"""Check install links and launch failures without opening Codex."""

import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from urllib.parse import parse_qs, urlsplit


ROOT = Path(__file__).resolve().parents[1]
POWERSHELL = shutil.which('powershell') or shutil.which('pwsh')
SH = shutil.which('sh')
if SH is None and os.name == 'nt':
    git_sh = Path(os.environ.get('ProgramFiles', 'C:/Program Files')) / 'Git/bin/sh.exe'
    if git_sh.is_file():
        SH = str(git_sh)


class InstallTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        for name in ('install.ps1', 'install.sh'):
            shutil.copyfile(ROOT / name, self.folder / name)

    def run_sh(self, args, fail=False):
        launcher = self.folder / 'open'
        launcher.write_text(
            '#!/bin/sh\nprintf "OPEN %s\\n" "$1"\n' + ('exit 1\n' if fail else ''),
            encoding='utf-8',
        )
        launcher.chmod(0o755)
        env = dict(os.environ, PATH=str(self.folder) + os.pathsep + os.environ['PATH'])
        return subprocess.run(
            [SH, 'install.sh', *args], cwd=self.folder, env=env,
            capture_output=True, text=True, timeout=120,
        )

    def run_ps(self, args, fail=False):
        action = "Write-Error 'Launch failed'" if fail else 'Write-Output "OPEN $FilePath"'
        command = (
            'function Start-Process { [CmdletBinding()] param([string]$FilePath) '
            + action + ' }; & ./install.ps1 ' + args
        )
        return subprocess.run(
            [POWERSHELL, '-NoProfile', '-ExecutionPolicy', 'Bypass', '-Command', command],
            cwd=self.folder, capture_output=True, text=True, timeout=120,
        )

    def check_link(self, result, variant):
        self.assertEqual(result.returncode, 0, result.stderr)
        lines = result.stdout.splitlines()
        self.assertEqual(len(lines), 1, result.stdout)
        link = urlsplit(lines[0])
        self.assertEqual((link.scheme, link.netloc, link.path), ('codex', 'pets', '/install'))
        self.assertFalse(link.fragment)
        folder = 'woogi-pixel' if variant == 'pixel' else 'woogi'
        self.assertEqual(parse_qs(link.query, strict_parsing=True), {
            'name': ['Woogi Pixel' if variant == 'pixel' else 'Woogi'],
            'imageUrl': [f'https://raw.githubusercontent.com/phykn/woogi/main/pets/{folder}/spritesheet.png'],
            'spriteVersionNumber': ['2'],
        })
        return lines[0]

    def check_launch(self, result, link):
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.splitlines()[0], 'OPEN ' + link)
        self.assertIn('confirm the installation', result.stdout)

    @unittest.skipUnless(SH, 'POSIX shell unavailable')
    def test_shell_rejects_invalid_arguments_without_launching(self):
        for args in (
            ['other'], ['woogi', '--print-lnik'], ['pixel', '--print-link', 'extra'],
            ['--print-link', 'pixel'], ['--print-link', '--print-link'],
        ):
            with self.subTest(args=args):
                result = self.run_sh(args)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('Usage:', result.stderr)
                self.assertNotIn('OPEN', result.stdout)

    @unittest.skipUnless(POWERSHELL, 'PowerShell unavailable')
    def test_powershell_rejects_invalid_arguments_without_launching(self):
        for args in ('-PrintLnik', '-Variant woogi -PrintLnik', '-Variant woogi extra', '-Variant other'):
            with self.subTest(args=args):
                result = self.run_ps(args)
                self.assertNotEqual(result.returncode, 0)
                self.assertNotIn('OPEN', result.stdout)
                self.assertNotIn('confirm the installation', result.stdout)

    @unittest.skipUnless(SH, 'POSIX shell unavailable')
    def test_shell_reports_failed_launch(self):
        result = self.run_sh(['woogi'], fail=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn('confirm the installation', result.stdout)

    @unittest.skipUnless(POWERSHELL, 'PowerShell unavailable')
    def test_powershell_reports_failed_launch(self):
        result = self.run_ps('', fail=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Launch failed', result.stderr)
        self.assertNotIn('confirm the installation', result.stdout)

    @unittest.skipUnless(SH, 'POSIX shell unavailable')
    def test_shell_prints_and_launches_expected_links(self):
        for args, variant in (([], 'woogi'), (['woogi'], 'woogi'), (['pixel'], 'pixel')):
            with self.subTest(args=args):
                link = self.check_link(self.run_sh([*args, '--print-link']), variant)
                self.check_launch(self.run_sh(args), link)

    @unittest.skipUnless(POWERSHELL, 'PowerShell unavailable')
    def test_powershell_prints_and_launches_expected_links(self):
        for args, variant in (('', 'woogi'), ('-Variant woogi', 'woogi'), ('-Variant pixel', 'pixel')):
            with self.subTest(args=args):
                link = self.check_link(self.run_ps(args + ' -PrintLink'), variant)
                self.check_launch(self.run_ps(args), link)


if __name__ == '__main__':
    unittest.main()

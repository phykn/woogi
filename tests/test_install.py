"""Check install links and launch failures without opening Codex."""

import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


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
            capture_output=True, text=True,
        )

    def run_ps(self, args, fail=False):
        action = "Write-Error 'Launch failed'" if fail else 'Write-Output "OPEN $FilePath"'
        command = (
            'function Start-Process { [CmdletBinding()] param([string]$FilePath) '
            + action + ' }; & ./install.ps1 ' + args
        )
        return subprocess.run(
            [POWERSHELL, '-NoProfile', '-Command', command], cwd=self.folder,
            capture_output=True, text=True,
        )

    @unittest.skipUnless(SH, 'POSIX shell unavailable')
    def test_shell_rejects_invalid_arguments_without_launching(self):
        for args in (['other'], ['woogi', '--print-lnik'], ['pixel', '--print-link', 'extra']):
            with self.subTest(args=args):
                result = self.run_sh(args)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('Usage:', result.stderr)
                self.assertNotIn('OPEN', result.stdout)

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

    @unittest.skipUnless(POWERSHELL and SH, 'PowerShell and POSIX shell required')
    def test_printed_and_launched_links_match_for_both_styles(self):
        for variant in ('woogi', 'pixel'):
            with self.subTest(variant=variant):
                ps = self.run_ps(f'-Variant {variant} -PrintLink')
                sh = self.run_sh([variant, '--print-link'])
                self.assertEqual(ps.returncode, 0, ps.stderr)
                self.assertEqual(sh.returncode, 0, sh.stderr)
                self.assertEqual(ps.stdout.strip(), sh.stdout.strip())
                self.assertTrue(ps.stdout.startswith('codex://pets/install?'))
                self.assertNotIn('OPEN', ps.stdout + sh.stdout)
                for result in (self.run_ps(f'-Variant {variant}'), self.run_sh([variant])):
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(result.stdout.splitlines()[0], 'OPEN ' + ps.stdout.strip())
                    self.assertIn('confirm the installation', result.stdout)


if __name__ == '__main__':
    unittest.main()

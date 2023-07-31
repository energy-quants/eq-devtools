from click.testing import CliRunner

from eq.devtools.cli import cli


def test_greet():
  runner = CliRunner()
  res = runner.invoke(cli, ['test', 'greet', '--name',  "Dave"])
  assert res.exit_code == 0, res.stdout
  assert res.output == "Hello Dave!\n"

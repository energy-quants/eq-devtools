from click.testing import CliRunner

from eq.devtools.cli import cli


def test_greet():
  runner = CliRunner()
  result = runner.invoke(cli, ['greet', '--name',  "Dave"])
  assert result.exit_code == 0
  assert result.output == "Hello Dave!\n"

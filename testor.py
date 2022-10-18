from click.testing import CliRunner

from hcycle import cli


def test_hcycle():
  runner = CliRunner()
  runner.invoke(cli, ['cycle-test', "-env", "stage", "-s", "D rack Towering Infernos", "-gr", "Cab B", "-cy", "2", "-w", ".5", "-cr", "10", "-em", "-f",  "blorp.csv", "--testing"])

def test_is_it_on():
  runner = CliRunner()
  runner.invoke(cli, ['is-this-thing-on'])
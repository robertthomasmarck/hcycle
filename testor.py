from click.testing import CliRunner

from hcycle import cli


def test_hcycle():
    runner = CliRunner()
    runner.invoke(cli,
                  ['cycle-test', "-env", "stage", "-s", "GlareControlTestSLC", "-gr", "Test Group: DR-250 LC", "-cy",
                   "50", "-cp", "10", "-cr", "30", "-em", "-full", "-f", "blorp.csv", "--debug"])


def test_is_it_on():
    runner = CliRunner()
    runner.invoke(cli, ['is-this-thing-on'])


def test_ctest():
    runner = CliRunner()
    runner.invoke(cli, ['run-ctest', '-st', 'STRESS_westwall'])

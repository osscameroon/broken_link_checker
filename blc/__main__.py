import logging
from configparser import ConfigParser

# import threading
import coloredlogs
import typer

from .checker import Checker  # Assuming existing module
from .notifier import Notifier  # Assuming existing module

coloredlogs.install()

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

app = typer.Typer()
logger = logging.getLogger(__name__)


def load_config(config_file: str) -> dict:
    """
    the main propulse of this function is the load the configiration file

    input ::: config_file: configuration file
    output : object configuration file

    """
    config = ConfigParser()
    try:
        with open(config_file) as f:
            config.read_file(f)
    except OSError as err:
        typer.echo(f"Error loading config: {err}", err=True)
        raise typer.Exit(code=1)

    defaults = {}
    if config.has_section("Checker"):
        defaults.update(dict(config.items("Checker")))
    if config.has_section("Notifier"):
        defaults.update(dict(config.items("Notifier")))

    return defaults


@app.command()
def main(
    host: str | None = typer.Option(None, help="Eg: http://example.com"),
    delay: float | None = typer.Option(
        1.0, "--delay", "-d", help="Delay between requests"
    ),
    sender: str | None = typer.Option(None, help="Email used to send report"),
    password: str | None = typer.Option(None, help="Password for email login"),
    smtp_server: str | None = typer.Option(None, help="SMTP server to send report"),
    recipient: str | None = typer.Option(None, help="Recipient email"),
    browser_sleep: float | None = typer.Option(
        None, help="Browser extension sleep time"
    ),
    deep_scan: bool = typer.Option(False, "--deep-scan", "-n", help="Enable deep scan"),
    config_file: str | None = typer.Option(
        None, "--config-file", "-c", help="Path to configuration file"
    ),
    debug: bool = typer.Option(False, "--debug", "-D", help="Enable debug mode"),
):
    """Do something."""

    if not debug:
        logging.disable(logging.CRITICAL)

    defaults = {
        "host": host,
        "delay": delay,
        "sender": sender,
        "password": password,
        "smtp_server": smtp_server,
        "recipient": recipient,
        "browser_sleep": browser_sleep,
    }

    # parse values from a configuration file if provided and use those as the
    # default values for the argparse arguments

    if config_file:
        typer.echo("Loading configuration file...")
        loaded = load_config(config_file)

        # update configuration file dict object
        for k, v in loaded.items():
            if k in defaults and defaults[k] is None:
                defaults[k] = v
        # typer.echo(defaults)

    if not defaults["host"]:
        typer.echo("Error: host is required", err=True)
        raise typer.Exit(code=1)

    notifier_fields = [
        defaults["sender"],
        defaults["password"],
        defaults["smtp_server"],
        defaults["recipient"],
    ]
    if any(notifier_fields) and not all(notifier_fields):
        typer.echo("Error: bad configuration of the notifier", err=True)
        raise typer.Exit(code=1)

    report = {}
    conn = None

    for target in defaults["host"].split(","):
        checker = Checker(
            target,
            delay=float(defaults["delay"]),
            deep_scan=deep_scan,
            browser_sleep=float(defaults["browser_sleep"])
            if defaults["browser_sleep"]
            else None,
        )
        if conn:
            checker.conn = conn
        else:
            conn = checker.conn

        # We config the shared dict
        report[target] = checker.urls
        checker.run()

    # We initialize the notifier

    notifier = Notifier(
        smtp_server=defaults["smtp_server"],
        username=defaults["sender"],
        password=defaults["password"],
    )

    # We start the checkers
    # for thread in checker_threads:
    #    logger.info('Checking of %s' % args.host)
    #    thread.start()

    # We wait for the completion
    # [thread.join() for thread in checker_threads]

    # We build the report

    msg = "Hello, the report of the broken link checker is ready.\n"
    for target, value in report.items():
        msg += f"\n--------------\nReport of {target}\n--------------"
        if not value:
            continue

        acc = 0
        for url, info in value.items():
            if info["result"][0]:
                continue

            msg += (
                f"\nURL:        {url}\n"
                f"Parent URL: {info['parent']}\n"
                f"Real URL:   {info['url']}\n"
                f"Check time: {round(info['check_time'], 4)} seconds\n"
                f"Result:     {info['result'][1]} -> {info['result'][2]}\n"
            )
            acc += 1

        msg += (
            f"\nThat's it. {acc} errors in {len(value)} links found.\n--------------\n"
        )

    # We verify if the email notifier is configured
    if defaults["smtp_server"]:
        logger.info(f"Sending report to {defaults['recipient']}...")
        notifier.send(
            subject="Broken links found",
            body=msg or "No broken url found\n",
            recipient=defaults["recipient"],
        )
    else:
        print(msg)


if __name__ == "__main__":
    app()

import click


@click.group()
def cli():
    pass


@cli.command()
@click.option(
    "--opt",
    default="opt1",
    help="Example option",
    show_default=True,
    type=click.Choice(["opt1", "opt2"]),
)
def option(opt):
    print("Option: " + opt)
    if yes_or_no(f"Do you like the example?"):
        pass


def yes_or_no(question):
    while "the answer is invalid":
        reply = str(input(question + " (y/n): ")).lower().strip()
        if reply[:1] == "y":
            return True
        if reply[:1] == "n":
            return False


if __name__ == "__main__":
    cli()

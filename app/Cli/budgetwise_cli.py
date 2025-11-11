# budgetwise_cli.py
import click
from auth_commands import auth
from transaction_commands import transactions
from category_commands import categories
from summary_commands import summary

@click.group()
def cli():
    """Budgetwise CLI — Manage your personal budget from the terminal."""
    pass

# Register subcommand groups
cli.add_command(auth)
cli.add_command(transactions)
cli.add_command(categories)
cli.add_command(summary)

if __name__ == "__main__":
    cli()

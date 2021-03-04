import click

from dafni_cli.login import login
import dafni_cli.model as model


@click.group()
@click.pass_context
def get(ctx):
    """Lists entities available to the user from
    models, datasets, workflows, groups, depending on command."""
    ctx.ensure_object(dict)
    jwt = ctx.invoke(login)
    ctx.obj['jwt'] = jwt


@get.command(help="List and filter models")
@click.option('--summary/--no-summary', default=False,
              help="Display short summary of model")
@click.option('--descr/--no-descr', default=False,
              help="Display full description of model")
@click.option('--creation-date', default=None,
              help="Filter for models created since given date. Format: DD/MM/YYYY")
@click.option('--publication-date', default=None,
              help="Filter for models published since given date. Format: DD/MM/YYYY")
@click.pass_context
def models(ctx, summary, descr, creation_date, publication_date):
    """Displays list of model names with other options allowing
        more details to be listed as well.

        Args:
            ctx: context containing the JWT
            summary (bool): whether summary should be displayed
            descr (bool): whether description should be displayed
            creation_date (str): for filtering by creation date. Format: DD/MM/YYYY
            publication_date (str): for filtering by publication date. Format: DD/MM/YYYY
        """
    model.list_groups(ctx, summary, descr, creation_date, publication_date)


@get.command()
def datasets():
    pass


@get.command()
def workflows():
    pass


@get.command()
def groups():
    pass


if __name__ == "__main__":
    get(obj={})

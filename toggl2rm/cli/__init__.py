import typer
from pathlib import Path
import toml

tgl = typer.Typer()
rdm = typer.Typer()
app = typer.Typer()

app.add_typer(rdm, name='rdm')
app.add_typer(rdm, name='tgl')




if __name__ == '__main__':
    app()

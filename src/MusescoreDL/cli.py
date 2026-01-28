import typer

from .MusescoreDL import DownloadScore

app = typer.Typer()
app.command()(DownloadScore)

if __name__ == "__main__":
    app()
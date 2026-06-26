from pathlib import Path

# ---------------------------------------------------------------------------- #
#                             CLI Argument Parsing                             #
# ---------------------------------------------------------------------------- #

def parse_args(args: list[str]) -> list[Path]:
    """Return a list of Paths from the command-line arguments."""
    paths: list[Path] = []
    for arg in args:
        p = Path(arg)
        if p.exists():
            paths.append(p)
        else:
            print(f"[Warning] Skipping non-existent path: {arg}")
    return paths
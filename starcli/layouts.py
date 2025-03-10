"""starcli.layouts"""

import math

from rich.align import Align
from rich.console import Console, group
from rich.rule import Rule
from rich.table import Table
from rich.text import Text
from rich.panel import Panel
from rich.columns import Columns


console = Console()

SYMBOL_MAP = {"stars": "★", "forks": "⎇"}

# Block characters for the graph bars
GRAPH_BLOCKS = "█"


def shorten_count(number):
    """Shortens number"""
    if number < 1000:
        return str(number)

    number = int(number)
    new_number = math.ceil(round(number / 100.0, 1)) * 100

    if new_number % 1000 == 0:
        return str(new_number)[0] + "k"
    if new_number < 1000:
        # returns the same old integer if no changes were made
        return str(number)
    # returns a new string if the number was shortened
    return str(new_number / 1000.0) + "k"


def format_stats(stars, forks):
    """Formatted string of repo stats"""
    stats = f"{stars}{SYMBOL_MAP['stars']} " if stars != "-1" else ""
    stats += f"{forks}{SYMBOL_MAP['forks']} " if forks != "-1" else ""
    return stats


def format_date_range(date_range):
    """Formatted and styled Text object of date_range period stars"""
    if not date_range:
        return Text("")
    return (
        Text("(", style="reset")
        .append(
            (date_range.replace(" stars", SYMBOL_MAP["stars"])), style="italic magenta"
        )
        .append(")")
    )

def graph_layout(repos):
    """Displays repositories in a graph format using rich"""
    
    # Convert formatted star/fork counts to integers for calculation
    def parse_count(count_str):
        if count_str == "-1":
            return 0
        # Handle shortened counts like "90.3k"
        if isinstance(count_str, str) and 'k' in count_str.lower():
            # Convert "90.3k" to 90300
            return int(float(count_str.lower().replace('k', '')) * 1000)
        return int(count_str)
    
    # Find the maximum star count for scaling
    max_stars = max(parse_count(repo["stargazers_count"]) for repo in repos)
    max_forks = max(parse_count(repo["forks"]) for repo in repos)
    
    # Maximum width for the bar (in characters)
    max_bar_width = 40
    
    table = Table(show_header=False, box=None, padding=(0, 1))
    table.add_column("Repo", style="bold yellow", no_wrap=True)
    table.add_column("Stats")
    table.add_column("Bars", width=max_bar_width + 10)
    
    for repo in repos:
        name = Text(repo["name"], overflow="fold")
        name.stylize(f"yellow link {repo['html_url']}")
        
        stats = format_stats(repo["stargazers_count"], repo["forks"])
        date_range_col = format_date_range(repo.get("date_range"))
        stats_text = Text(stats, style="italic blue")
        if date_range_col:
            stats_text.append("\n")
            stats_text.append(date_range_col)
        
        # Create bar graphs for stars and forks
        stars_count = parse_count(repo["stargazers_count"])
        forks_count = parse_count(repo["forks"])
        
        # Scale the bars
        stars_bar_width = int((stars_count / max_stars) * max_bar_width) if max_stars > 0 else 0
        forks_bar_width = int((forks_count / max_stars) * max_bar_width) if max_stars > 0 else 0
        
        # Create the bars
        stars_bar = Text(GRAPH_BLOCKS * stars_bar_width, style="bright_yellow")
        forks_bar = Text(GRAPH_BLOCKS * forks_bar_width, style="bright_blue")
        
        # Add labels
        bars = Text(f"{SYMBOL_MAP['stars']} ", style="bright_yellow")
        bars.append(stars_bar)
        bars.append(f" {repo['stargazers_count']}\n")
        bars.append(f"{SYMBOL_MAP['forks']} ", style="bright_blue")
        bars.append(forks_bar)
        bars.append(f" {repo['forks']}")
        
        table.add_row(name, stats_text, bars)
    
    console.print(table)

def list_layout(repos):
    """Display repositories in a list layout using rich"""

    width = 80

    @group()
    def render_repo(repo):
        """Yields renderables for a single repo."""
        yield Rule(style="bright_yellow")
        yield ""
        # Table with description and stats
        title_table = Table.grid(padding=(0, 1))
        title_table.expand = True
        title = Text(repo["full_name"], overflow="fold")
        title.stylize(f"yellow link {repo['html_url']}")

        stats = format_stats(repo["stargazers_count"], repo["forks"])
        date_range_col = format_date_range(repo.get("date_range"))

        title_table.add_row(title, Text(stats, style="italic blue"))
        title_table.columns[1].no_wrap = True
        title_table.columns[1].justify = "right"
        yield title_table
        yield ""
        lang_table = Table.grid(padding=(0, 1))
        lang_table.expand = True
        language_col = (
            Text(repo["language"], style="bold cyan")
            if repo["language"]
            else Text("no language")
        )
        lang_table.add_row(language_col, date_range_col)
        lang_table.columns[1].justify = "right"
        yield lang_table
        yield ""
        # Description
        description = repo["description"]
        if description:
            yield Text(description.strip())
        else:
            yield "[i]no description"
        yield ""

    def column(renderable):
        """Constrain width and align to center to create a column."""
        return Align.center(renderable, width=width, pad=False)

    for repo in repos:
        console.print(column(render_repo(repo)))
    console.print(column(Rule(style="bright_yellow")))


def table_layout(repos):
    """Displays repositories in a table format using rich"""
    table = Table(leading=1)

    # make the columns
    table.add_column("Name", style="bold yellow")
    table.add_column("Language")
    table.add_column("Description")
    table.add_column("Stats", justify="right")

    for repo in repos:
        stats = Text(
            format_stats(repo["stargazers_count"], repo["forks"]), style="blue"
        )
        stats.append("\n").append(format_date_range(repo.get("date_range")))

        language = (
            Text(repo["language"], style="cyan")
            if repo["language"]
            else Text("no language", style="italic")
        )
        description = (
            Text(repo["description"])
            if repo["description"]
            else Text("no description", style="italic")
        )

        name = Text(repo["name"], overflow="fold")
        name.stylize(f"yellow link {repo['html_url']}")

        table.add_row(name, language, description, stats)

    console.print(table)


def grid_layout(repos):
    """Displays repositories in a grid format using rich"""

    max_desc_len = 90

    panels = []
    for repo in repos:

        stats = format_stats(repo["stargazers_count"], repo["forks"])
        # '\n' added here as it would group both text and new line together
        # hence if date_range isn't present the new line will also not be displayed
        date_range = format_date_range(repo.get("date_range")).append("\n")

        language = (
            Text(repo["language"], style="cyan")
            if repo["language"]
            else Text("no language", style="italic")
        )
        description = (
            Text(repo["description"])
            if repo["description"]
            else Text("no description", style="italic")
        )

        name = Text(repo["name"], style="bold yellow")
        name.stylize(f"link {repo['html_url']}")
        stats = Text(stats, style="blue")

        # truncate rest of the description if
        # it's more than 90 (max_desc_len) chars
        # using truncate() is better than textwrap
        # because it also takes care of asian characters
        description.truncate(max_desc_len, overflow="ellipsis")

        repo_summary = Text.assemble(
            name,
            "\n",
            stats,
            " ",
            date_range,
            language,
            "\n",
            description,
        )
        panels.append(Panel(repo_summary, expand=True))

    console.print((Columns(panels, width=30, expand=True)))


def print_results(*args, page=False, layout=""):
    """Use a specified layout to print or page the fetched results"""
    if page:
        with console.pager():
            print_layout(layout=layout, *args)
        return
    print_layout(
        layout=layout,
        *args,
    )


def print_layout(*args, layout="list"):
    """Use specified layout"""
    if layout == "table":
        table_layout(*args)
    elif layout == "grid":
        grid_layout(*args)
    elif layout == "graph":
        graph_layout(*args)
    else:
        list_layout(*args)

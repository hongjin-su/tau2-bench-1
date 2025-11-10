"""CLI entry point for agentify-example-tau-bench."""

import asyncio

import typer
from agentify_tau_bench.green_agent import start_green_agent
from agentify_tau_bench.launcher import launch_evaluation
from agentify_tau_bench.white_agent import start_white_agent

app = typer.Typer(help="Agentified Tau-Bench - Standardized agent assessment framework")


@app.command()
def green():
    """Start the green agent (assessment manager)."""
    start_green_agent()


@app.command()
def white():
    """Start the white agent (target being tested)."""
    start_white_agent()


@app.command()
def launch():
    """Launch the complete evaluation workflow."""
    asyncio.run(launch_evaluation())


if __name__ == "__main__":
    app()

import click
import os
from pathlib import Path
from typing import Optional
from .abi_analyzer import ABIAnalyzer
import json
import asyncio
from .mcp_generator import MCPGenerator

@click.group()
def cli():
    """MCP Server Generator CLI"""
    pass

@cli.command()
@click.argument('abi_file', type=click.Path(exists=True))
@click.argument('output_dir', type=click.Path())
@click.argument('contract_name')
def generate(abi_file: str, output_dir: str, contract_name: str):
    """Generate an MCP server from a contract ABI."""
    # Check for OpenAI API key
    openai_api_key = os.getenv('OPENAI_API_KEY')
    if not openai_api_key:
        click.echo("Error: OPENAI_API_KEY environment variable is not set", err=True)
        return
        
    # Load ABI
    with open(abi_file) as f:
        abi = json.load(f)
        
    # Analyze ABI
    analyzer = ABIAnalyzer(abi)
    analysis = analyzer.analyze()
    
    # Create generator
    generator = MCPGenerator(
        analysis=analysis,
        output_dir=Path(output_dir),
        contract_name=contract_name,
        openai_api_key=openai_api_key
    )
    
    # Generate server
    asyncio.run(generator.generate())
    
    click.echo(f"MCP server generated in {output_dir}")

@cli.command()
@click.argument('cache_dir', type=click.Path(exists=True))
def clear_cache(cache_dir: str):
    """Clear the method implementation cache."""
    cache_path = Path(cache_dir)
    if not cache_path.exists():
        click.echo("Cache directory does not exist")
        return
        
    # Remove all .py files in cache directory
    for file in cache_path.glob("*.py"):
        file.unlink()
        
    click.echo("Cache cleared")

if __name__ == '__main__':
    cli() 
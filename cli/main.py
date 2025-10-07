"""
KubeGenie CLI

A command-line interface for the KubeGenie Kubernetes and Crossplane automation agent.
"""

import typer
import requests
import json
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from typing import Optional, List
import os

app = typer.Typer(help="KubeGenie - Smart Kubernetes and Crossplane automation")
console = Console()

# Configuration
API_BASE_URL = os.getenv("KUBEGENIE_API_URL", "http://localhost:8000")


@app.command()
def chat(message: str):
    """Send a natural language message to KubeGenie"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/v1/chat/message",
            json={"message": message}
        )
        response.raise_for_status()
        
        data = response.json()
        
        # Display response
        console.print(Panel(data["response"], title="KubeGenie Response", style="blue"))
        
        # Display actions if any
        if data.get("actions"):
            console.print("\n[bold]Actions to be performed:[/bold]")
            for i, action in enumerate(data["actions"], 1):
                console.print(f"{i}. {action['type']}")
                for key, value in action.get("parameters", {}).items():
                    console.print(f"   {key}: {value}")
        
        # Display suggestions
        if data.get("suggestions"):
            console.print("\n[bold]Suggestions:[/bold]")
            for suggestion in data["suggestions"]:
                console.print(f"• {suggestion}")
                
    except requests.exceptions.RequestException as e:
        console.print(f"[red]Error communicating with API: {e}[/red]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


@app.command()
def deploy(
    name: str,
    image: str,
    replicas: int = typer.Option(1, help="Number of replicas"),
    namespace: str = typer.Option("default", help="Kubernetes namespace")
):
    """Deploy an application to Kubernetes"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/v1/k8s/deployments",
            json={
                "name": name,
                "image": image,
                "replicas": replicas,
                "namespace": namespace
            }
        )
        response.raise_for_status()
        
        data = response.json()
        console.print(f"[green]✓[/green] Deployed {name} with {replicas} replicas")
        console.print(f"  Image: {image}")
        console.print(f"  Namespace: {namespace}")
        
    except requests.exceptions.RequestException as e:
        console.print(f"[red]Error: {e}[/red]")


@app.command()
def scale(
    name: str,
    replicas: int,
    namespace: str = typer.Option("default", help="Kubernetes namespace")
):
    """Scale a deployment"""
    try:
        response = requests.patch(
            f"{API_BASE_URL}/api/v1/k8s/deployments/{name}/scale",
            json={"replicas": replicas},
            params={"namespace": namespace}
        )
        response.raise_for_status()
        
        console.print(f"[green]✓[/green] Scaled {name} to {replicas} replicas")
        
    except requests.exceptions.RequestException as e:
        console.print(f"[red]Error: {e}[/red]")


@app.command()
def pods(
    namespace: str = typer.Option("default", help="Kubernetes namespace")
):
    """List pods in a namespace"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/v1/k8s/pods",
            params={"namespace": namespace}
        )
        response.raise_for_status()
        
        pods = response.json()
        
        if not pods:
            console.print(f"No pods found in namespace '{namespace}'")
            return
            
        table = Table(title=f"Pods in namespace '{namespace}'")
        table.add_column("Name", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Ready", justify="center")
        table.add_column("Restarts", justify="center")
        table.add_column("Age")
        
        for pod in pods:
            status_style = "green" if pod["status"] == "Running" else "red"
            table.add_row(
                pod["name"],
                f"[{status_style}]{pod['status']}[/{status_style}]",
                str(pod["ready"]),
                str(pod["restarts"]),
                str(pod["age"])
            )
        
        console.print(table)
        
    except requests.exceptions.RequestException as e:
        console.print(f"[red]Error: {e}[/red]")


@app.command()
def provision(
    name: str,
    provider: str = typer.Option(..., help="Cloud provider (aws, gcp, azure)"),
    resource_type: str = typer.Option(..., help="Resource type (rds, s3, gke, etc.)"),
):
    """Provision cloud resources via Crossplane"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/v1/crossplane/resources",
            json={
                "name": name,
                "provider": provider,
                "resource_type": resource_type,
                "parameters": {}
            }
        )
        response.raise_for_status()
        
        data = response.json()
        console.print(f"[green]✓[/green] Provisioning {resource_type} resource: {name}")
        console.print(f"  Provider: {provider}")
        console.print(f"  Status: {data.get('status', 'unknown')}")
        
    except requests.exceptions.RequestException as e:
        console.print(f"[red]Error: {e}[/red]")


@app.command()
def status(
    namespace: str = typer.Option("default", help="Kubernetes namespace")
):
    """Show cluster status"""
    try:
        # Get pods
        pods_response = requests.get(
            f"{API_BASE_URL}/api/v1/k8s/pods",
            params={"namespace": namespace}
        )
        pods_response.raise_for_status()
        pods = pods_response.json()
        
        # Get events
        events_response = requests.get(
            f"{API_BASE_URL}/api/v1/k8s/events",
            params={"namespace": namespace}
        )
        events_response.raise_for_status()
        events = events_response.json()
        
        console.print(Panel(f"Cluster Status - Namespace: {namespace}", style="blue"))
        
        # Pod summary
        running_pods = len([p for p in pods if p["status"] == "Running"])
        total_pods = len(pods)
        console.print(f"Pods: {running_pods}/{total_pods} running")
        
        # Recent events
        if events:
            console.print("\n[bold]Recent Events:[/bold]")
            for event in events[:5]:  # Show last 5 events
                event_style = "red" if event["type"] == "Warning" else "green"
                console.print(f"[{event_style}]{event['type']}[/{event_style}]: {event['message']}")
        
    except requests.exceptions.RequestException as e:
        console.print(f"[red]Error: {e}[/red]")


@app.command()
def version():
    """Show KubeGenie version"""
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        response.raise_for_status()
        
        data = response.json()
        console.print(f"KubeGenie CLI v1.0.0")
        console.print(f"Backend: {data.get('version', 'unknown')}")
        
    except requests.exceptions.RequestException as e:
        console.print(f"[red]Error connecting to KubeGenie backend: {e}[/red]")


if __name__ == "__main__":
    app()
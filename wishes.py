from rich import print
import pyfiglet, datetime

# Print ASCII art banner
print(f"[yellow]{pyfiglet.figlet_format('Happy Birthday!')}[/yellow]")

# Ask for user input
name = input("Your name: ")

# Current year
year = datetime.datetime.now().year

# Welcome message
print(f"\n[bold green]Happy Birthday, {name}![/bold green]")
print("[cyan]Celebrate + Smile + Shine[/cyan]\n")

# Birthday wishes
for f in [
    "May your code always compile 🎂",
    "Another year, another adventure 🚀",
    "Keep learning, keep growing 🌟"
]:
    print(f"[yellow]{f}[/yellow]")

# Closing message
print(f"\n[bold white]Wishing you joy and success in {year}![/bold white]")
print("[bold red]Wishes by Roshan[/bold red]")

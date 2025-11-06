"""
Command Line Interface for SkillMatch.AI
"""
import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm
from rich.syntax import Syntax

from .models import UserProfile, SkillItem, ExperienceLevel, PreferenceType, UserPreferences
from .agents.skill_match_agent import SkillMatchAgent
from .utils.data_loader import DataLoader


console = Console()


def load_config() -> Dict[str, Any]:
    """Load configuration from file or environment"""
    config = {}
    
    # Try to load from config file
    config_path = Path("config/config.json")
    if config_path.exists():
        with open(config_path, 'r') as f:
            config = json.load(f)
    
    # Override with environment variables
    if "GITHUB_TOKEN" in os.environ:
        config["github_token"] = os.environ["GITHUB_TOKEN"]
    
    return config


def create_sample_user_profile() -> UserProfile:
    """Create a sample user profile for testing"""
    skills = [
        SkillItem(
            skill_id="python",
            skill_name="Python",
            category="programming",
            level=ExperienceLevel.ADVANCED,
            years_experience=5.0
        ),
        SkillItem(
            skill_id="machine-learning",
            skill_name="Machine Learning",
            category="data_science",
            level=ExperienceLevel.INTERMEDIATE,
            years_experience=3.0
        ),
        SkillItem(
            skill_id="sql",
            skill_name="SQL",
            category="database",
            level=ExperienceLevel.INTERMEDIATE,
            years_experience=4.0
        )
    ]
    
    preferences = UserPreferences(
        work_type=[PreferenceType.REMOTE, PreferenceType.HYBRID],
        desired_roles=["Data Scientist", "Machine Learning Engineer"],
        salary_min=100000,
        locations=["San Francisco", "Remote"],
        industries=["Technology", "Healthcare"]
    )
    
    return UserProfile(
        user_id="sample_user",
        name="John Developer",
        email="john@example.com",
        location="San Francisco, CA",
        summary="Experienced Python developer with strong background in data science and machine learning.",
        skills=skills,
        preferences=preferences,
        career_goals=["Become a senior data scientist", "Lead ML projects", "Learn deep learning"]
    )


@click.group()
@click.option('--config', default='config/config.json', help='Configuration file path')
@click.pass_context
def cli(ctx, config):
    """SkillMatch.AI - Intelligent Career and Skill Matching System"""
    ctx.ensure_object(dict)
    ctx.obj['config_path'] = config
    
    # Load configuration
    try:
        config_data = load_config()
        ctx.obj['config'] = config_data
    except Exception as e:
        console.print(f"[red]Error loading configuration: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.pass_context
def setup(ctx):
    """Set up SkillMatch.AI configuration"""
    console.print(Panel.fit("SkillMatch.AI Setup", style="bold blue"))
    
    # Get GitHub token
    github_token = Prompt.ask(
        "Enter your GitHub Personal Access Token",
        password=True,
        default=ctx.obj['config'].get('github_token', '')
    )
    
    # Get model preference
    model_options = [
        "openai/gpt-4.1-mini",
        "openai/gpt-4.1",
        "openai/gpt-4o-mini",
        "microsoft/phi-4-mini-instruct"
    ]
    
    console.print("\nAvailable models:")
    for i, model in enumerate(model_options, 1):
        console.print(f"  {i}. {model}")
    
    model_choice = Prompt.ask(
        "Choose a model",
        choices=[str(i) for i in range(1, len(model_options) + 1)],
        default="1"
    )
    
    selected_model = model_options[int(model_choice) - 1]
    
    # Save configuration
    config = {
        "github_token": github_token,
        "model_id": selected_model,
        "skills_db_path": "data/skills_database.json",
        "opportunities_db_path": "data/opportunities_database.json"
    }
    
    # Create config directory if it doesn't exist
    config_dir = Path("config")
    config_dir.mkdir(exist_ok=True)
    
    # Save config file
    with open("config/config.json", 'w') as f:
        json.dump(config, f, indent=2)
    
    console.print("[green]✓ Configuration saved successfully![/green]")
    console.print(f"Model: {selected_model}")
    console.print("You can now use SkillMatch.AI commands.")


@cli.command()
@click.option('--profile', default='profiles/sample_profile.json', help='User profile JSON file')
@click.option('--interactive', is_flag=True, help='Interactive mode')
@click.pass_context
async def match(ctx, profile, interactive):
    """Find matching opportunities for a user profile"""
    config = ctx.obj['config']
    
    if not config.get('github_token'):
        console.print("[red]Error: GitHub token not configured. Run 'skillmatch setup' first.[/red]")
        return
    
    # Load or create user profile
    if interactive:
        user_profile = await create_interactive_profile()
    else:
        try:
            profile_path = Path(profile)
            if not profile_path.exists():
                console.print(f"[yellow]Profile file not found. Creating sample profile at {profile}[/yellow]")
                # Create sample profile
                sample_profile = create_sample_user_profile()
                profile_path.parent.mkdir(parents=True, exist_ok=True)
                with open(profile_path, 'w') as f:
                    json.dump(sample_profile.dict(), f, indent=2, default=str)
                console.print(f"[green]Sample profile created at {profile}[/green]")
            
            with open(profile_path, 'r') as f:
                profile_data = json.load(f)
            user_profile = UserProfile(**profile_data)
        except Exception as e:
            console.print(f"[red]Error loading profile: {e}[/red]")
            return
    
    # Initialize agent
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Initializing SkillMatch AI...", total=None)
        
        try:
            agent = SkillMatchAgent(
                github_token=config['github_token'],
                model_id=config.get('model_id', 'openai/gpt-4.1-mini'),
                skills_db_path=config.get('skills_db_path', 'data/skills_database.json'),
                opportunities_db_path=config.get('opportunities_db_path', 'data/opportunities_database.json')
            )
            await agent.initialize()
            progress.update(task, description="✓ AI Agent ready")
        except Exception as e:
            console.print(f"[red]Error initializing agent: {e}[/red]")
            return
    
    console.print(f"\n[bold]Finding matches for: {user_profile.name}[/bold]")
    
    try:
        # Find matching opportunities
        profile_json = json.dumps(user_profile.dict(), default=str)
        matches_result = await agent.find_matching_opportunities(
            user_profile_json=profile_json,
            opportunity_types="job,project,learning",
            max_results=10
        )
        
        matches_data = json.loads(matches_result)
        
        if matches_data['status'] == 'success':
            display_matches(matches_data['matches'])
        else:
            console.print(f"[red]Error finding matches: {matches_data.get('message', 'Unknown error')}[/red]")
        
        # Offer to analyze specific match
        if matches_data['status'] == 'success' and matches_data['matches']:
            if Confirm.ask("\nWould you like to analyze a specific opportunity in detail?"):
                await analyze_specific_match(agent, user_profile, matches_data['matches'])
        
    except Exception as e:
        console.print(f"[red]Error during matching: {e}[/red]")
    
    finally:
        await agent.close()


@cli.command()
@click.option('--profile', default='profiles/sample_profile.json', help='User profile JSON file')
@click.option('--target-role', help='Target role to analyze gaps for')
@click.pass_context
async def gaps(ctx, profile, target_role):
    """Analyze skill gaps for career advancement"""
    config = ctx.obj['config']
    
    if not config.get('github_token'):
        console.print("[red]Error: GitHub token not configured. Run 'skillmatch setup' first.[/red]")
        return
    
    # Load user profile
    try:
        with open(profile, 'r') as f:
            profile_data = json.load(f)
        user_profile = UserProfile(**profile_data)
    except Exception as e:
        console.print(f"[red]Error loading profile: {e}[/red]")
        return
    
    # Initialize agent
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Analyzing skill gaps...", total=None)
        
        try:
            agent = SkillMatchAgent(
                github_token=config['github_token'],
                model_id=config.get('model_id', 'openai/gpt-4.1-mini'),
                skills_db_path=config.get('skills_db_path', 'data/skills_database.json'),
                opportunities_db_path=config.get('opportunities_db_path', 'data/opportunities_database.json')
            )
            await agent.initialize()
            progress.update(task, description="✓ Analysis complete")
        except Exception as e:
            console.print(f"[red]Error initializing agent: {e}[/red]")
            return
    
    try:
        # Analyze skill gaps
        profile_json = json.dumps(user_profile.dict(), default=str)
        gaps_result = await agent.identify_skill_gaps(
            user_profile_json=profile_json,
            target_role=target_role or ""
        )
        
        gaps_data = json.loads(gaps_result)
        
        if gaps_data['status'] == 'success':
            display_skill_gaps(gaps_data, target_role)
            
            # Get learning recommendations
            if gaps_data['skill_gaps']:
                recommendations_result = await agent.get_skill_recommendations(gaps_result)
                recommendations_data = json.loads(recommendations_result)
                
                if recommendations_data['status'] == 'success':
                    display_learning_recommendations(recommendations_data['recommendations'])
        else:
            console.print(f"[red]Error analyzing gaps: {gaps_data.get('message', 'Unknown error')}[/red]")
    
    except Exception as e:
        console.print(f"[red]Error during analysis: {e}[/red]")
    
    finally:
        await agent.close()


@cli.command()
@click.option('--skills', required=True, help='Comma-separated list of skills to learn')
@click.option('--difficulty', default='any', help='Preferred difficulty level')
@click.option('--max-cost', default=1000.0, help='Maximum cost for courses')
@click.pass_context
async def learn(ctx, skills, difficulty, max_cost):
    """Find learning opportunities for specific skills"""
    config = ctx.obj['config']
    
    if not config.get('github_token'):
        console.print("[red]Error: GitHub token not configured. Run 'skillmatch setup' first.[/red]")
        return
    
    # Initialize agent
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Searching learning opportunities...", total=None)
        
        try:
            agent = SkillMatchAgent(
                github_token=config['github_token'],
                model_id=config.get('model_id', 'openai/gpt-4.1-mini'),
                skills_db_path=config.get('skills_db_path', 'data/skills_database.json'),
                opportunities_db_path=config.get('opportunities_db_path', 'data/opportunities_database.json')
            )
            await agent.initialize()
            progress.update(task, description="✓ Search complete")
        except Exception as e:
            console.print(f"[red]Error initializing agent: {e}[/red]")
            return
    
    try:
        # Search learning opportunities
        learning_result = await agent.search_learning_opportunities(
            skills_to_learn=skills,
            difficulty_level=difficulty,
            max_cost=float(max_cost)
        )
        
        learning_data = json.loads(learning_result)
        
        if learning_data['status'] == 'success':
            display_learning_opportunities(learning_data)
        else:
            console.print(f"[red]Error searching opportunities: {learning_data.get('message', 'Unknown error')}[/red]")
    
    except Exception as e:
        console.print(f"[red]Error during search: {e}[/red]")
    
    finally:
        await agent.close()


@cli.command()
@click.pass_context
async def chat(ctx):
    """Interactive chat with SkillMatch AI"""
    config = ctx.obj['config']
    
    if not config.get('github_token'):
        console.print("[red]Error: GitHub token not configured. Run 'skillmatch setup' first.[/red]")
        return
    
    console.print(Panel.fit("SkillMatch.AI Interactive Chat", style="bold blue"))
    console.print("Type 'quit' or 'exit' to end the chat session.\n")
    
    # Initialize agent
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Starting chat session...", total=None)
        
        try:
            agent = SkillMatchAgent(
                github_token=config['github_token'],
                model_id=config.get('model_id', 'openai/gpt-4.1-mini'),
                skills_db_path=config.get('skills_db_path', 'data/skills_database.json'),
                opportunities_db_path=config.get('opportunities_db_path', 'data/opportunities_database.json')
            )
            await agent.initialize()
            progress.update(task, description="✓ Chat ready")
        except Exception as e:
            console.print(f"[red]Error initializing agent: {e}[/red]")
            return
    
    try:
        while True:
            user_input = Prompt.ask("[bold blue]You[/bold blue]")
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                console.print("[green]Goodbye![/green]")
                break
            
            with Progress(
                SpinnerColumn(),
                TextColumn("AI is thinking..."),
                console=console
            ) as progress:
                task = progress.add_task("Processing...", total=None)
                
                try:
                    response = await agent.chat(user_input)
                    progress.stop()
                    console.print(f"\n[bold green]SkillMatch AI:[/bold green] {response}\n")
                except Exception as e:
                    progress.stop()
                    console.print(f"[red]Error: {e}[/red]\n")
    
    except KeyboardInterrupt:
        console.print("\n[yellow]Chat session interrupted.[/yellow]")
    
    finally:
        await agent.close()


def display_matches(matches):
    """Display matching opportunities in a formatted table"""
    if not matches:
        console.print("[yellow]No matching opportunities found.[/yellow]")
        return
    
    table = Table(title="Matching Opportunities", show_header=True, header_style="bold magenta")
    table.add_column("Title", style="cyan", no_wrap=True)
    table.add_column("Type", style="green")
    table.add_column("Company", style="blue")
    table.add_column("Location", style="yellow")
    table.add_column("Match Score", style="red", justify="center")
    table.add_column("Skills Match", style="red", justify="center")
    
    for match in matches:
        table.add_row(
            match['title'][:30] + "..." if len(match['title']) > 30 else match['title'],
            match['type'].title(),
            match['company'][:20] + "..." if len(match['company']) > 20 else match['company'],
            match['location'][:15] + "..." if len(match['location']) > 15 else match['location'],
            f"{match['match_score']:.1%}",
            f"{match['skill_match']:.1%}"
        )
    
    console.print(table)
    
    # Display top match details
    if matches:
        console.print(f"\n[bold]Top Match Details:[/bold]")
        top_match = matches[0]
        console.print(f"📋 {top_match['title']}")
        console.print(f"🏢 {top_match['company']}")
        console.print(f"📍 {top_match['location']}")
        console.print(f"📊 Overall Match: {top_match['match_score']:.1%}")
        console.print(f"💡 {top_match['explanation']}")
        
        if top_match['strengths']:
            console.print(f"\n[green]✓ Your Strengths:[/green]")
            for strength in top_match['strengths'][:3]:
                console.print(f"  • {strength}")
        
        if top_match['skill_gaps']:
            console.print(f"\n[yellow]📚 Skills to Develop:[/yellow]")
            for gap in top_match['skill_gaps'][:3]:
                console.print(f"  • {gap['skill']} ({gap['current']} → {gap['required']})")


def display_skill_gaps(gaps_data, target_role):
    """Display skill gaps analysis"""
    console.print(f"\n[bold]Skill Gap Analysis[/bold]")
    if target_role:
        console.print(f"Target Role: {target_role}")
    
    if not gaps_data['skill_gaps']:
        console.print("[green]✓ No significant skill gaps identified![/green]")
        return
    
    table = Table(title="Skill Gaps to Address", show_header=True, header_style="bold magenta")
    table.add_column("Skill", style="cyan")
    table.add_column("Current Level", style="yellow")
    table.add_column("Required Level", style="green")
    table.add_column("Priority", style="red")
    table.add_column("Importance", justify="center")
    
    for gap in gaps_data['skill_gaps']:
        priority_color = {
            'High': 'red',
            'Medium': 'yellow', 
            'Low': 'green'
        }.get(gap['priority'], 'white')
        
        table.add_row(
            gap['skill'],
            gap['current_level'],
            gap['required_level'],
            f"[{priority_color}]{gap['priority']}[/{priority_color}]",
            f"{gap['importance']:.1%}"
        )
    
    console.print(table)


def display_learning_recommendations(recommendations):
    """Display learning recommendations"""
    console.print(f"\n[bold]📚 Learning Recommendations[/bold]")
    
    for rec in recommendations:
        console.print(f"\n[cyan]🎯 {rec['skill']}[/cyan]")
        console.print(f"   Current: {rec['current_level']} → Target: {rec['target_level']}")
        
        if rec['learning_opportunities']:
            console.print("   [blue]Learning Opportunities:[/blue]")
            for opp in rec['learning_opportunities']:
                cost_str = f"${opp['cost']}" if opp['cost'] > 0 else "Free"
                cert_str = "🏆" if opp['certification'] else ""
                console.print(f"     • {opp['title']} ({opp['provider']}) - {cost_str} {cert_str}")
        
        console.print(f"   [green]💡 Advice:[/green] {rec['general_advice']}")


def display_learning_opportunities(learning_data):
    """Display learning opportunities"""
    console.print(f"\n[bold]📚 Learning Opportunities[/bold]")
    console.print(f"Skills: {', '.join(learning_data['requested_skills'])}")
    console.print(f"Found: {learning_data['total_opportunities']} opportunities")
    
    if not learning_data['learning_opportunities']:
        console.print("[yellow]No learning opportunities found for the specified criteria.[/yellow]")
        return
    
    for opp in learning_data['learning_opportunities']:
        console.print(f"\n[cyan]📖 {opp['title']}[/cyan]")
        console.print(f"   Provider: {opp['provider']}")
        console.print(f"   Duration: {opp['duration']}")
        console.print(f"   Difficulty: {opp['difficulty']}")
        cost_str = f"${opp['cost']}" if opp['cost'] > 0 else "Free"
        cert_str = " 🏆 Certification" if opp['certification'] else ""
        console.print(f"   Cost: {cost_str}{cert_str}")
        console.print(f"   Skills: {', '.join(opp['skills_taught'])}")
        
        if opp['prerequisites']:
            console.print(f"   Prerequisites: {', '.join(opp['prerequisites'])}")


async def create_interactive_profile():
    """Create user profile interactively"""
    console.print(Panel.fit("Create Your Profile", style="bold blue"))
    
    # Basic info
    name = Prompt.ask("Your name")
    email = Prompt.ask("Email address")
    location = Prompt.ask("Location", default="")
    summary = Prompt.ask("Professional summary", default="")
    
    # Skills
    console.print("\n[bold]Add Your Skills[/bold]")
    skills = []
    
    while True:
        skill_name = Prompt.ask("Skill name (or 'done' to finish)", default="done")
        if skill_name.lower() == 'done':
            break
        
        # Try to find skill in database
        skill_id = skill_name.lower().replace(' ', '-').replace('.', '')
        
        level_options = ["beginner", "intermediate", "advanced", "expert"]
        console.print(f"Skill levels: {', '.join(f'{i+1}. {level}' for i, level in enumerate(level_options))}")
        level_choice = Prompt.ask("Choose skill level", choices=["1", "2", "3", "4"], default="2")
        level = level_options[int(level_choice) - 1]
        
        years = Prompt.ask("Years of experience", default="0")
        
        skill = SkillItem(
            skill_id=skill_id,
            skill_name=skill_name,
            category="programming",  # Default category
            level=ExperienceLevel(level),
            years_experience=float(years) if years else None
        )
        skills.append(skill)
        
        console.print(f"[green]✓ Added {skill_name} ({level})[/green]")
    
    # Preferences
    console.print("\n[bold]Set Your Preferences[/bold]")
    work_types = []
    if Confirm.ask("Interested in remote work?"):
        work_types.append(PreferenceType.REMOTE)
    if Confirm.ask("Interested in hybrid work?"):
        work_types.append(PreferenceType.HYBRID)
    if Confirm.ask("Interested in onsite work?"):
        work_types.append(PreferenceType.ONSITE)
    
    desired_roles = []
    while True:
        role = Prompt.ask("Desired job title (or 'done' to finish)", default="done")
        if role.lower() == 'done':
            break
        desired_roles.append(role)
    
    salary_min = Prompt.ask("Minimum salary expectation (USD)", default="0")
    locations = Prompt.ask("Preferred locations (comma-separated)", default="").split(',')
    locations = [loc.strip() for loc in locations if loc.strip()]
    
    preferences = UserPreferences(
        work_type=work_types,
        desired_roles=desired_roles,
        salary_min=float(salary_min) if salary_min != "0" else None,
        locations=locations
    )
    
    profile = UserProfile(
        user_id="interactive_user",
        name=name,
        email=email,
        location=location,
        summary=summary,
        skills=skills,
        preferences=preferences
    )
    
    console.print("[green]✓ Profile created successfully![/green]")
    return profile


async def analyze_specific_match(agent, user_profile, matches):
    """Analyze a specific opportunity in detail"""
    console.print("\n[bold]Available opportunities:[/bold]")
    for i, match in enumerate(matches[:5], 1):
        console.print(f"{i}. {match['title']} ({match['company']})")
    
    choice = Prompt.ask(
        "Select opportunity to analyze",
        choices=[str(i) for i in range(1, min(6, len(matches) + 1))]
    )
    
    selected_match = matches[int(choice) - 1]
    opportunity_id = selected_match['opportunity_id']
    
    with Progress(
        SpinnerColumn(),
        TextColumn("Analyzing opportunity..."),
        console=console
    ) as progress:
        task = progress.add_task("Processing...", total=None)
        
        profile_json = json.dumps(user_profile.dict(), default=str)
        analysis_result = await agent.calculate_match_score(
            user_profile_json=profile_json,
            opportunity_id=opportunity_id
        )
    
    analysis_data = json.loads(analysis_result)
    
    if analysis_data['status'] == 'success':
        console.print(f"\n[bold]Detailed Analysis: {analysis_data['opportunity_title']}[/bold]")
        console.print(f"Overall Score: {analysis_data['overall_score']:.1%}")
        console.print(f"Skill Match: {analysis_data['skill_match_score']:.1%}")
        console.print(f"Experience Match: {analysis_data['experience_score']:.1%}")
        console.print(f"Preference Match: {analysis_data['preference_score']:.1%}")
        console.print(f"\n{analysis_data['explanation']}")
        
        if analysis_data.get('recommendations'):
            console.print(f"\n[green]📋 Recommendations:[/green]")
            for rec in analysis_data['recommendations']:
                console.print(f"  • {rec}")




def main():
    """Main entry point that handles async CLI commands"""
    # Store original async callbacks
    original_match = match.callback
    original_gaps = gaps.callback
    original_learn = learn.callback  
    original_chat = chat.callback
    
    # Create sync wrappers for async commands
    def make_sync(async_callback):
        def sync_func(*args, **kwargs):
            return asyncio.run(async_callback(*args, **kwargs))
        return sync_func
    
    # Replace the callbacks with sync versions
    match.callback = make_sync(original_match)
    gaps.callback = make_sync(original_gaps)
    learn.callback = make_sync(original_learn)
    chat.callback = make_sync(original_chat)
    
    cli()


if __name__ == '__main__':
    main()
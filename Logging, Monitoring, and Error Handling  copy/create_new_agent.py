#!/usr/bin/env python3
"""
Agent Generator Script

This script generates a new agent based on the test agent template.
It creates the necessary files for a new agent with customized parameters.
"""

import os
import sys
import argparse
import shutil
from datetime import datetime

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Generate a new agent based on the test agent template.')
    parser.add_argument('agent_name', help='Name of the new agent (e.g., research_agent)')
    parser.add_argument('--port', type=int, default=8002, help='Port for the metrics server (default: 8002)')
    parser.add_argument('--skills', nargs='+', default=['skill_1', 'skill_2'], help='List of skills for the agent (default: skill_1 skill_2)')
    parser.add_argument('--output-dir', default='.', help='Output directory for the new agent files (default: current directory)')
    return parser.parse_args()

def create_agent_file(args):
    """Create the new agent Python file."""
    agent_file_path = os.path.join(args.output_dir, f"{args.agent_name}.py")
    
    # Read the test agent file
    with open('test_agent.py', 'r') as f:
        content = f.read()
    
    # Replace the agent name, type, and port
    content = content.replace('test_agent', args.agent_name)
    content = content.replace('test_agent_1', f"{args.agent_name}_1")
    content = content.replace('test_skill_1', args.skills[0])
    content = content.replace('test_skill_2', args.skills[1] if len(args.skills) > 1 else args.skills[0])
    content = content.replace('AGENT_PORT = 8001', f'AGENT_PORT = {args.port}')
    
    # Add a generation comment
    generation_comment = f"""#!/usr/bin/env python3
\"\"\"
{args.agent_name.replace('_', ' ').title()}

This agent was generated from the test agent template on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.
It demonstrates how to integrate with the central logging, monitoring, and error handling infrastructure.
\"\"\"

"""
    content = generation_comment + content[content.find('import'):]
    
    # Write the new agent file
    with open(agent_file_path, 'w') as f:
        f.write(content)
    
    # Make the file executable
    os.chmod(agent_file_path, 0o755)
    
    return agent_file_path

def create_dockerfile(args):
    """Create a Dockerfile for the new agent."""
    dockerfile_path = os.path.join(args.output_dir, f"Dockerfile.{args.agent_name}")
    
    # Read the test agent Dockerfile
    with open('Dockerfile.test_agent', 'r') as f:
        content = f.read()
    
    # Replace the agent name and port
    content = content.replace('test_agent.py', f"{args.agent_name}.py")
    content = content.replace('EXPOSE 8001', f'EXPOSE {args.port}')
    
    # Write the new Dockerfile
    with open(dockerfile_path, 'w') as f:
        f.write(content)
    
    return dockerfile_path

def create_run_script(args):
    """Create a run script for the new agent."""
    run_script_path = os.path.join(args.output_dir, f"run_{args.agent_name}.sh")
    
    # Read the test agent run script
    with open('run_test_agent.sh', 'r') as f:
        content = f.read()
    
    # Replace the agent name
    content = content.replace('Test Agent', f"{args.agent_name.replace('_', ' ').title()}")
    content = content.replace('test_agent.py', f"{args.agent_name}.py")
    content = content.replace('test agent', args.agent_name.replace('_', ' '))
    
    # Write the new run script
    with open(run_script_path, 'w') as f:
        f.write(content)
    
    # Make the file executable
    os.chmod(run_script_path, 0o755)
    
    return run_script_path

def main():
    """Main function."""
    args = parse_arguments()
    
    # Create output directory if it doesn't exist
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)
    
    # Create the agent files
    agent_file = create_agent_file(args)
    dockerfile = create_dockerfile(args)
    run_script = create_run_script(args)
    
    print(f"=== New Agent Created: {args.agent_name} ===")
    print(f"Agent file: {agent_file}")
    print(f"Dockerfile: {dockerfile}")
    print(f"Run script: {run_script}")
    print("")
    print("To run the agent:")
    print(f"  ./{os.path.basename(run_script)}")
    print("")
    print("To build and run the agent in Docker:")
    print(f"  docker build -t {args.agent_name} -f {os.path.basename(dockerfile)} .")
    print(f"  docker run --name {args.agent_name} --network logging-network -p {args.port}:{args.port} {args.agent_name}")
    print("")
    print("Remember to customize the agent's functionality in the agent file.")

if __name__ == "__main__":
    main()

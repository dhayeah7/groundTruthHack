#!/usr/bin/env python3
import subprocess
import os

# Set environment with Node 20 first in PATH
env = os.environ.copy()
env['PATH'] = '/opt/homebrew/bin:/opt/homebrew/opt/node@20/bin:' + env.get('PATH', '')

# Change to frontend directory and run npm
os.chdir('/Users/dayamahesh/gtHack/nike-ai-chat')

# Run npm dev server
subprocess.run(['npm', 'run', 'dev'], env=env)

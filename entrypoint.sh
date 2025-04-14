#!/bin/bash

echo "Welcome to AgentMesh!"
echo "Available commands:"
echo "  list    - List available teams (python main.py -l)"
echo "  run     - Run a specific team (python main.py -t TEAM_NAME)"
echo "  help    - Show this help message"
echo "  exit    - Exit the container"
echo ""

while true; do
  read -p "agentmesh> " cmd args
  
  case "$cmd" in
    list)
      python main.py -l
      ;;
    run)
      if [ -z "$args" ]; then
        echo "Error: Please specify a team name"
        echo "Usage: run TEAM_NAME"
      else
        python main.py -t $args
      fi
      ;;
    help)
      echo "Available commands:"
      echo "  list    - List available teams"
      echo "  run     - Run a specific team (run TEAM_NAME)"
      echo "  help    - Show this help message"
      echo "  exit    - Exit the container"
      ;;
    exit)
      echo "Goodbye!"
      exit 0
      ;;
    *)
      if [ -n "$cmd" ]; then
        echo "Unknown command: $cmd"
        echo "Type 'help' for available commands"
      fi
      ;;
  esac
done 
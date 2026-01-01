# Agent Memory System for CAMEO

## Overview
This system stores and retrieves contextual information about the CAMEO chemical safety platform for the AI agent.

## Memory Structure

### Project Context
- **Project Type**: Chemical Safety Platform (HSE Dashboard)
- **Technology Stack**: Flask + React + Vite + SQLite
- **Architecture**: Backend API + Frontend SPA
- **Database**: SQLite (chemicals.db, user.db)

### Key Components
- **Backend**: Flask app with chemical search, compatibility analysis
- **Frontend**: React app with enterprise-grade UI
- **Database**: Chemical data, reactivity rules, user data
- **UI Framework**: Tailwind CSS + Alpine.js

### Critical Files & Locations
- `backend/app.py` - Main Flask application
- `backend/templates/mixer.html` - Chemical compatibility interface
- `backend/logic/reactivity_engine.py` - Core compatibility logic
- `backend/data/chemicals.db` - Chemical database
- `src/App.tsx` - React frontend entry point

### Recent Changes
- Enterprise UI overhaul completed
- Reactivity engine implemented
- Database schema finalized
- GitHub integration active (behnoodghza-design/CAMEO)

## Memory Usage Guidelines
1. Check memory before making structural changes
2. Update memory after significant modifications
3. Store architectural decisions
4. Track API endpoint changes
5. Document database schema modifications

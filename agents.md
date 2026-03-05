# Agents Instructions

## Project Overview

This is a Weather Agent project with three layers:
- **MCP Server** (`mcp-server/`) - Microservice wrapper for OpenWeatherMap API with LFU caching
- **Agent Backend** (`backend/`) - LangChain-powered LLM agent with tool calling (Anthropic Claude)
- **React Frontend** (`frontend/`) - Chat interface with tabbed navigation

## Frontend Tab Structure

The frontend has the following tabs, each rendered by its own component in `frontend/src/components/`:

| Tab | Component | Purpose |
|-----|-----------|---------|
| Chat | `ChatInterface.jsx` | Live chat with the weather agent |
| Help | `HelpPanel.jsx` | Usage guide and example queries |
| Architecture | `ArchitecturePanel.jsx` | System architecture and design decisions |
| Agent | `AgentPanel.jsx` | Agent internals, tool calling, and LLM details |
| Experience | `ExperiencePanel.jsx` | UX decisions and user experience notes |
| Improvements | `ImprovementsPanel.jsx` | Planned and completed improvements |
| Deployment | `DeploymentPanel.jsx` | Deployment instructions and configuration |

## Documentation Philosophy

This project follows a strict documentation-first philosophy. Every agent working on this codebase must adhere to these principles:

### 1. Document Every Change
All changes — features, bug fixes, refactors, config updates — must be documented. No change is too small to skip documentation. If it touched the code, it gets documented.

### 2. Document the Reason, Not Just the What
Every change must include **why** it was made, not just what was changed. Future developers need historical context to understand decisions. When updating frontend tabs or code comments, always include the motivation and reasoning behind the change so that the intent is never lost.

### 3. Comment Exceptions and Non-Obvious Code
Any exception handling, edge-case logic, workarounds, or intentional deviations from the norm **must** have a code comment explaining why it exists. These comments act as guardrails — they prevent future developers (or agents) from removing code that looks unnecessary but actually serves a critical purpose. Mark these clearly so they are not mistaken for dead code.

### 4. Frontend Tabs Are the Living Documentation
The frontend tabs are not static docs — they are the **single source of truth** for any new or collaborating developer joining the project. They must always reflect the latest state of the system. A developer should be able to read through the tabs and fully understand the current architecture, agent behavior, deployment setup, and improvement history without reading a single line of backend code.

---

## Critical Rule: Keep Frontend Tabs in Sync

**Every improvement, bug fix, or code change MUST be reflected in the relevant frontend tab.**

When making changes, follow this checklist:

1. **Architecture changes** (new services, API changes, caching, data flow) - Update `ArchitecturePanel.jsx`
2. **Agent/LLM changes** (model swap, new tools, prompt changes, chain modifications) - Update `AgentPanel.jsx`
3. **UX/UI changes** (new components, styling, interaction patterns) - Update `ExperiencePanel.jsx`
4. **Bug fixes, optimizations, new features** - Update `ImprovementsPanel.jsx`
5. **Deployment/infra changes** (env vars, Docker, CI/CD, hosting) - Update `DeploymentPanel.jsx`
6. **New user-facing capabilities or usage patterns** - Update `HelpPanel.jsx`

If a change spans multiple areas, update all relevant tabs.

## Workflow

1. Make the code change
2. Identify which tab(s) the change relates to
3. Update the corresponding panel component(s) to document the change
4. Verify the frontend renders correctly

# Agents

This document describes the AI agents used in the development and maintenance of `mdutil`.

## Useful documents

### Specifications and Design

The mdutil-specification.md document contains the design specifics of the tool.

### Other useful information

- The README.md document contains useful information for the user, which ranges from how to compile the tool, as well as other information (history, etc.).
- The LICENSE file contains the FLOSS license under which this tool is been released.

## Overview

The agents listed below are used to assist with tasks such as code generation, documentation, testing, and bug fixing.

## Agent Roles

### 1. Developer Agent
- **Role**: Primary coding assistant.
- **Responsibilities**:
  - Writing and refactoring code.
  - Implementing new features.
  - Writing unit tests.
- **Context/Instructions**: Follows the project's coding standards and architecture.

### 2. Reviewer Agent
- **Role**: Code quality and security auditor.
- **Responsibilities**:
  - Reviewing pull requests.
  - Identifying potential security vulnerabilities.
  - Checking for compliance with style guides.

### 3. Documentation Agent
- **Role**: Documentation maintainer.
- **Responsibilities**:
  - Updating `README.md`.
  - Generating API documentation.
  - Maintaining the `docs/` folder.

## Guidelines for Interacting with Agents

- **Clarity**: Be specific in instructions to avoid ambiguity.
- **Context**: Provide necessary file contents or error logs when reporting bugs.
- **Verification**: Always manually verify the outputs of agents before committing changes.

### Git Branching Policy

**Never work directly on the `main` branch.** The `main` branch is protected and can only be updated via a Pull Request.

Always follow this pattern:
1. Check if you're on a named branch
2. If not, create one before doing any work
3. Use naming templates:
   - Features: `feature/branchname` (e.g., `feature/mermaid-export`)
   - Bug fixes: `bugfix/branchname` (e.g., `bugfix/html-table-rendering`)

This ensures clean history and proper code review workflow.

### Pull Request Conventions

**Be terse with PR name/description.** Put all details in the Summary field.

- PR name: Short, descriptive title (one line)
- PR description: Terse bullet points or "See Summary"
- Summary field: Full details, context, testing notes, release checklist

The current PR template renders description text as H1, making large blobs of text unwieldy. Keep it concise in the description, expand in the Summary.

## Configuration and Prompts

(Optional: Information on where system prompts or agent configurations are stored.)

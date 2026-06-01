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

## Configuration and Prompts

(Optional: Information on where system prompts or agent configurations are stored.)

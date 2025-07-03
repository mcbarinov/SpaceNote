# Task Tracker

A comprehensive task management system for teams to track work items, assign responsibilities, and monitor progress.

## Overview

The Task Tracker space is designed for project management and task coordination. It allows teams to:
- Create and manage tasks with detailed descriptions
- Assign tasks to team members
- Set priorities and track status
- Use tags for organization
- Filter and view tasks by various criteria

## Space Configuration

**Download**: [task-tracker.json](json/task-tracker.json) - Complete space configuration ready for import

**Members**: alice, bob, charlie

**Fields**:
- **title** (string, required): Task title/summary
- **body** (markdown, optional): Detailed task description
- **assignee** (user, required): Person responsible for the task
- **priority** (choice, optional): Task priority level (low, medium, high)
  - Default: medium
- **open** (boolean, required): Whether the task is still open
  - Default: true
- **paused** (boolean, optional): Whether the task is temporarily paused
  - Default: false
- **tags** (tags, optional): Categorization labels

**List View**: Shows title, assignee, open status, paused status, and tags

**Create Form**: Hides open and paused fields (automatically set to defaults)

## Filters

**Active Tasks**:
- Shows tasks that are open and not paused
- Sorted by creation date (newest first)
- Displays: title, tags, assignee, priority, open status

**My Tasks**:
- Shows open tasks assigned to the current user
- Sorted by creation date (newest first)
- Displays: title, priority, tags

## Example Records

### Task 1: Bug Fix
```json
{
  "title": "Fix login page validation",
  "body": "The email validation on the login page is not working correctly. Users can submit invalid email addresses.\n\n**Steps to reproduce:**\n1. Go to login page\n2. Enter invalid email\n3. Click submit\n\n**Expected:** Error message should appear\n**Actual:** Form submits successfully",
  "assignee": "bob",
  "priority": "high",
  "open": true,
  "paused": false,
  "tags": ["bug", "frontend", "urgent"]
}
```

### Task 2: Feature Development
```json
{
  "title": "Implement user profile settings",
  "body": "Add a settings page where users can:\n- Update their profile information\n- Change password\n- Configure notification preferences\n- Upload avatar image",
  "assignee": "charlie",
  "priority": "medium",
  "open": true,
  "paused": false,
  "tags": ["feature", "backend", "frontend"]
}
```

### Task 3: Documentation
```json
{
  "title": "Update API documentation",
  "body": "Review and update the API documentation to reflect recent changes in the authentication endpoints.",
  "assignee": "alice",
  "priority": "low",
  "open": false,
  "paused": false,
  "tags": ["documentation", "api"]
}
```

### Task 4: Research Task
```json
{
  "title": "Research authentication libraries",
  "body": "Evaluate different authentication libraries for the new security requirements:\n- OAuth 2.0 support\n- Multi-factor authentication\n- Session management\n- Integration difficulty",
  "assignee": "bob",
  "priority": "medium",
  "open": true,
  "paused": true,
  "tags": ["research", "security", "backend"]
}
```

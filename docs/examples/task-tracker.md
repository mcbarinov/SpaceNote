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
- **status** (choice, required): Current task state (new, in_progress, paused, completed, cancelled)
  - Default: new
- **tags** (tags, optional): Categorization labels

**List View**: Shows title, assignee, status, and tags

**Create Form**: Hides status field (automatically set to "new")

## Filters

**Active Tasks**:
- Shows tasks with status "new" or "in_progress"
- Sorted by creation date (newest first)
- Displays: title, tags, assignee, priority, status

**My Tasks**:
- Shows tasks assigned to the current user that are not completed
- Sorted by creation date (newest first)
- Displays: title, priority, status, tags

## Example Records

### Task 1: Bug Fix
```json
{
  "title": "Fix login page validation",
  "body": "The email validation on the login page is not working correctly. Users can submit invalid email addresses.\n\n**Steps to reproduce:**\n1. Go to login page\n2. Enter invalid email\n3. Click submit\n\n**Expected:** Error message should appear\n**Actual:** Form submits successfully",
  "assignee": "bob",
  "priority": "high",
  "status": "new",
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
  "status": "in_progress",
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
  "status": "completed",
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
  "status": "paused",
  "tags": ["research", "security", "backend"]
}
```

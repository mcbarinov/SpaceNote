#!/usr/bin/env python3
"""
Demo data generator for Task Tracker space.

This script creates a Task Tracker space with realistic demo data including:
- User creation (alice, bob, charlie + admin)
- Space setup with fields and filters
- Generated tasks with various priorities and statuses
- Comments on tasks for discussion simulation

Usage:
    python scripts/demo/task_tracker.py [--records 200] [--max-comments 20]
"""

import argparse
import asyncio
import contextlib
import json
import random
from pathlib import Path
from typing import Any

from spacenote.core.app import App
from spacenote.core.config import CoreConfig
from spacenote.core.field.models import SpaceField
from spacenote.core.filter.models import Filter
from spacenote.core.user.models import User


class TaskTrackerGenerator:
    def __init__(self, app: App, admin_user: User, records: int = 200, max_comments: int = 20) -> None:
        self.app = app
        self.admin_user = admin_user
        self.records = records
        self.max_comments = max_comments
        self.space_id = ""
        self.members = []

    async def generate(self) -> None:
        """Generate the complete Task Tracker demo space with data."""
        print("🚀 Starting Task Tracker demo generation...")

        # Load space configuration
        config = self._load_space_config()

        # Create users
        await self._create_users(config["members"])

        # Create and configure space
        await self._create_space(config)

        # Generate demo data
        await self._generate_tasks()

        print(f"✅ Task Tracker demo completed!")
        print(f"   Space ID: {self.space_id}")
        print(f"   Members: {', '.join(self.members)}")
        print(f"   Records: {self.records}")
        print(f"   Max comments per task: {self.max_comments}")

    def _load_space_config(self) -> dict[str, Any]:
        """Load space configuration from JSON file."""
        config_path = Path(__file__).parent.parent.parent / "docs" / "examples" / "json" / "task-tracker.json"

        if not config_path.exists():
            raise FileNotFoundError(f"Space configuration not found: {config_path}")

        with config_path.open() as f:
            return json.load(f)

    async def _create_users(self, members: list[str]) -> None:
        """Create users if they don't exist and ensure admin is in members."""
        print("👥 Creating users...")

        # Always include admin in members
        if "admin" not in members:
            members.append("admin")

        existing_users = {user.id for user in self.app.get_users(self.admin_user)}

        for username in members:
            if username not in existing_users:
                await self.app.create_user(self.admin_user, username, "password123")
                print(f"   Created user: {username}")
            else:
                print(f"   User exists: {username}")

        self.members = members

    async def _create_space(self, config: dict[str, Any]) -> None:
        """Create space with configuration from JSON."""
        print("🏢 Creating space...")

        # Find unique space ID
        base_id = config["_id"]
        space_id = base_id
        suffix = 1

        existing_spaces = {space.id for space in self.app.get_all_spaces(self.admin_user)}

        while space_id in existing_spaces:
            suffix += 1
            space_id = f"{base_id}-{suffix}"

        self.space_id = space_id

        # Create space
        await self.app.create_space(self.admin_user, space_id, config["name"])
        print(f"   Created space: {space_id}")

        # Add members
        await self._update_space_members()

        # Configure fields
        await self._configure_fields(config["fields"])

        # Configure list fields
        await self.app.update_list_fields(self.admin_user, space_id, config["list_fields"])

        # Configure hidden create fields
        await self.app.update_hidden_create_fields(self.admin_user, space_id, config["hidden_create_fields"])

        # Add filters
        await self._add_filters(config["filters"])

        print(f"   Space configured successfully")

    async def _update_space_members(self) -> None:
        """Update space members to include all demo users."""
        await self.app.update_space_members(self.admin_user, self.space_id, self.members)
        print(f"   Members updated: {', '.join(self.members)}")

    async def _configure_fields(self, fields_config: list[dict[str, Any]]) -> None:
        """Configure space fields from JSON configuration."""
        for field_config in fields_config:
            field = SpaceField(**field_config)
            await self.app.add_field(self.admin_user, self.space_id, field)

    async def _add_filters(self, filters_config: list[dict[str, Any]]) -> None:
        """Add filters from JSON configuration."""
        for filter_config in filters_config:
            filter_obj = Filter(**filter_config)
            await self.app.add_filter(self.admin_user, self.space_id, filter_obj)

    async def _generate_tasks(self) -> None:
        """Generate realistic task data."""
        print(f"📝 Generating {self.records} tasks...")

        task_templates = self._get_task_templates()
        priorities = ["low", "medium", "high"]
        statuses = ["new", "in_progress", "paused", "completed", "cancelled"]
        # Weight distribution: more new/in_progress tasks, fewer completed/cancelled
        status_weights = [0.4, 0.3, 0.1, 0.15, 0.05]

        for i in range(self.records):
            # Select random template and customize
            template = random.choice(task_templates)

            # Customize task
            status = random.choices(statuses, weights=status_weights)[0]
            task_data = {
                "title": template["title"].format(i=i + 1),
                "body": template["body"],
                "assignee": random.choice(self.members),
                "priority": random.choices(priorities, weights=[0.3, 0.5, 0.2])[0],
                "status": status,
                "tags": ",".join(random.sample(template["tags"], k=random.randint(1, min(3, len(template["tags"]))))),
            }

            # Create task
            note = await self.app.create_note_from_raw_fields(self.admin_user, self.space_id, task_data)

            # Add comments
            await self._add_comments(note.id)

            if (i + 1) % 50 == 0:
                print(f"   Generated {i + 1} tasks...")

    async def _add_comments(self, note_id: int) -> None:
        """Add random comments to a task."""
        num_comments = random.randint(0, self.max_comments)

        comment_templates = [
            "Started working on this task",
            "Found the issue, investigating further",
            "This is more complex than expected",
            "Need help with the implementation",
            "Testing the solution now",
            "Ready for review",
            "Deployed to staging",
            "Looks good, closing this task",
            "Reopening due to new requirements",
            "Added documentation",
            "Fixed the bug, needs verification",
            "Merged the PR",
        ]

        for _ in range(num_comments):
            comment = random.choice(comment_templates)

            # Note: This assumes admin can create comments as any user
            # May need to be modified based on actual comment API
            with contextlib.suppress(Exception):
                await self.app.create_comment(self.admin_user, self.space_id, note_id, comment)

    def _get_task_templates(self) -> list[dict[str, Any]]:
        """Get realistic task templates for generation."""
        return [
            {
                "title": "Fix login validation bug #{i}",
                "body": (
                    "The login form validation is not working correctly. Users can submit invalid credentials.\n\n"
                    "**Steps to reproduce:**\n1. Go to login page\n2. Enter invalid data\n3. Submit form\n\n"
                    "**Expected:** Show validation error\n**Actual:** Form submits"
                ),
                "tags": ["bug", "frontend", "auth", "validation"],
            },
            {
                "title": "Implement user profile page #{i}",
                "body": (
                    "Create a user profile page where users can:\n- View their information\n- Edit profile details\n"
                    "- Change password\n- Upload avatar\n\n**Acceptance criteria:**\n- Mobile responsive design\n"
                    "- Form validation\n- Image upload functionality"
                ),
                "tags": ["feature", "frontend", "profile", "ui"],
            },
            {
                "title": "Add API endpoint for data export #{i}",
                "body": (
                    "Create REST API endpoint to export user data in JSON format.\n\n**Requirements:**\n"
                    "- Authentication required\n- Rate limiting\n- Data filtering options\n- CSV and JSON formats\n\n"
                    "**Estimated effort:** 3-5 hours"
                ),
                "tags": ["feature", "backend", "api", "export"],
            },
            {
                "title": "Update documentation for new features #{i}",
                "body": (
                    "Update the API documentation to reflect recent changes:\n- New endpoints\n- Changed parameters\n"
                    "- Authentication updates\n- Code examples\n\n**Files to update:**\n- README.md\n- API.md\n"
                    "- Installation guide"
                ),
                "tags": ["documentation", "api", "maintenance"],
            },
            {
                "title": "Research database optimization #{i}",
                "body": (
                    "Investigate database performance issues:\n- Slow queries identification\n- Index optimization\n"
                    "- Query optimization\n- Connection pooling\n\n**Deliverables:**\n- Performance analysis report\n"
                    "- Optimization recommendations\n- Implementation plan"
                ),
                "tags": ["research", "database", "performance", "optimization"],
            },
            {
                "title": "Fix CSS styling issues #{i}",
                "body": (
                    "Several CSS styling issues reported:\n- Button alignment on mobile\n- Text overflow in containers\n"
                    "- Color contrast issues\n- Responsive breakpoints\n\n**Affected pages:**\n- Dashboard\n"
                    "- Settings\n- Profile page"
                ),
                "tags": ["bug", "frontend", "css", "ui", "mobile"],
            },
            {
                "title": "Implement email notifications #{i}",
                "body": (
                    "Add email notification system:\n- Welcome emails\n- Password reset\n- Activity notifications\n"
                    "- Weekly digest\n\n**Technical requirements:**\n- Email templates\n- Queue system\n"
                    "- Unsubscribe functionality\n- Testing framework"
                ),
                "tags": ["feature", "backend", "email", "notifications"],
            },
            {
                "title": "Security audit and fixes #{i}",
                "body": (
                    "Conduct security review and fix issues:\n- SQL injection prevention\n- XSS protection\n"
                    "- CSRF tokens\n- Input validation\n- Rate limiting\n\n**Priority:** High\n**Deadline:** End of sprint"
                ),
                "tags": ["security", "audit", "backend", "frontend", "critical"],
            },
        ]


async def main() -> None:
    """Main function to run the demo generator."""
    parser = argparse.ArgumentParser(description="Generate Task Tracker demo data")
    parser.add_argument("--records", type=int, default=200, help="Number of tasks to generate")
    parser.add_argument("--max-comments", type=int, default=20, help="Maximum comments per task")

    args = parser.parse_args()

    # Initialize app
    config = CoreConfig()
    app = App(config)

    async with app.lifespan():
        # Login as admin
        session_id = await app.login("admin", "admin")
        if not session_id:
            print("❌ Failed to login as admin")
            return

        admin_user = await app.get_user_by_session(session_id)
        if not admin_user:
            print("❌ Failed to get admin user")
            return

        # Generate demo data
        generator = TaskTrackerGenerator(app, admin_user, args.records, args.max_comments)
        await generator.generate()


if __name__ == "__main__":
    asyncio.run(main())

"""Slash commands handler for QChat.

Provides Discord-style slash commands for fun interactions and utilities.
"""

import random
from dataclasses import dataclass
from typing import Callable, Optional

from qchat.gui.effects import dizzy, flick_of_the_wrist, wizz


@dataclass
class SlashCommandResult:
    """Result of a slash command execution."""

    success: bool
    message_text: Optional[str] = None  # Text to send to chat
    local_action: Optional[Callable] = None  # Local action to execute
    error: Optional[str] = None


class SlashCommandHandler:
    """Handler for slash commands in QChat."""

    # Magic 8-ball responses (classic answers)
    EIGHT_BALL_RESPONSES = [
        "It is certain",
        "It is decidedly so",
        "Without a doubt",
        "Yes definitely",
        "You may rely on it",
        "As I see it, yes",
        "Most likely",
        "Outlook good",
        "Yes",
        "Signs point to yes",
        "Reply hazy, try again",
        "Ask again later",
        "Better not tell you now",
        "Cannot predict now",
        "Concentrate and ask again",
        "Don't count on it",
        "My reply is no",
        "My sources say no",
        "Outlook not so good",
        "Very doubtful",
    ]

    # Command descriptions for help/autocomplete
    COMMAND_DESCRIPTIONS = {
        "list": "List all available commands",
        "shrug": "Send ¯\\_(ツ)_/¯",
        "tableflip": "Send (╯°□°)╯︵ ┻━┻",
        "lenny": "Send ( ͡° ͜ʖ ͡°)",
        "yolo": "Convert message to UPPERCASE + 🎲",
        "flip": "Flip a coin (heads or tails)",
        "roll": "Roll dice (e.g. /roll 2d20)",
        "8ball": "Ask the magic 8-ball",
        "dizz": "Let QGIS shake",
        "flick": "Look at QGIS flicking the wrist",
        "wizz": "Make the entire QGIS application shake like MSN effect",
    }

    def __init__(self):
        """Initialize the slash command handler."""
        self.commands = {
            "list": self.cmd_list,
            "shrug": self.cmd_shrug,
            "tableflip": self.cmd_tableflip,
            "lenny": self.cmd_lenny,
            "yolo": self.cmd_yolo,
            "flip": self.cmd_flip,
            "roll": self.cmd_roll,
            "8ball": self.cmd_8ball,
            "dizz": self.cmd_dizz,
            "flick": self.cmd_flick,
            "wizz": self.cmd_wizz,
        }

    def get_command_list(self) -> list[str]:
        """Get list of available commands (for autocomplete).

        :return: list of command names with leading /
        """
        return [f"/{cmd}" for cmd in sorted(self.commands.keys())]

    def is_command(self, text: str) -> bool:
        """Check if the text is a slash command.

        :param text: text to check
        :return: True if text starts with /
        """
        return text.strip().startswith("/")

    def execute(self, text: str) -> SlashCommandResult:
        """Execute a slash command.

        :param text: command text (e.g., "/shrug" or "/roll")
        :return: SlashCommandResult with the result
        """
        text = text.strip()
        if not self.is_command(text):
            return SlashCommandResult(success=False, error="Not a command")

        # Parse command and arguments
        parts = text[1:].split(maxsplit=1)  # Remove leading /
        command = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""

        # Execute command
        if command in self.commands:
            return self.commands[command](args)
        else:
            return SlashCommandResult(
                success=False,
                error=f"Unknown command: /{command}",
            )

    def cmd_shrug(self, args: str) -> SlashCommandResult:
        """Shrug command: ¯\\_(ツ)_/¯

        :param args: optional message after shrug
        :return: SlashCommandResult
        """
        message = "¯\\_(ツ)_/¯"
        if args:
            message = f"{message} {args}"
        return SlashCommandResult(success=True, message_text=message)

    def cmd_tableflip(self, args: str) -> SlashCommandResult:
        """Table flip command: (╯°□°)╯︵ ┻━┻

        :param args: optional message after tableflip
        :return: SlashCommandResult
        """
        message = "(╯°□°)╯︵ ┻━┻"
        if args:
            message = f"{message} {args}"
        return SlashCommandResult(success=True, message_text=message)

    def cmd_lenny(self, args: str) -> SlashCommandResult:
        """Lenny face command: ( ͡° ͜ʖ ͡°)

        :param args: optional message after lenny
        :return: SlashCommandResult
        """
        message = "( ͡° ͜ʖ ͡°)"
        if args:
            message = f"{message} {args}"
        return SlashCommandResult(success=True, message_text=message)

    def cmd_yolo(self, args: str) -> SlashCommandResult:
        """YOLO command: converts message to CAPS + emoji

        :param args: message to yolo-fy
        :return: SlashCommandResult
        """
        if not args:
            message = "YOLO! 🎲"
        else:
            message = f"{args.upper()} 🎲"
        return SlashCommandResult(success=True, message_text=message)

    def cmd_flip(self, args: str) -> SlashCommandResult:
        """Coin flip command: heads or tails

        :param args: unused
        :return: SlashCommandResult
        """
        result = random.choice(["Heads", "Tails"])
        emoji = "🪙"
        message = f"{emoji} {result}!"
        return SlashCommandResult(success=True, message_text=message)

    def cmd_roll(self, args: str) -> SlashCommandResult:
        """Dice roll command: 1-6

        :param args: optional dice specification (e.g., "2d20" for 2 dice of 20 sides)
        :return: SlashCommandResult
        """
        # Parse args for custom dice (e.g., "2d20")
        num_dice = 1
        num_sides = 6

        if args:
            try:
                if "d" in args.lower():
                    parts = args.lower().split("d")
                    num_dice = int(parts[0]) if parts[0] else 1
                    num_sides = int(parts[1]) if parts[1] else 6
                else:
                    num_sides = int(args)
            except (ValueError, IndexError):
                return SlashCommandResult(
                    success=False,
                    error="Invalid format. Use /roll [faces] or /roll [number]d[faces]",
                )

        # Validate
        if num_dice < 1 or num_dice > 100:
            return SlashCommandResult(
                success=False, error="Invalid number of dice [1-100]"
            )
        if num_sides < 2 or num_sides > 1000:
            return SlashCommandResult(
                success=False, error="Invalid number of sides (2-1000)"
            )

        # Roll
        rolls = [random.randint(1, num_sides) for _ in range(num_dice)]
        total = sum(rolls)

        if num_dice == 1:
            message = f"🎲 {rolls[0]}"
        else:
            rolls_str = ", ".join(str(r) for r in rolls)
            message = f"🎲 {rolls_str} (total: {total})"

        return SlashCommandResult(success=True, message_text=message)

    def cmd_8ball(self, args: str) -> SlashCommandResult:
        """Magic 8-ball command: random answer

        :param args: the question (optional)
        :return: SlashCommandResult
        """
        answer = random.choice(self.EIGHT_BALL_RESPONSES)
        emoji = "🎱"
        message = f"{emoji} {answer}"
        return SlashCommandResult(success=True, message_text=message)

    def cmd_dizz(self, args: str) -> SlashCommandResult:
        """Dizz command, makes QGIS shake.

        :param args: optional message displayed in message bar
        :return: SlashCommandResult
        """

        dizzy()

        return SlashCommandResult(
            success=True, local_action=lambda: ("show_message_bar", args)
        )

    def cmd_flick(self, args: str) -> SlashCommandResult:
        """Flick command, QGIS is flicking the wrist.

        :param args: optional message displayed in message bar
        :return: SlashCommandResult
        """

        flick_of_the_wrist()

        return SlashCommandResult(
            success=True, local_action=lambda: ("show_message_bar", args)
        )

    def cmd_wizz(self, args: str) -> SlashCommandResult:
        """Wizz command, makes the entire QGIS application shake like MSN effect.

        :param args: optional message displayed in message bar
        :return: SlashCommandResult
        """

        wizz()

        return SlashCommandResult(
            success=True, local_action=lambda: ("show_message_bar", args)
        )

    def cmd_list(self, args: str) -> SlashCommandResult:
        """List all available commands.

        :param args: unused
        :return: SlashCommandResult (local action, not sent to chat)
        """
        # Build command list with descriptions
        lines = ["📋 Available commands:"]
        for cmd in sorted(self.commands.keys()):
            desc = self.COMMAND_DESCRIPTIONS.get(cmd, "")
            lines.append(f"  /{cmd} - {desc}")

        message = "\n".join(lines)

        # Return as local action (display locally, don't send to chat)
        return SlashCommandResult(
            success=True,
            local_action=lambda: ("show_message", message),
        )

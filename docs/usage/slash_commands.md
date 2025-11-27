# Slash Commands

QChat supports Discord-style slash commands. Type a command starting with `/` in the chat input to use it.

## Available Commands

| Command | Description | Example |
| :------ | :---------- | :------ |
| `/list` | Display all available commands | `/list` |
| `/shrug` | Send the shrug emoticon ¯\\_(ツ)_/¯ | `/shrug oh well` |
| `/tableflip` | Send the table flip emoticon (╯°□°)╯︵ ┻━┻ | `/tableflip QGIS crash` |
| `/lenny` | Send the Lenny face ( ͡° ͜ʖ ͡°) | `/lenny` |
| `/yolo` | Convert your message to UPPERCASE with a dice emoji | `/yolo let's do this` |
| `/flip` | Flip a coin (heads or tails) | `/flip` |
| `/roll` | Roll dice with customizable faces and count | `/roll 2d20` |
| `/8ball` | Ask the magic 8-ball a question | `/8ball Will it rain?` |

## Command Details

### /list

Displays a list of all available slash commands with their descriptions.

### /shrug, /tableflip, /lenny

These emoticon commands send their respective text art to the chat. You can optionally add a message after the command:

```
/shrug I don't know
```

Sends: `¯\_(ツ)_/¯ I don't know`

### /yolo

Converts your message to uppercase and adds a dice emoji. If no message is provided, sends "YOLO! 🎲".

```
/yolo let's go
```

Sends: `LET'S GO 🎲`

### /flip

Flips a virtual coin and returns either "Heads" or "Tails" with a coin emoji.

### /roll

Rolls dice with customizable parameters. Supports several formats:

- `/roll` — Roll a single 6-sided die (default)
- `/roll 20` — Roll a single 20-sided die
- `/roll 2d6` — Roll 2 six-sided dice
- `/roll 4d20` — Roll 4 twenty-sided dice

**Limits:**

- Number of dice: 1 to 100
- Number of sides: 2 to 1000

When rolling multiple dice, the result shows each individual roll and the total:

```
🎲 15, 8, 12 (total: 35)
```

### /8ball

Ask the [magic 8-ball](https://en.wikipedia.org/wiki/Magic_8_Ball) a question and receive a random classic response. The question text is optional but makes it more fun:

```
/8ball Should I use Shapefile?
```

Possible responses include:

- Positive: "It is certain", "Without a doubt", "Yes definitely", "Outlook good"
- Neutral: "Reply hazy, try again", "Ask again later", "Cannot predict now"
- Negative: "Don't count on it", "My reply is no", "Outlook not so good", "Very doubtful"

## Autocomplete

When you start typing `/` in the chat input, QChat provides autocomplete suggestions for available commands.

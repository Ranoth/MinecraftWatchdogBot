"""
Minecraft Death Messages Database
Extracted from https://minecraft.wiki/w/Death_messages

This module contains all Minecraft Java Edition death messages organized by category.
Each death message is a string that can appear in the Minecraft server logs.
"""

# Standard death message patterns with placeholders:
# <player> = player name
# <player/mob> = player or mob name 
# <item> = item name

MINECRAFT_DEATH_MESSAGES = {
    "cactus": [
        "<player> was pricked to death",
        "<player> walked into a cactus while trying to escape <player/mob>"
    ],
    
    "drowning": [
        "<player> drowned",
        "<player> drowned while trying to escape <player/mob>"
    ],
    
    "drying_out": [
        "<player> died from dehydration",
        "<player> died from dehydration while trying to escape <player/mob>"
    ],
    
    "elytra": [
        "<player> experienced kinetic energy",
        "<player> experienced kinetic energy while trying to escape <player/mob>"
    ],
    
    "explosions": [
        "<player> blew up",
        "<player> was blown up by <player/mob>",
        "<player> was blown up by <player/mob> using <item>",
        "<player> was killed by [Intentional Game Design]"
    ],
    
    "falling": [
        "<player> hit the ground too hard",
        "<player> hit the ground too hard while trying to escape <player/mob>",
        "<player> fell from a high place",
        "<player> fell off a ladder",
        "<player> fell off some vines",
        "<player> fell off some weeping vines",
        "<player> fell off some twisting vines",
        "<player> fell off scaffolding",
        "<player> fell while climbing",
        "<player> was doomed to fall",
        "<player> was doomed to fall by <player/mob>",
        "<player> was doomed to fall by <player/mob> using <item>",
        "<player> was impaled on a stalagmite",
        "<player> was impaled on a stalagmite while fighting <player/mob>"
    ],
    
    "falling_blocks": [
        "<player> was squashed by a falling anvil",
        "<player> was squashed by a falling block",
        "<player> was skewered by a falling stalactite"
    ],
    
    "fire": [
        "<player> went up in flames",
        "<player> walked into fire while fighting <player/mob>",
        "<player> burned to death",
        "<player> was burned to a crisp while fighting <player/mob>"
    ],
    
    "fireworks": [
        "<player> went off with a bang",
        "<player> went off with a bang due to a firework fired from <item> by <player/mob>"
    ],
    
    "lava": [
        "<player> tried to swim in lava",
        "<player> tried to swim in lava to escape <player/mob>"
    ],
    
    "lightning": [
        "<player> was struck by lightning",
        "<player> was struck by lightning while fighting <player/mob>"
    ],
    
    "magma_block": [
        "<player> discovered the floor was lava",
        "<player> walked into the danger zone due to <player/mob>"
    ],
    
    "magic": [
        "<player> was killed by magic",
        "<player> was killed by magic while trying to escape <player/mob>",
        "<player> was killed by <player/mob> using magic",
        "<player> was killed by <player/mob> using <item>"
    ],
    
    "powder_snow": [
        "<player> froze to death",
        "<player> was frozen to death by <player/mob>"
    ],
    
    "players_and_mobs": [
        "<player> was slain by <player/mob>",
        "<player> was slain by <player/mob> using <item>",
        "<player> was stung to death",
        "<player> was stung to death by <player/mob> using <item>",
        "<player> was obliterated by a sonically-charged shriek",
        "<player> was obliterated by a sonically-charged shriek while trying to escape <player/mob> wielding <item>",
        "<player> was smashed by <player/mob>",
        "<player> was smashed by <player/mob> with <item>",
        "<player> was speared by <player/mob>",
        "<player> was speared by <player/mob> using <item>"
    ],
    
    "projectiles": [
        "<player> was shot by <player/mob>",
        "<player> was shot by <player/mob> using <item>",
        "<player> was pummeled by <player/mob>",
        "<player> was pummeled by <player/mob> using <item>",
        "<player> was fireballed by <player/mob>",
        "<player> was fireballed by <player/mob> using <item>",
        "<player> was shot by a skull from <player/mob>",
        "<player> was shot by a skull from <player/mob> using <item>"
    ],
    
    "starving": [
        "<player> starved to death",
        "<player> starved to death while fighting <player/mob>"
    ],
    
    "suffocation": [
        "<player> suffocated in a wall",
        "<player> suffocated in a wall while fighting <player/mob>",
        "<player> was squished too much",
        "<player> was squashed by <player/mob>",
        "<player> left the confines of this world",
        "<player> left the confines of this world while fighting <player/mob>"
    ],
    
    "sweet_berry_bush": [
        "<player> was poked to death by a sweet berry bush",
        "<player> was poked to death by a sweet berry bush while trying to escape <player/mob>"
    ],
    
    "thorns": [
        "<player> was killed while trying to hurt <player/mob>",
        "<player> was killed by <item> while trying to hurt <player/mob>"
    ],
    
    "trident": [
        "<player> was impaled by <player/mob>",
        "<player> was impaled by <player/mob> with <item>"
    ],
    
    "void": [
        "<player> fell out of the world",
        "<player> didn't want to live in the same world as <player/mob>"
    ],
    
    "wither_effect": [
        "<player> withered away",
        "<player> withered away while fighting <player/mob>"
    ],
    
    "generic": [
        "<player> died",
        "<player> died because of <player/mob>",
        "<player> was killed",
        "<player> was killed while fighting <player/mob>"
    ]
}

# Flattened list of all death messages for easy searching
ALL_DEATH_MESSAGES = []
for category, messages in MINECRAFT_DEATH_MESSAGES.items():
    ALL_DEATH_MESSAGES.extend(messages)

# Common player/mob names and items for pattern matching
COMMON_PLAYER_NAMES = [
    "Steve", "Alex", "Notch", "Herobrine", "Player", "Admin"
]

COMMON_MOB_NAMES = [
    "Zombie", "Skeleton", "Creeper", "Spider", "Enderman", "Witch",
    "Blaze", "Ghast", "Wither", "Ender Dragon", "Guardian", "Shulker",
    "Vindicator", "Evoker", "Pillager", "Ravager", "Warden", "Piglin"
]

COMMON_ITEMS = [
    "Diamond Sword", "Iron Sword", "Bow", "Crossbow", "Trident", 
    "Netherite Sword", "Enchanted Book", "Golden Apple", "TNT"
]

# Regex patterns for placeholder replacement
PLAYER_PATTERN = r"[A-Za-z0-9_]+"
ENTITY_PATTERN = r"[A-Za-z0-9_ ]+"
ITEM_PATTERN = r"[A-Za-z0-9_ ]+"

def _create_regex_pattern(death_msg):
    """Create a regex pattern from a death message template."""
    pattern = death_msg.replace("<player>", PLAYER_PATTERN)
    pattern = pattern.replace("<player/mob>", ENTITY_PATTERN)
    pattern = pattern.replace("<item>", ITEM_PATTERN)
    return f"^{pattern}$"

def is_death_message(message):
    """
    Check if a given message matches any Minecraft death message pattern.
    
    Args:
        message (str): The message to check
        
    Returns:
        bool: True if the message appears to be a death message
    """
    import re
    message = message.strip()
    
    # Check for exact matches with placeholders
    for death_msg in ALL_DEATH_MESSAGES:
        pattern = _create_regex_pattern(death_msg)
        if re.match(pattern, message):
            return True
    
    return False

def get_death_message_category(message):
    """
    Determine which category a death message belongs to.
    
    Args:
        message (str): The death message
        
    Returns:
        str or None: The category name if found, None otherwise
    """
    import re
    
    for category, messages in MINECRAFT_DEATH_MESSAGES.items():
        for death_msg in messages:
            pattern = _create_regex_pattern(death_msg)
            if re.match(pattern, message):
                return category
    
    return None

# Example usage:
if __name__ == "__main__":
    # Test some example death messages
    test_messages = [
        "Steve was pricked to death",
        "Alex fell from a high place",
        "Notch was slain by Zombie",
        "Player tried to swim in lava",
        "Admin was blown up by Creeper",
        "This is not a death message"
    ]
    
    print("Testing death message detection:")
    for msg in test_messages:
        is_death = is_death_message(msg)
        category = get_death_message_category(msg) if is_death else None
        print(f"'{msg}' -> Death: {is_death}, Category: {category}")
    
    print(f"\nTotal death messages: {len(ALL_DEATH_MESSAGES)}")
    print(f"Total categories: {len(MINECRAFT_DEATH_MESSAGES)}")
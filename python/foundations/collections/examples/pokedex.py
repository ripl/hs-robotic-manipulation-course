cards = {
    "Pikachu": "Common",
    "Charizard": "Rare",
    "Blastoise": "Rare",
    "Mewtwo": "Legendary",
    "Jigglypuff": "Uncommon",
    "Snorlax": "Common",
    "Dragonite": "Rare"
}

def count_rarity_levels(cards):
  """
  >>> count_rarity_levels(cards)
  {'Common': 2, 'Rare': 3, 'Legendary': 1, 'Uncommon': 1}
  """
  pass

def filter_by_rarity(cards, rarity):
  """
  Filter cards based on the specified rarity level.

  Examples:
  >>> filter_by_rarity(cards, "Rare")
  {'Charizard': 'Rare', 'Blastoise': 'Rare', 'Dragonite': 'Rare'}
    
  >>> filter_by_rarity(cards, "Common")
  {'Pikachu': 'Common', 'Snorlax': 'Common'}
  
  >>> filter_by_rarity(cards, "Legendary")
  {'Mewtwo': 'Legendary'}
    
  >>> filter_by_rarity(cards, "Uncommon")
  {'Jigglypuff': 'Uncommon'}
    
  >>> filter_by_rarity(cards, "Mythical")  # Returns an empty dictionary for non-existent rarity
  {}
  """
  pass


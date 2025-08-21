# services/wahapedia-scraper/src/scrapers/wahapedia/css_selectors.py

"""
CSS selectors and patterns for Wahapedia scraping.
Centralized location for all selectors to make maintenance easier.
"""

# Navigation and Faction List Selectors
FACTION_SELECTORS = {
    'nav_button': '.NavBtn_Factions',
    'dropdown_content': '.NavDropdown-content',
    'faction_items': '.BreakInsideAvoid',
    'faction_link': '.BreakInsideAvoid a',
}

# Army Rules Selectors (for Phase 2)
ARMY_RULE_SELECTORS = {
    'army_rules_anchor': 'a[name="Army-Rules"]',
    'columns_container': '.Columns2',
    'break_inside_avoid': '.BreakInsideAvoid',
    'rule_name': 'h3',
}

# Detachment Selectors (for Phase 3) 
DETACHMENT_SELECTORS = {
    'detachment_anchor': 'a[name*="Detachment-Rule"]',
    'detachment_header': 'h2.outline_header',
    'enhancement_anchor': 'a[name*="Enhancements"]',
    'enhancement_container': '.Columns2',
    'enhancement_item': '.BreakInsideAvoid',
    'enhancement_table': 'table',
    'enhancement_name_span': 'tbody tr td ul li span:first-child',
    'enhancement_cost_span': 'tbody tr td ul li span:last-child',
}

# Unit/Datasheet Selectors (for Phase 4)
UNIT_SELECTORS = {
    'datasheet': 'div.datasheet:not([style*="display: none"])',
    'unit_header': '.dsH2Header',
    'unit_name': '.dsH2Header > div',
    'price_tag': '.PriceTag',
    'wargear_header': 'div:contains("WARGEAR OPTIONS")',
    'wargear_list': 'ul',
    'wargear_item': 'li',
}

# URLs
URLS = {
    'quick_start': '/wh40k10ed/the-rules/quick-start-guide/',
    'faction_datasheets': '/wh40k10ed/factions/{faction_name}/datasheets.html',
}

# Population Growth/Decline Rates (yearly rates converted to daily)
HUMAN_GROWTH_RATE = 1.0003  # ~11% yearly growth
HUMAN_DECLINE_RATE = 0.9997  # ~11% yearly decline
TREE_GROWTH_RATE = 1.0001  # ~3.7% yearly growth
WILDLIFE_DECLINE_RATE = 0.999  # ~30% yearly decline

# Population Density Limits (per cell)
MAX_HUMAN_DENSITY = 1000  # maximum humans per city cell
MAX_TREE_DENSITY = 500   # maximum trees per forest cell

# Cell Conversion Thresholds
CITY_ABANDONMENT_DAYS = 365  # days before a city can convert to land
LAND_TO_FOREST_DAYS = 1825   # 5 years of no use before land can become forest

# Health Impact Rates
AIR_POLLUTION_HEALTH_IMPACT = -0.15
GROUND_POLLUTION_HEALTH_IMPACT = -0.05
NATURE_PROXIMITY_BONUS = 0.05
WILDLIFE_BASE_HEALTH_DECLINE = 0.1

# Tree/Forest Related
TREE_CO2_ABSORPTION_FACTOR = 0.1
FOREST_SPREAD_CHANCE = 0.1

# Pollution Related Constants
AIR_SPREAD_RATE = 0.4  # Air pollution spreads faster
GROUND_SPREAD_RATE = 0.1  # Ground pollution spreads slower
AIR_TO_GROUND_RATE = 0.2  # Rate at which air pollution settles into ground

# Time Constants (in simulation days)
WEEKLY_TIMEOUT = 7
MONTHLY_TIMEOUT = 30
DAILY_TIMEOUT = 1

# Wildlife Movement Constants
MAX_WILDLIFE_MOVEMENT_RADIUS = 3
WILDLIFE_BASE_SUCCESS_RATE = 0.7  # 70% base chance
WILDLIFE_DISTANCE_PENALTY = 0.2   # -20% per cell distance
WILDLIFE_HEALTH_BONUS = 0.3       # Up to +30% from health

# Resource Management
COMMUTE_POLLUTION_MULTIPLIER = 2  # Two commutes per day

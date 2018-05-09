# Little trick to get convinient way of working with db connection
# We will assign db pool connection during start appliction and destroy during shutdown
# with db.DB_POOL variable
DB_POOL = None

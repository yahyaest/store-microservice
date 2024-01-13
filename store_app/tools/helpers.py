import sys
import logging 
import coloredlogs

logFormatter = logging.Formatter('%(asctime)s %(levelname)s [%(name)s] %(message)s' )
stdLogHandler = logging.StreamHandler(sys.stdout)
stdLogHandler.setFormatter( logFormatter )

logger = logging.getLogger("Store")
logger.addHandler( stdLogHandler )
logger.setLevel( logging.DEBUG )

coloredlogs.install(level='ERROR')
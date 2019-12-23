# Logging and Pipeline Verbosity

The pipeline reports about it's progress during several de-identification stages. We use [`tqdm`](https://github.com/tqdm/tqdm) and [`loguru`](https://github.com/Delgan/loguru) for logging. You can use the `verbose` parameter of the taggers to enable progress report.

Logging can be configured as follows:

```py
import logging
import sys
from loguru import logger

logger.remove()
logger.add(sys.stderr, level=logging.WARNING)
logging.getLogger('flair').setLevel(logging.WARNING)
```

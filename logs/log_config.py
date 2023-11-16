import logging

# import uvicorn

logger = logging.getLogger('dtmb-logs')
logger.setLevel(logging.INFO)

FORMAT: str = "%(levelname)s: \t %(asctime)s \t %(filename)s %(funcName)s - line: %(lineno)s \t %(message)s"

file1 = logging.FileHandler('apiLogs.log')
# file2 = logging.FileHandler('apiLogs.ini')

fomatter = logging.Formatter(fmt=FORMAT, datefmt='%Y-%m-%d %H:%M:%S')
file1.setFormatter(fomatter)
# file2.setFormatter(fomatter)

logger.addHandler(file1)
# logger.addHandler(file2)

# logging.basicConfig(
#     level=logging.INFO,
#     format=FORMAT,
#     datefmt='%Y-%m-%d %H:%M:%S',
#     handlers=[file1, file2],
#     # style=uvicorn.logging.DefaultFormatter(FORMAT, datefmt="%Y-%m-%d %H:%M:%S")

# )




# logging.setFormatter=uvicorn.logging.DefaultFormatter(FORMAT), datefmt="%Y-%m-%d %H:%M:%S")
# log_config.py
import logging
import sys
import datetime
import os
import config
import os
import config
path = config.get_config_directory()
# 更改工作目录为脚本所在目录
os.chdir(path)

# 打印当前工作目录
print("Package.log_config.py:当前工作目录：", os.getcwd())
# 获取当前时间并格式化文件名
current_time = datetime.datetime.now()
formatted_time = current_time.strftime('%Y年%m月%d日')
FILE_NAME = './logs/' + formatted_time + '.txt'


class Logger(object):
    def __init__(self, filename='default.log', stream=sys.stdout):
        self.terminal = stream
        self.log = open(filename, 'a')

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        pass


class FileLoggerHandler(logging.Handler):
    def __init__(self, filename='default.log', stream=sys.stdout):
        super().__init__()
        self.logger_writer = Logger(filename, stream)

    def emit(self, record):
        msg = self.format(record)
        self.logger_writer.write(msg + '\n')


class CustomFormatter(logging.Formatter):
    def format(self, record):
        # 仅保留文件名而不是完整路径
        record.pathname = os.path.basename(record.pathname)
        return super().format(record)


# 配置日志记录器
formatter = CustomFormatter('[%(asctime)s] [%(levelname)8s] %(pathname)s:%(lineno)d - %(message)s')
file_logger_handler = FileLoggerHandler(FILE_NAME, sys.stdout)
file_logger_handler.setFormatter(formatter)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.addHandler(file_logger_handler)
# 确保所有日志级别都输出到日志文件中
logging.basicConfig(level=logging.DEBUG, handlers=[file_logger_handler])
# 重定向 sys.stdout 和 sys.stderr 到不同的日志文件和控制台
sys.stdout = Logger(FILE_NAME, sys.stdout)
sys.stderr = Logger(FILE_NAME, sys.stderr)

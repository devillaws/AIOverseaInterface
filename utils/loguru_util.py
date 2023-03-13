import os
import datetime
import sys
from loguru import logger



class MyLogger:
    def __init__(self):
        self.logger = logger
        # 清空所有设置
        self.logger.remove()
        # 添加控制台输出的格式,sys.stdout为输出到屏幕;关于这些配置还需要自定义请移步官网查看相关参数说明
        self.logger.add(sys.stdout,
                        format="<green>{time:YYYYMMDD HH:mm:ss}</green> | "  # 颜色>时间
                               "{process.name} | "  # 进程名
                               "{thread.name} | "  # 线程名
                               "<cyan>{module}</cyan>.<cyan>{function}</cyan>"  # 模块名.方法名
                               ":<cyan>{line}</cyan> | "  # 行号
                               "<level>{level}</level>: "  # 等级
                               "<level>{message}</level>",  # 日志内容
                        )
        # 输出到文件的格式,注释下面的add',则关闭日志写入
        self.logger.add(self.get_log_filename(),
                        encoding="utf-8",
                        backtrace=True,  # 回溯
                        diagnose=True,  # 诊断
                        enqueue=True,  # 异步写入
                        level='DEBUG',
                        format='{time:YYYYMMDD HH:mm:ss} - '  # 时间
                               "{process.name} | "  # 进程名
                               "{thread.name} | "  # 线程名
                               '{module}.{function}:{line} - {level} -{message}',  # 模块名.方法名:行号
                        rotation='00:00',  # 日志创建周期
                        retention='1 year',  # 保存
                        )

    def make_log_dir(self, dirname='logs'):  # 创建存放日志的目录，并返回目录的路径
        now_dir = os.path.dirname(__file__)
        father_path = os.path.split(now_dir)[0]
        path = os.path.join(father_path, dirname)
        path = os.path.normpath(path)
        if not os.path.exists(path):
            os.mkdir(path)
        return path

    def get_log_filename(self):  # 创建日志文件的文件名格式，便于区分每天的日志
        filename = "{}.log".format(datetime.date.today())
        filename = os.path.join(self.make_log_dir(), filename)
        filename = os.path.normpath(filename)
        return filename

    def info(self, msg):
        return logger.info(msg)

    def debug(self, msg):
        return logger.debug(msg)

    def warning(self, msg):
        return logger.warning(msg)

    def error(self, msg, title="错误提醒", is_send=True):
        # if is_send:
            # SendMail(title=title,
            #          content=msg,
            #          recv=[EMAIL]).send_mail()
        return logger.error(msg)


if __name__ == '__main__':
    loggers = MyLogger()
    loggers.debug('this is a debug message')
    loggers.info('this is another debug message')
    loggers.warning('this is another debug message')
    loggers.error('this is another debug message')

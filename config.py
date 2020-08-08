import os

basedir =  os.path.abspath(os.path.dirname(__file__))

class Config:
    # 基础环境配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    # 开发环境配置
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URI') or \
                              'mysql+pymysql://root:yzn1370628636@localhost/xuanshang'

class TestingConfig(Config):
    pass

class ProductionConfig(Config):
    # 生产环境配置
    pass

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

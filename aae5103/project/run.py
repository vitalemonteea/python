#!/usr/bin/env python3
"""
实时航班登机口管理系统

这是系统的主入口脚本，支持两种运行模式：
1. Web界面模式（默认）
2. 命令行模式
"""

import os
import sys
import logging
import argparse
from pathlib import Path

# 配置日志系统
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_FILE = 'gate_assignment.log'

def setup_logging():
    """配置日志系统"""
    logging.basicConfig(
        level=logging.INFO,
        format=LOG_FORMAT,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(LOG_FILE)
        ]
    )
    return logging.getLogger(__name__)

def check_environment():
    """检查运行环境和数据文件"""
    logger = logging.getLogger(__name__)
    
    # 检查数据目录
    data_dir = Path(__file__).parent / 'data'
    if not data_dir.exists():
        logger.warning(f"数据目录不存在: {data_dir}")
        logger.info("创建数据目录...")
        data_dir.mkdir(exist_ok=True)
    
    # 检查必要数据文件
    flight_file = data_dir / 'flight.xlsx'
    distance_file = data_dir / 'distance.xlsx'
    
    missing_files = []
    if not flight_file.exists():
        missing_files.append('flight.xlsx')
    if not distance_file.exists():
        missing_files.append('distance.xlsx')
    
    if missing_files:
        logger.warning(f"缺少必要的数据文件: {', '.join(missing_files)}")
        logger.info("系统将尝试从其他位置加载数据，或在启动时提示错误")
    else:
        logger.info("数据文件检查成功")
    
    return True

def run_standalone():
    """运行独立的命令行版本"""
    try:
        from main import run_assignment
        logger.info("启动命令行版本登机口分配系统")
        run_assignment()
    except ImportError:
        logger.error("找不到必要的模块，请确保已安装所有依赖")
        sys.exit(1)
    except Exception as e:
        logger.error(f"运行命令行版本时发生错误: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)

def run_web():
    """运行Web版本"""
    try:
        from app import app
        logger.info("启动Web版本登机口分配系统")
        logger.info("访问 http://127.0.0.1:8080 打开管理界面")
        app.run(debug=False, host='0.0.0.0', port=8080)
    except ImportError:
        logger.error("找不到必要的模块，请确保已安装所有依赖")
        logger.error("提示: 运行 'pip install -r requirements.txt' 安装依赖")
        sys.exit(1)
    except Exception as e:
        logger.error(f"启动Web服务器时发生错误: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    # 设置命令行参数
    parser = argparse.ArgumentParser(
        description='实时航班登机口管理系统',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        '--mode', 
        choices=['web', 'cli'], 
        default='web', 
        help='运行模式: web(网页界面) 或 cli(命令行)'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=8080,
        help='Web服务器端口号'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='启用调试模式'
    )
    
    args = parser.parse_args()
    
    # 设置日志系统
    logger = setup_logging()
    
    # 显示环境信息
    logger.info(f"当前工作目录: {os.getcwd()}")
    logger.info(f"Python版本: {sys.version}")
    
    # 检查环境和数据文件
    check_environment()
    
    # 根据模式运行程序
    if args.mode == 'web':
        run_web()
    else:
        run_standalone() 
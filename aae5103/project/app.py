#!/usr/bin/env python3
"""
实时航班登机口管理系统 - Web服务器

为登机口管理系统提供Web API和用户界面。
此模块实现了系统的所有HTTP端点，包括静态页面和API接口。

主要端点:
- GET /: 主页，返回用户界面
- GET /current_assignment: 获取当前航班分配
- POST /reassign: 处理重新分配请求
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import traceback
import logging
from datetime import datetime
import json

# 导入业务逻辑模块
from gate_assignment_engine import reassign_gates, get_current_flights

# 配置日志
logger = logging.getLogger(__name__)

# 初始化Flask应用
app = Flask(__name__)
CORS(app)  # 添加CORS支持，解决跨域问题

# 配置应用
app.config.update(
    JSON_SORT_KEYS=False,  # 禁止JSON键排序，保持原始顺序
    JSON_AS_ASCII=False,   # 允许JSON中包含非ASCII字符
    JSONIFY_PRETTYPRINT_REGULAR=True,  # 美化JSON输出
    MAX_CONTENT_LENGTH=16 * 1024 * 1024  # 限制请求大小为16MB
)

@app.route('/')
def index():
    """
    系统主页
    
    返回:
        HTML: 渲染后的仪表盘页面
    """
    logger.info("访问主页")
    return render_template('dashboard.html')

@app.route('/current_assignment')
def current_assignment():
    """
    获取当前航班分配状态
    
    返回:
        JSON: 包含所有航班和可用登机口的JSON数据
        
    错误:
        500: 如果获取数据时发生错误
    """
    try:
        logger.info("获取当前航班分配状态")
        flights = get_current_flights()
        
        # 记录数据概要
        flight_count = len(flights.get('flights', []))
        gate_count = len(flights.get('gates', []))
        logger.info(f"成功获取航班数据: {flight_count}个航班, {gate_count}个登机口")
        
        return jsonify(flights)
    except Exception as e:
        error_msg = f"获取航班数据出错: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        return jsonify({"error": error_msg, "details": traceback.format_exc()}), 500

@app.route('/reassign', methods=['POST'])
def reassign():
    """
    处理重新分配登机口的请求
    
    支持两种类型的重新分配触发条件:
    1. 登机口关闭: 将指定登机口标记为不可用，为其分配的航班找到新的登机口
    2. 航班延误: 更新航班的起飞时间，并考虑时间冲突进行重新分配
    
    请求体:
        JSON对象，包含以下可选字段:
        - closed_gates: 关闭的登机口列表
        - delayed_flights: 延误航班列表，每个元素包含航班号和新时间
    
    返回:
        JSON: 包含重新分配结果的JSON数据
        
    错误:
        400: 如果请求数据格式错误
        500: 如果处理过程中发生服务器错误
    """
    try:
        request_data = request.json
        logger.info(f"收到重新分配请求: {json.dumps(request_data)}")
        
        # 验证请求数据
        if not request_data:
            logger.error("请求数据为空")
            return jsonify({'status': 'failed', 'message': '请求数据为空'}), 400
        
        # 处理关闭的登机口
        closed_gates = request_data.get('closed_gates', [])
        if closed_gates:
            logger.info(f"需要处理的关闭登机口: {closed_gates}")
        else:
            logger.info("没有指定关闭的登机口")
        
        # 处理延误的航班
        delayed_flights = request_data.get('delayed_flights', [])
        if delayed_flights:
            logger.info(f"需要处理的延误航班: {len(delayed_flights)}个")
            
            # 验证延误航班数据格式
            for flight in delayed_flights:
                if 'no' not in flight or 'new_time' not in flight:
                    error_msg = f"延误航班数据格式错误: {flight}"
                    logger.error(error_msg)
                    return jsonify({'status': 'failed', 'message': error_msg}), 400
                
                # 验证时间格式
                try:
                    hours, minutes = flight['new_time'].split(':')
                    hours = int(hours)
                    minutes = int(minutes)
                    if hours < 0 or hours > 23 or minutes < 0 or minutes > 59:
                        error_msg = f"延误航班时间格式错误: {flight['new_time']}"
                        logger.error(error_msg)
                        return jsonify({'status': 'failed', 'message': error_msg}), 400
                except Exception as e:
                    error_msg = f"延误航班时间格式错误: {flight['new_time']} - {str(e)}"
                    logger.error(error_msg)
                    return jsonify({'status': 'failed', 'message': error_msg}), 400
        else:
            logger.info("没有指定延误的航班")
        
        # 检查是否有任何需要处理的数据
        if not closed_gates and not delayed_flights:
            warning_msg = "请求中没有指定关闭的登机口或延误的航班"
            logger.warning(warning_msg)
            return jsonify({'status': 'warning', 'message': warning_msg}), 400
            
        # 特殊情况处理：如果只关闭了登机口但该登机口当前没有安排航班
        if closed_gates and not delayed_flights:
            # 获取当前航班数据
            current_flights = get_current_flights()
            
            # 检查关闭的登机口是否有航班
            gates_with_flights = set()
            for flight in current_flights['flights']:
                if flight['gate'] in closed_gates:
                    gates_with_flights.add(flight['gate'])
            
            if not gates_with_flights:
                info_msg = f"关闭的登机口 {closed_gates} 当前没有航班，无需重新分配"
                logger.info(info_msg)
                return jsonify({
                    'status': 'success', 
                    'assignment': [],
                    'message': '关闭的登机口当前没有航班，无需重新分配'
                })
            else:
                logger.info(f"以下关闭的登机口有航班需要重新分配: {gates_with_flights}")
        
        # 准备数据并调用重新分配引擎
        reassign_data = {
            'closed_gates': closed_gates,
            'delayed_flights': delayed_flights,
            '_force_reassign': True  # 添加一个标记，强制执行重新分配
        }
        
        # 调用分配引擎
        start_time = datetime.now()
        logger.info(f"调用gate_assignment_engine.reassign_gates，参数: {json.dumps(reassign_data)}")
        result = reassign_gates(reassign_data)
        end_time = datetime.now()
        
        # 计算处理时间
        processing_time = (end_time - start_time).total_seconds()
        logger.info(f"重新分配处理时间: {processing_time:.3f} 秒")
        
        # 记录重新分配的结果
        if result['status'] == 'success':
            changes = [a for a in result['assignment'] if a['original_gate'] != a['new_gate']]
            logger.info(f"重新分配成功，共{len(changes)}个航班被重新分配")
            for change in changes:
                logger.info(f"航班 {change['flight']} 从 {change['original_gate']} 重新分配到 {change['new_gate']}")
        else:
            error_msg = f"重新分配失败: {result.get('message', '未知错误')}"
            logger.error(error_msg)
        
        # 添加处理时间信息到结果
        result['processing_time'] = f"{processing_time:.3f}"
            
        return jsonify(result)
    except Exception as e:
        error_msg = f"重新分配过程中发生错误: {str(e)}"
        logger.exception(error_msg)
        return jsonify({
            'status': 'failed', 
            'message': error_msg,
            'details': traceback.format_exc()
        }), 500

# 添加一个健康检查端点
@app.route('/health')
def health_check():
    """
    系统健康检查端点
    
    返回:
        JSON: 包含系统状态信息
    """
    try:
        # 尝试获取航班数据，测试系统的基本功能
        flights = get_current_flights()
        flight_count = len(flights.get('flights', []))
        gate_count = len(flights.get('gates', []))
        
        return jsonify({
            'status': 'healthy',
            'flight_count': flight_count,
            'gate_count': gate_count,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"健康检查失败: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# 错误处理器
@app.errorhandler(404)
def not_found(error):
    """处理404错误"""
    logger.warning(f"404错误: {request.path}")
    return jsonify({'error': 'Not Found', 'path': request.path}), 404

@app.errorhandler(405)
def method_not_allowed(error):
    """处理405错误"""
    logger.warning(f"405错误: {request.method} {request.path}")
    return jsonify({'error': 'Method Not Allowed', 'method': request.method, 'path': request.path}), 405

@app.errorhandler(500)
def server_error(error):
    """处理500错误"""
    logger.error(f"500错误: {str(error)}")
    return jsonify({'error': 'Internal Server Error', 'details': str(error)}), 500

# 启动服务器
if __name__ == '__main__':
    logger.info("直接启动Flask应用服务器")
    app.run(debug=False, host='0.0.0.0', port=8080) 
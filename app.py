from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import json
import os
import datetime
import math
from dateutil import tz

app = Flask(__name__)
CORS(app)

# 简化核素数据库 - 只保留F18和C11
HALF_LIFE_DICT = {
    'F18': 109.7,
    'C11': 20.3
}

# 核素显示名称
NUCLIDE_NAMES = {
    'F18': 'F-18 (FDG)',
    'C11': 'C-11 (Choline)'
}

# 数据保存功能已迁移到客户端localStorage

def decay_activity(initial_activity, elapsed_minutes, half_life):
    """计算放射性衰变后的活度"""
    return initial_activity * (0.5 ** (elapsed_minutes / half_life))

def calculate_concentration(activity, volume):
    """计算浓度"""
    return activity / volume if volume else 0

def calculate_volume(dose, concentration):
    """计算所需体积"""
    return dose / concentration if concentration else 0

# 数据保存功能已迁移到客户端localStorage，不再需要服务器端保存

def get_current_time_cn():
    """获取东八区当前时间"""
    cn_tz = tz.gettz('Asia/Shanghai')
    return datetime.datetime.now(cn_tz)

@app.route('/')
def index():
    """主页面"""
    return render_template('index.html')

@app.route('/api/calculate', methods=['POST'])
def calculate():
    """计算API端点"""
    try:
        data = request.get_json()
        
        # 获取输入参数
        nuclide = data.get('nuclide', 'F18')
        init_time_str = data.get('init_time', '07:00')
        target_time_str = data.get('target_time', '07:30')
        init_activity = float(data.get('init_activity', 0))
        init_volume = float(data.get('init_volume', 0))
        desired_dose_str = data.get('desired_dose', '')
        
        # 如果目标剂量为空，返回默认结果
        if not desired_dose_str or desired_dose_str == '':
            return jsonify({
                'success': True,
                'result': {
                    'current_activity': 0.0,
                    'current_concentration': 0.0,
                    'required_volume': 0.0,
                    'elapsed_minutes': 0.0
                }
            })
        
        desired_dose = float(desired_dose_str)
        
        # 解析时间
        init_time = datetime.datetime.strptime(init_time_str, '%H:%M').time()
        target_time = datetime.datetime.strptime(target_time_str, '%H:%M').time()
        
        # 计算时间差（分钟）
        init_dt = datetime.datetime.combine(datetime.date.today(), init_time)
        target_dt = datetime.datetime.combine(datetime.date.today(), target_time)
        
        # 如果目标时间小于初始时间，说明跨天了
        if target_dt < init_dt:
            target_dt += datetime.timedelta(days=1)
        
        elapsed_minutes = (target_dt - init_dt).total_seconds() / 60
        
        # 获取半衰期
        half_life = HALF_LIFE_DICT.get(nuclide, 109.7)
        
        # 计算当前活度
        current_activity = decay_activity(init_activity, elapsed_minutes, half_life)
        
        # 计算当前浓度
        current_concentration = calculate_concentration(current_activity, init_volume)
        
        # 计算所需体积
        required_volume = calculate_volume(desired_dose, current_concentration)
        
        # 数据现在保存在客户端localStorage中，不再需要服务器端保存
        
        return jsonify({
            'success': True,
            'result': {
                'current_activity': round(current_activity, 2),
                'current_concentration': round(current_concentration, 3),
                'required_volume': round(required_volume, 3),
                'elapsed_minutes': round(elapsed_minutes, 1)
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/current-time', methods=['GET'])
def get_current_time():
    """获取东八区当前时间"""
    current_time = get_current_time_cn()
    return jsonify({
        'current_time': current_time.strftime('%H:%M'),
        'timezone': 'Asia/Shanghai'
    })

# 数据保存功能已迁移到客户端localStorage，不再需要此API端点

@app.route('/api/nuclides', methods=['GET'])
def get_nuclides():
    """获取核素信息"""
    return jsonify({
        'nuclides': NUCLIDE_NAMES,
        'half_lives': HALF_LIFE_DICT
    })

@app.route('/health')
def health_check():
    """健康检查端点"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.datetime.now().isoformat()})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5001)))

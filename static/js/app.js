// 应用状态管理
class DoseCalculatorApp {
    constructor() {
        this.currentNuclide = 'F18';
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadSavedData();
        this.updateNuclideUI();
        this.calculate();
        // 默认选择第二个标签页（分装与计算）
        this.switchTab('tab2');
    }

    bindEvents() {
        // 标签页切换
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.switchTab(e.currentTarget.dataset.tab);
            });
        });

        // 核素选择
        document.querySelectorAll('.nuclide-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.currentNuclide = e.currentTarget.dataset.nuclide;
                this.updateNuclideUI();
                this.calculate();
            });
        });

        // 填充当前时间
        document.getElementById('fill-current-time').addEventListener('click', () => {
            this.fillCurrentTime();
        });

        // 快速时间按钮
        document.querySelectorAll('.btn-quick').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const minutes = parseInt(e.currentTarget.dataset.minutes);
                this.addMinutesToTargetTime(minutes);
            });
        });

        // 清空剂量
        document.getElementById('clear-dose').addEventListener('click', () => {
            document.getElementById('desired-dose').value = '';
            this.clearResults();
        });

        // 计算按钮
        document.getElementById('calculate-btn').addEventListener('click', () => {
            this.calculate();
        });

        // 输入变化时自动计算
        const inputs = ['init-time', 'target-time', 'init-activity', 'init-volume', 'desired-dose'];
        inputs.forEach(id => {
            document.getElementById(id).addEventListener('input', () => {
                this.calculate();
            });
        });
    }

    switchTab(tabId) {
        // 更新标签页按钮状态
        document.querySelectorAll('.tab-btn').forEach(btn => {
            if (btn.dataset.tab === tabId) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });

        // 更新标签页内容
        document.querySelectorAll('.tab-content').forEach(content => {
            if (content.id === tabId) {
                content.classList.add('active');
            } else {
                content.classList.remove('active');
            }
        });
    }

    updateNuclideUI() {
        document.querySelectorAll('.nuclide-btn').forEach(btn => {
            if (btn.dataset.nuclide === this.currentNuclide) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });
    }

    async fillCurrentTime() {
        try {
            const response = await fetch('/api/current-time');
            const data = await response.json();
            document.getElementById('init-time').value = data.current_time;
            this.calculate();
        } catch (error) {
            console.error('获取当前时间失败:', error);
            // 使用本地时间作为备选
            const now = new Date();
            const timeString = now.toTimeString().slice(0, 5);
            document.getElementById('init-time').value = timeString;
            this.calculate();
        }
    }

    addMinutesToTargetTime(minutes) {
        const targetTimeInput = document.getElementById('target-time');
        const currentTime = targetTimeInput.value;
        
        if (currentTime) {
            const [hours, mins] = currentTime.split(':').map(Number);
            const date = new Date();
            date.setHours(hours, mins + minutes, 0);
            
            const newTime = date.toTimeString().slice(0, 5);
            targetTimeInput.value = newTime;
            this.calculate();
        }
    }

    async loadSavedData() {
        try {
            const response = await fetch('/api/saved-data');
            const data = await response.json();
            
            if (data.init_time) document.getElementById('init-time').value = data.init_time;
            if (data.target_time) document.getElementById('target-time').value = data.target_time;
            if (data.init_activity) document.getElementById('init-activity').value = data.init_activity;
            if (data.init_volume) document.getElementById('init-volume').value = data.init_volume;
            if (data.desired_dose) document.getElementById('desired-dose').value = data.desired_dose;
            if (data.nuclide) this.currentNuclide = data.nuclide;
            
            // 更新核素UI
            this.updateNuclideUI();
            
        } catch (error) {
            console.error('加载保存数据失败:', error);
        }
    }

    async calculate() {
        const calculateBtn = document.getElementById('calculate-btn');
        calculateBtn.classList.add('loading');
        calculateBtn.textContent = '计算中...';

        try {
            const formData = {
                nuclide: this.currentNuclide,
                init_time: document.getElementById('init-time').value,
                target_time: document.getElementById('target-time').value,
                init_activity: document.getElementById('init-activity').value,
                init_volume: document.getElementById('init-volume').value,
                desired_dose: document.getElementById('desired-dose').value
            };

            // 如果目标剂量为空，不进行计算，直接清空结果显示
            if (!formData.desired_dose || formData.desired_dose === '') {
                this.clearResults();
                return;
            }

            const response = await fetch('/api/calculate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });

            const result = await response.json();

            if (result.success) {
                this.updateResults(result.result);
            } else {
                this.showError(result.error);
            }

        } catch (error) {
            console.error('计算失败:', error);
            this.showError('网络错误，请检查连接');
        } finally {
            calculateBtn.classList.remove('loading');
            calculateBtn.textContent = '计算';
        }
    }

    updateResults(result) {
        // 更新主要结果
        document.getElementById('required-volume').textContent = `${result.required_volume.toFixed(3)} mL`;
        
        // 更新详细结果
        document.getElementById('current-activity').textContent = `${result.current_activity.toFixed(2)} mCi`;
        document.getElementById('current-concentration').textContent = `${result.current_concentration.toFixed(3)} mCi/mL`;
        document.getElementById('elapsed-time').textContent = `${result.elapsed_minutes.toFixed(1)} 分钟`;

        // 添加结果动画
        this.animateResults();
    }

    clearResults() {
        // 清空主要结果
        document.getElementById('required-volume').textContent = '0.000 mL';
        
        // 清空详细结果
        document.getElementById('current-activity').textContent = '0.00 mCi';
        document.getElementById('current-concentration').textContent = '0.000 mCi/mL';
        document.getElementById('elapsed-time').textContent = '0.0 分钟';
    }

    animateResults() {
        const resultElements = document.querySelectorAll('.result-value');
        resultElements.forEach(element => {
            element.style.animation = 'none';
            element.offsetHeight; // 触发重排
            element.style.animation = 'fadeIn 0.5s ease-out';
        });
    }

    showError(message) {
        // 简单的错误提示
        alert(`计算错误: ${message}`);
    }
}

// 页面加载完成后初始化应用
document.addEventListener('DOMContentLoaded', () => {
    new DoseCalculatorApp();
});

// 添加一些辅助函数
function formatNumber(num, decimals = 3) {
    return Number(num).toFixed(decimals);
}

function validateInput(value, min = 0) {
    const num = parseFloat(value);
    return !isNaN(num) && num >= min;
}

// 添加键盘快捷键支持
document.addEventListener('keydown', (e) => {
    // Ctrl+Enter 或 Cmd+Enter 触发计算
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        e.preventDefault();
        document.getElementById('calculate-btn').click();
    }
    
    // Escape 键清空剂量
    if (e.key === 'Escape') {
        document.getElementById('clear-dose').click();
    }
});

// 添加触摸设备优化
if ('ontouchstart' in window) {
    document.body.classList.add('touch-device');
    
    // 为触摸设备优化按钮大小
    const style = document.createElement('style');
    style.textContent = `
        .touch-device .btn {
            min-height: 44px;
            padding: 12px 24px;
        }
        .touch-device .nuclide-btn {
            min-height: 60px;
        }
        .touch-device input {
            min-height: 44px;
        }
    `;
    document.head.appendChild(style);
}

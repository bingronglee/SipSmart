from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
import os
import logging
from logging.handlers import RotatingFileHandler
import sys

# 配置日誌系統
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 設置日誌檔編碼為UTF-8
handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=3, encoding='utf-8')
handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
logger.addHandler(handler)

# 添加控制台處理器並設置編碼
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(logging.Formatter('%(message)s'))
logger.addHandler(console_handler)

# 應用配置
class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///water_tracker.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

class WaterLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    date = db.Column(db.Date, nullable=False, default=date.today)

class Settings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    daily_goal = db.Column(db.Integer, nullable=False, default=2000)
    reminder_interval = db.Column(db.Integer, nullable=False, default=60)
    notifications_enabled = db.Column(db.Boolean, nullable=False, default=True)
    last_active_date = db.Column(db.Date, nullable=False, default=date.today)

def initialize_database():
    try:
        # 只在資料庫不存在時創建
        if not os.path.exists('water_tracker.db'):
            db.create_all()
            logger.info("資料庫表創建成功")

            # 檢查並創建默認設置
            if not Settings.query.first():
                default_settings = Settings(
                    daily_goal=2000,
                    reminder_interval=60,
                    notifications_enabled=True,
                    last_active_date=date.today()
                )
                db.session.add(default_settings)
                db.session.commit()
                logger.info("默認設置初始化成功")
        else:
            logger.info("資料庫已存在，跳過初始化")
        return True
    except Exception as e:
        logger.error(f"資料庫初始化錯誤: {str(e)}")
        return False

# 在應用上下文中初始化資料庫
with app.app_context():
    if not initialize_database():
        logger.error("資料庫初始化失敗，應用可能無法正常運行")
        sys.exit(1)  # 如果資料庫初始化失敗，終止應用

def check_and_reset_daily_progress():
    settings = Settings.query.first()
    today = date.today()
    
    if settings.last_active_date < today:
        # 更新最後活動日期
        settings.last_active_date = today
        db.session.commit()
        return True
    return False

@app.route('/')
def index():
    settings = Settings.query.first()
    today = date.today()
    
    # 檢查是否需要重置
    check_and_reset_daily_progress()
    
    # 只獲取今天的記錄
    today_logs = WaterLog.query.filter(
        db.func.date(WaterLog.timestamp) == today
    ).all()
    
    total_today = sum(log.amount for log in today_logs)
    percentage = min(int((total_today / settings.daily_goal) * 100), 100)
    
    return render_template('index.html',
                         total_today=total_today,
                         goal=settings.daily_goal,
                         percentage=percentage,
                         settings=settings)

class ValidationError(Exception):
    pass

def validate_water_amount(amount):
    """驗證飲水量是否合理"""
    try:
        amount = int(amount)
        if amount <= 0 or amount > 5000:  # 假設單次最大飲水量為5000ml
            raise ValidationError("飲水量必須在1-5000ml之間")
        return amount
    except ValueError:
        raise ValidationError("飲水量必須是有效的數位")

def validate_settings(daily_goal, reminder_interval):
    """驗證設置參數是否合理"""
    try:
        daily_goal = int(daily_goal)
        reminder_interval = int(reminder_interval)
        
        if daily_goal < 500 or daily_goal > 10000:
            raise ValidationError("每日目標必須在500-10000ml之間")
        if reminder_interval < 15 or reminder_interval > 240:
            raise ValidationError("提醒間隔必須在15-240分鐘之間")
            
        return daily_goal, reminder_interval
    except ValueError:
        raise ValidationError("參數必須是有效的數位")

@app.errorhandler(ValidationError)
def handle_validation_error(error):
    return jsonify({'error': str(error)}), 400

@app.errorhandler(500)
def handle_server_error(error):
    logger.error(f"伺服器錯誤: {str(error)}")
    return jsonify({'error': '伺服器內部錯誤'}), 500

@app.route('/add_water', methods=['POST'])
def add_water():
    try:
        amount = request.json.get('amount')
        amount = validate_water_amount(amount)
        
        check_and_reset_daily_progress()
        
        log = WaterLog(amount=amount, date=date.today())
        db.session.add(log)
        db.session.commit()
        
        today = date.today()
        total_today = WaterLog.query.filter(
            db.func.date(WaterLog.timestamp) == today
        ).with_entities(db.func.sum(WaterLog.amount)).scalar() or 0
        
        settings = Settings.query.first()
        percentage = (total_today / settings.daily_goal) * 100 if settings else 0
        
        return jsonify({
            'success': True,
            'total_today': total_today,
            'percentage': percentage
        })
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"添加飲水記錄時出錯: {str(e)}")
        return jsonify({'error': '伺服器內部錯誤'}), 500

@app.route('/update_settings', methods=['POST'])
def update_settings():
    try:
        data = request.json
        daily_goal = data.get('daily_goal')
        reminder_interval = data.get('reminder_interval')
        notifications_enabled = data.get('notifications_enabled', True)
        
        daily_goal, reminder_interval = validate_settings(daily_goal, reminder_interval)
        
        settings = Settings.query.first()
        if not settings:
            settings = Settings()
            db.session.add(settings)
        
        settings.daily_goal = daily_goal
        settings.reminder_interval = reminder_interval
        settings.notifications_enabled = notifications_enabled
        
        db.session.commit()
        logger.info(f"設置更新成功: 目標={daily_goal}ml, 間隔={reminder_interval}分鐘")
        
        return jsonify({'success': True})
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"更新設置時出錯: {str(e)}")
        return jsonify({'error': '伺服器內部錯誤'}), 500

@app.route('/get_history')
def get_history():
    # 檢查是否需要重置
    check_and_reset_daily_progress()
    
    # 獲取最近的記錄，按日期分組
    logs = WaterLog.query.order_by(WaterLog.timestamp.desc()).limit(10).all()
    history = [{
        'time': log.timestamp.strftime('%Y-%m-%d %H:%M'),
        'amount': log.amount,
        'date': log.timestamp.strftime('%Y-%m-%d')
    } for log in logs]
    return jsonify(history)

if __name__ == '__main__':
    app.run(debug=True)

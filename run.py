from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime

from app import create_app , db
from app.model import Booking

app = create_app()

def delete_past_bookings():
    now = datetime.now()
    with app.app_context():  # Убедитесь, что используете контекст приложения Flask
        # Удаляем записи, где время уже прошло
        db.session.query(Booking).filter(Booking.time < now).delete()
        db.session.commit()
        print("Удалены старые записи, где время прошло.")

# Настройка планировщика задач
scheduler = BackgroundScheduler()
scheduler.add_job(func=delete_past_bookings, trigger="interval", minutes=1)  # Проверка каждый час
scheduler.start()

if __name__ == '__main__':
    app.run(debug=True)







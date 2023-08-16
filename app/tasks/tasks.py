import asyncio
import logging
from celery import Celery

from app.services.ExcelService import initialize_exc, cnt
from app.services.RedisService import RedisService

celery = Celery('tasks', broker='redis://redis:6379', backend='redis://redis:6379')
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@celery.task()
def check_excel_changes():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_async_check_excel_changes())


@celery.task()
async def run_async_check_excel_changes():
    print('Here')
    previous_data, cn = await RedisService().get_excel_data()
    exc = await initialize_exc()
    current_data, df = exc.get_from_xlsx()
    count_ = await cnt(df)
    if previous_data:
        if previous_data == current_data:
            print('No changes')
        else:
            print('check chenges')
            await exc.check(previous_data, current_data)
    await RedisService().save_excel_data(current_data, count_)
    # if a == []:
    #     print("no changes")
    # else:
    #     print("was changes")
    #     print(a)
    #     await updates_data(a)


celery.conf.beat_schedule = {
    'run-me-every-15-seconds': {
        'task': 'app.tasks.tasks.check_excel_changes',
        'schedule': 15.0
    }
}

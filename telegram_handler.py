import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

# 로깅 설정
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# 특정 함수 정의 (예: "go" 명령을 받으면 수행할 함수)
def perform_task():
    from main import test_filter
    # 여기에 원하는 함수를 작성하세요
    result = test_filter()
    return result

# '/start' 명령 처리
async def start(update: Update, context) -> None:
    await update.message.reply_text('안녕하세요! 명령을 입력해주세요.')

# 일반 메시지 처리 (예: "go" 메시지)
async def handle_message(update: Update, context) -> None:
    user_message = update.message.text.lower()

    if user_message == "go":
        # 특정 작업을 수행하고 결과 반환
        result = perform_task()
        await update.message.reply_text(f"결과: {result}")
    else:
        await update.message.reply_text('유효하지 않은 명령입니다. "go"를 입력해주세요.')

# 메인 함수: 봇 실행
def telegtram_main():
    # 텔레그램 봇 토큰
    TOKEN = '7102499363:AAHGgwxkfybyKemrDs8ydeqfYTEVK2g9cdo'  # BotFather로부터 받은 토큰을 입력하세요

    # ApplicationBuilder로 애플리케이션 생성
    app = ApplicationBuilder().token(TOKEN).build()

    # 핸들러 등록
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # 봇 시작
    app.run_polling()  # start_polling() 대신 run_polling() 사용

if __name__ == '__main__':
    telegtram_main()

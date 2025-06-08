# Регистрируем все хендлеры
for handler in handlers:
    dp.include_router(handler.router)

# Регистрируем middleware
dp.message.middleware(LoggingMiddleware())
dp.message.middleware(AdminMiddleware())
dp.message.middleware(AntiFloodMiddleware())
dp.message.middleware(ChatMiddleware())
dp.message.middleware(LearningMiddleware())

# Регистрируем фильтры
dp.message.filter(F.chat.type != "private")

return dp 
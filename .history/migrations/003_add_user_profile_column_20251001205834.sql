-- Добавление новой колонки в таблицу users
ALTER TABLE users ADD COLUMN IF NOT EXISTS profile_data JSONB;

-- Комментарий к таблице и колонке
COMMENT ON TABLE users IS 'Таблица пользователей системы';
COMMENT ON COLUMN users.profile_data IS 'Дополнительные данные профиля в формате JSON';
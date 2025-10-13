-- Создание таблицы заказов
CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER DEFAULT 1,
    total_price DECIMAL(10,2) NOT NULL,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'pending'
);

-- Создание индексов для оптимизации запросов
CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id);
CREATE INDEX IF NOT EXISTS idx_orders_product_id ON orders(product_id);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);

-- Добавление ограничения внешнего ключа (опционально)
-- ALTER TABLE orders ADD CONSTRAINT fk_orders_user_id 
-- FOREIGN KEY (user_id) REFERENCES users(id);

-- Комментарии к таблице и колонкам
COMMENT ON TABLE orders IS 'Таблица заказов пользователей';
COMMENT ON COLUMN orders.user_id IS 'ID пользователя, сделавшего заказ';
COMMENT ON COLUMN orders.product_id IS 'ID заказанного продукта';
COMMENT ON COLUMN orders.status IS 'Статус заказа: pending, completed, cancelled';

-- Вставка тестовых данных
INSERT INTO orders (user_id, product_id, quantity, total_price, status) VALUES
(1, 1, 2, 50.00, 'completed'),
(1, 2, 1, 25.50, 'pending'),
(2, 1, 1, 25.00, 'completed')
ON CONFLICT (id) DO NOTHING;
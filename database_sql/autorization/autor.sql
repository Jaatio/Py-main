
use p4_question;


CREATE TABLE user_info (
    id INT AUTO_INCREMENT PRIMARY KEY,
    role_log ENUM('Менеджер', 'Лаборант', 'Контролер') NOT NULL,
    login VARCHAR(24),
    password VARCHAR(24),
    UNIQUE (login)
);


INSERT INTO user_info (role_log, login, password) VALUES
    ('Менеджер', 'asd', '123');
    
SELECT * FROM user_info;
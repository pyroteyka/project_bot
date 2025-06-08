import sqlite3
from config import *

# Предустановленные навыки и статусы
skills = [(_,) for _ in ['Python', 'SQL', 'API', 'Telegram']]
statuses = [(_,) for _ in ['На этапе проектирования', 'В процессе разработки',
                          'Разработан. Готов к использованию.', 'Обновлен',
                          'Завершен. Не поддерживается']]

class DB_Manager:
    # Инициализация с путём к БД
    def __init__(self, database):
        self.database = database

    # Создание всех таблиц
    def create_tables(self):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.execute('''CREATE TABLE projects (
                project_id INTEGER PRIMARY KEY,
                user_id INTEGER,
                project_name TEXT NOT NULL,
                description TEXT,
                url TEXT,
                status_id INTEGER,
                FOREIGN KEY(status_id) REFERENCES status(status_id))''')
            conn.execute('''CREATE TABLE skills (
                skill_id INTEGER PRIMARY KEY,
                skill_name TEXT)''')
            conn.execute('''CREATE TABLE project_skills (
                project_id INTEGER,
                skill_id INTEGER,
                FOREIGN KEY(project_id) REFERENCES projects(project_id),
                FOREIGN KEY(skill_id) REFERENCES skills(skill_id))''')
            conn.execute('''CREATE TABLE status (
                status_id INTEGER PRIMARY KEY,
                status_name TEXT)''')
            conn.commit()
        print("База данных успешно создана.")

    # Вспомогательный метод для массовых запросов
    def __executemany(self, sql, data):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.executemany(sql, data)
            conn.commit()

    # Вспомогательный метод SELECT-запроса
    def __select_data(self, sql, data=tuple()):
        conn = sqlite3.connect(self.database)
        with conn:
            cur = conn.cursor()
            cur.execute(sql, data)
            return cur.fetchall()

    # Заполнение таблиц значениями по умолчанию
    def default_insert(self):
        self.__executemany('INSERT OR IGNORE INTO skills (skill_name) values(?)', skills)
        self.__executemany('INSERT OR IGNORE INTO status (status_name) values(?)', statuses)

    # Добавление проекта
    def insert_project(self, data):
        sql = 'INSERT OR IGNORE INTO projects (user_id, project_name, url, status_id) values(?, ?, ?, ?)'
        self.__executemany(sql, data)

    # Привязка навыка к проекту
    def insert_skill(self, user_id, project_name, skill):
        project_id = self.__select_data('SELECT project_id FROM projects WHERE project_name = ? AND user_id = ?', (project_name, user_id))[0][0]
        skill_id = self.__select_data('SELECT skill_id FROM skills WHERE skill_name = ?', (skill,))[0][0]
        self.__executemany('INSERT OR IGNORE INTO project_skills VALUES (?, ?)', [(project_id, skill_id)])

    # Получение всех статусов
    def get_statuses(self):
        return self.__select_data('SELECT status_name FROM status')

    # Получение ID статуса по названию
    def get_status_id(self, status_name):
        res = self.__select_data('SELECT status_id FROM status WHERE status_name = ?', (status_name,))
        return res[0][0] if res else None

    # Получение всех проектов пользователя
    def get_projects(self, user_id):
        return self.__select_data('SELECT * FROM projects WHERE user_id = ?', (user_id,))

    # Получение ID проекта по названию
    def get_project_id(self, project_name, user_id):
        return self.__select_data('SELECT project_id FROM projects WHERE project_name = ? AND user_id = ?', (project_name, user_id))[0][0]

    # Получение всех навыков
    def get_skills(self):
        return self.__select_data('SELECT * FROM skills')

    # Получение навыков, связанных с проектом
    def get_project_skills(self, project_name):
        res = self.__select_data('''
            SELECT skill_name FROM projects 
            JOIN project_skills ON projects.project_id = project_skills.project_id 
            JOIN skills ON skills.skill_id = project_skills.skill_id 
            WHERE project_name = ?''', (project_name,))
        return ', '.join([x[0] for x in res])

    # Получение полной информации о проекте
    def get_project_info(self, user_id, project_name):
        return self.__select_data('''
            SELECT project_name, description, url, status_name FROM projects 
            JOIN status ON status.status_id = projects.status_id
            WHERE project_name = ? AND user_id = ?''', (project_name, user_id))

    # Обновление поля в проекте
    def update_projects(self, param, data):
        self.__executemany(f"UPDATE projects SET {param} = ? WHERE project_name = ? AND user_id = ?", [data])

    # Удаление проекта
    def delete_project(self, user_id, project_id):
        self.__executemany("DELETE FROM projects WHERE user_id = ? AND project_id = ?", [(user_id, project_id)])

    # Удаление связи между проектом и навыком
    def delete_skill(self, project_id, skill_id):
        self.__executemany("DELETE FROM project_skills WHERE skill_id = ? AND project_id = ?", [(skill_id, project_id)])

# Тестирование
if __name__ == '__main__':
    manager = DB_Manager(DATABASE)
    manager.create_tables()
    manager.default_insert()
    # manager.insert_skill(...) — примеры тестов здесь

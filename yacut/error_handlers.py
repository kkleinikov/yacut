from http import HTTPStatus

from flask import jsonify, render_template

from yacut import app, db


class InvalidAPIUsage(Exception):
    """
    Исключение для обработки ошибок API с возвращением сообщения в формате
    JSON.

    Используется для унификации ответов от API при возникновении ошибок,
    связанных с неверными запросами или данными. Позволяет возвращать
    пользователю понятное сообщение об ошибке и соответствующий HTTP-код.

    Attributes:
        message (str): Сообщение об ошибке.
        status_code (int): Код HTTP-статуса (по умолчанию 400 — BAD REQUEST).
    """

    status_code = HTTPStatus.BAD_REQUEST

    def __init__(self, message, status_code=None):
        super().__init__()
        self.message = message
        if status_code is not None:
            self.status_code = status_code

    def to_dict(self) -> dict[str, str]:
        """
        Возвращает словарь с данными об ошибке для формирования JSON-ответа.

        Returns:
            dict[str, str]: Словарь с ключом 'message' и значением —
            сообщением об ошибке.
        """
        return dict(message=self.message)


@app.errorhandler(InvalidAPIUsage)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), HTTPStatus.NOT_FOUND


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), HTTPStatus.INTERNAL_SERVER_ERROR

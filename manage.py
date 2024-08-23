from RealProject import create_app
from flask import send_from_directory
import os

app = create_app()


@app.route('/favicon.ico')
def favicon():
    return send_from_directory('app/blog/static/img', 'March-seven.ico')


# 作为入口文件运行项目，app在RealProject中实例化了
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)


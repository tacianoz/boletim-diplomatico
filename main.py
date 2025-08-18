#!/usr/bin/env python3
"""
Aplicação principal para Cloud Run
"""

from app_web import app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)

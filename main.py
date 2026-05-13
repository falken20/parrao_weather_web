# by Richi Rod AKA @richionline / falken20

import os

from src.web import app


if __name__ == "__main__":
    # app.run(debug=True)
    app.run(port=int(os.environ.get("PORT", "5000")))

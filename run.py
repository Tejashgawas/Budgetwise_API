from app import create_app
from app.utils.auth_exceptions import TokenMissingError
app = create_app()

@app.route("/")
def home():
    app.logger.debug("Logger debug message")
    return "Welcome to the BudgetWise Application!"

@app.route("/test-401")
def test_401():
    raise TokenMissingError("You must login to view this page.")

if __name__ == "__main__":
    app.run(debug=True)
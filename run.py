from app import create_app

app = create_app()

@app.route("/")
def home():
    return "Welcome to the BudgetWise Application!"

if __name__ == "__main__":
    app.run(debug=True)
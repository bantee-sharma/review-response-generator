from flask import Flask, render_template, request
from langgraph_workflow import process_review

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    sentiment = None
    response = None
    diagnosis = None
    review = ""

    if request.method == "POST":
        review = request.form.get("review", "")
        if review:
            result = process_review(review)
            sentiment = result.get("sentiment", "")
            response = result.get("response", "")
            diagnosis = result.get("diagnosis")

    return render_template("index.html",
                           review=review,
                           sentiment=sentiment,
                           response=response,
                           diagnosis=diagnosis)

if __name__ == "__main__":
    app.run(debug=True)

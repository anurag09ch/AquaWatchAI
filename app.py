
from flask import Flask, render_template, request
import pickle
import pandas as pd

app = Flask(__name__)

with open("aquawatch_model.pkl", "rb") as file:
    model = pickle.load(file)


@app.route("/", methods=["GET", "POST"])
def home():
    result = None
    probability = None
    message = None
    result_type = None

    if request.method == "POST":
        try:
            household_size = int(request.form["household_size"])
            daily_usage = float(request.form["daily_usage"])
            night_usage = float(request.form["night_usage"])
            high_usage_days = int(request.form["high_usage_days"])

            if (
                household_size < 1
                or daily_usage < 0
                or night_usage < 0
                or high_usage_days < 0
            ):
                raise ValueError

            input_data = pd.DataFrame([{
                "household_size": household_size,
                "daily_usage": daily_usage,
                "night_usage": night_usage,
                "high_usage_days": high_usage_days
            }])

            print("INPUT SENT TO MODEL:")
            print(input_data)

            prediction = model.predict(input_data)[0]
            probabilities = model.predict_proba(input_data)[0]

            print("PREDICTION:", prediction)
            print("PROBABILITIES:", probabilities)

            probability = round(float(probabilities[1]) * 100, 1)

            if prediction == 1:
                result = "Possible Unusual Water Usage"
                result_type = "warning"
                message = (
                    "Your water usage pattern may indicate a leak. "
                    "Check your water meter and household plumbing."
                )
            else:
                result = "No Strong Leak Signal Detected"
                result_type = "normal"
                message = (
                    "Your current water usage pattern does not "
                    "show a strong leak signal."
                )

        except (ValueError, TypeError):
            message = "Please enter valid, non-negative numbers."

    return render_template(
        "index.html",
        result=result,
        probability=probability,
        message=message,
        result_type=result_type
    )


if __name__ == "__main__":
    app.run(debug=True)

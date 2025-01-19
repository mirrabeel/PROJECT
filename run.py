from my_app import create_app
from my_app import app, db

app = create_app()

# ამ ბრძანებით შექმნათ მონაცემთა ბაზა
with app.app_context():
    db.create_all() # შექმნის მინაცემთა ბაზის ცხრილებს

# ფლასკ აპლიკაციის გაშვება
if __name__ == "__main__":
    app.run(debug=True)
from website import create_app, db
from website.models import User
from slugify import slugify

app = create_app()

with app.app_context():
    for user in User.query.all():
        user.slug = slugify(user.name)
    db.session.commit()
    print("Slugs updated successfully!")

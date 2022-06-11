git fetch --all
git reset --hard origin/main

python manage.py collectstatic

cd reactapp

git fetch --all
git reset --hard origin/build

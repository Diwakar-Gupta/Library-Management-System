git fetch --all
git reset --hard origin/main

cd reactapp

git fetch --all
git reset --hard origin/build

cd ..
python manage.py collectstatic


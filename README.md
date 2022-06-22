https://www.educative.io/courses/grokking-the-object-oriented-design-interview/RMlM3NgjAyR#Use-case-diagram

Live at: https://diwakar.pythonanywhere.com/

### Rest Api
https://www.django-rest-framework.org/api-guide/generic-views/#generic-views
https://www.django-rest-framework.org/tutorial/3-class-based-views/

#### Rest Token Auth

```post http://127.0.0.1:8000/api-token-auth/ {username:abrar, password:abrar}```

```curl -X GET http://127.0.0.1:8000/book/9865232658/  -H "Authorization: Token 12b85098b8ec8df108fe0cd6d7576ac362ae04a7"```

#### Backup Data
python manage.py dumpdata --natural-foreign --natural-primary -e contenttypes > dummy_data.json
#### Restore Data
python manage.py loaddata dummy_data.json

#### Test Suit
https://zerotobyte.com/django-multiple-databases-setup/

#### filter ListView
https://www.geeksforgeeks.org/filter-data-in-django-rest-framework/

#### Cached System

Cached is stored in:
1. Database
2. Filesystem
3. Memory : kind of bad because not permanent



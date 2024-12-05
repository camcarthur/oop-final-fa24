# Object Oriented Programming Final - Banking Web App

## Group Members

Colin McArthur, Jake Peterson, and Carlos Ortiz

---

## Description

For our project we are going create a psuedo bank website that has functionality to track multiple
users with individual accounts ([Abstract](/abstract.txt)).

<br>

The flask server runs on port 5000 by default

**Key Features:**
- Password Hashing
- Database
- Clean User Interface
- User Authentication
- Error Handling (overdraws, rollbacks, account validation, etc.)
- Multiple Bank Account Types
- User Roles (user, admin w/ admin page)
- Internal & External Transfer Capabilities
- Transaction History (with filtering functionality)

---

## How to Run

```bash
pip install -r requirements.txt
```

```bash
make run
```

<br>

Drop the database then remake:
```bash
sudo -u postgres psql
DROP DATABASE banking_db;
python3 database/setup_db.py
python3 python3 -m database.init_db
```
Then you should be able to:
```bash
make run
```

---

## How to Test

```bash
make run-test
```

[HTML coverage report](./htmlcov/index.html)

---

# Judges' Average Score

**Judge**: 55/45

**Average Score**: 55/45

---

# Team Self-Grade

Each requirement score is between 0-5 (0 - F, 1 - Needs improvement, 2 - Poor, 3 - Fair, 4 – Good, 5 - Excellent)

| Rubric Requirement | Score | Justification |
| ------------------ | ----- | ------------- |
| 1. Use of fundamental OOD concept | 5 | Used getters and setters where necessary. Used attributes and methods according to OOD principles. The singleton is an abstract class. Inheritance is used with the command pattern for the withdraw and deposit classes. |
| 2. Use of at least 3 Design Patterns | 5 | Used Singleton, Command, and Decorator Patterns. |
| 3. Testing for correctness | 4 | Do not have full coverage, however we do have a big chunk of it (considering the size of our project). |
| 4. Documentation | 5 | The README document explains how to run the application, as well as a basic overview of the capabilities of the application. UML's overview how each object interacts with one another. |
| 5. Software Management | 4 | Kept up with each other- good communication. Used a texting groupchat and Discord server to track progress. GitHub repo w/ individual branches for each persons workload. Didn't use a dedicated SW management tool like Jira. |
| 6. Teamwork | 5 | Everyone did what they said they would. No one dropped the bar. Had multiple, frequent in-person meetings to go over progress and things to get done. |
| 7. Project requirements and execution | 5 | Project is more than adequate for a Sophomore/Junior level CS student. |
| 8. Team presentation | 5 | Went over all aspects of the rubric. Presentation was concise with a good demonstration of the app and its features. |
| 9. Use 4+1 views to explain design to audience | 4 | We created all views before and after development to give us a development reference, but also reflect finished product. Some more time could've been put into tidiness. |
| 10. Above and Beyond (Extra credit /10) | 10 | Solid User Interface, used a database, simulates a real world banking web application, and built a CI/CD Pipeline. If we had a client, I'm sure they would be happy with the delivered product. |

**Total**: 52/45

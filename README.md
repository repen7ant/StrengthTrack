# StrengthTrack

Welcome to **StrengthTrack** – a comprehensive solution to track your strength training progress, manage personal bests, and generate structured mesocycles.

---

## Local Installation

Follow these steps to set up StrengthTrack on your local machine:

### 1. Clone the Repository

```bash
git clone https://github.com/repen7ant/StrengthTrack.git
cd StrengthTrack
```

### 2. Create and Activate a Virtual Environment

```bash
python -m venv venv
# On Unix/Linux/macOS:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root and specify your settings:
```env
DJANGO_SECRET_KEY=your_secret_key_here
DEBUG=False
```

### 5. Apply Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Populate Exercises

This command will add the initial list of exercises:

```bash
python manage.py populate_exercises
```

### 7. Start the Server

```bash
python manage.py runserver
```

Visit http://127.0.0.1:8000/ to access the app in your browser.

---

## Screenshots

![Main Page](screenshots/home.png)
*Home page after launching the server*

![Profile Page](screenshots/profile.png)
*User profile with best sets*

![Add Best Set](screenshots/add_set.png)
*Form for adding or editing personal best sets*

![Mesocycle Generation](screenshots/mesocycle.png)
*Generated 4-week mesocycle based on best sets*

![Progress Chart](screenshots/progress.png)
*1RM progress over time, with per-exercise charts*

---

## Architecture Overview

**StrengthTrack** is built on Django with a modular, domain-driven architecture:

### Main Components

- **Users & Profiles:**  
  The `UserProfile` model extends Django's core user, creating a profile for training-related data.
  
- **Exercises:**  
  The `Exercise` model contains a catalog of lift/exercise names.

- **BestSet:**  
  The `BestSet` model stores the user's best result (weight × repetitions) per exercise, automatically calculating the Brzycki-estimated 1RM:
  ```
  1RM = weight / (1.0278 - 0.0278 * reps)
  ```
  All historical bests are kept in `BestSetHistory`.
  
- **Mesocycles:**  
  The `Mesocycle` model organizes structured 4-week training blocks, auto-generated per main exercise and user bests, with periodized intensity (RPE, reps, weight progression formula).

- **Services:**  
  Business logic sits in the `services/` layer (e.g. `BestSetService`, `MesocycleService`, `ProfileService`, `ProgressService`).  
  - `BestSetService`: Adds, updates, deletes user bests, manages validations and history.
  - `MesocycleService`: Generates and retrieves mesocycles per user, groups results, handles exercise weight rounding.
  - `ProfileService`: Fetches best sets for user profiles.
  - `ProgressService`: Builds 1RM progress series for charts.

- **Forms:**  
  - Registration and profile updates (`UserRegisterForm`, `UserUpdateForm`)
  - Best set entry and validation (`BestSetForm`)
  - All forms leverage `django-crispy-forms` for clean Bootstrap layouts.

- **Views:**  
  Django function views handle rendering, form processing, login restrictions, and service interaction:
    - `/`                  – Home page (`core/views.py`)
    - `/accounts/profile/` – Profile with best sets, CRUD operations
    - `/accounts/mesocycle/` – Mesocycle creator & list
    - `/accounts/progress/` – Progress chart for all exercises
    - Auth routes for login, registration

- **Templates:**  
  - Stored in `core/templates/core` and `core/templates/accounts`.
  - Support registration, login, main screens, forms, lists, popups, and charts.

---

### Data Flow

1. **User registers or logs in**
2. **Adds best sets** (weight, reps, exercise) via forms
   - Existing bests are validated & updated only if new best 1RM > old 1RM
   - Old best sets moved to history
3. **Generates mesocycles**
   - System pre-loads main barbell lifts
   - 4-week training block created, with periodized intensity/reps/weight
4. **Tracks all best set progress**
   - 1RM improvements and history displayed as charts

---

### Tech Stack

- Django (core backend)
- SQLite (database)
- Crispy Forms with Bootstrap (front-end forms, styling)
- HTML templates
- Chart.js for progress visualization

---

## FAQ / Notes

- To access Django admin:  
  `python manage.py createsuperuser`
- Do **not** commit your `.env` or secret keys to version control!
- If you want to pre-load more exercises, modify `core/management/commands/populate_exercises.py`.

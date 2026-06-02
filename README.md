# EcoTrack

A community recycling and upcycling marketplace built with Django — share, claim, and coordinate free items in your neighborhood.
 
## Features

- Browse and post free items with images and location
- Claim workflow for items with donor approval
- User accounts with social login (Google, GitHub)
- Notifications and a simple dashboard for donors/claimants
- Map view using Leaflet for item locations
- Modern responsive UI powered by Tailwind CSS

## Tech Stack

- Python / Django
- Tailwind CSS
- Leaflet (maps)
- Django Allauth (authentication + social logins)

## Quickstart (Local Development)

1. Clone the repo and open the project root (where `manage.py` lives):

   cd ECOTRACK-main/ECOTRACK-main

2. Create and activate a virtual environment (example using venv):

   python -m venv .venv
   # Windows (PowerShell)
   .\.venv\Scripts\Activate.ps1
   # macOS / Linux
   source .venv/bin/activate

3. Install Python dependencies:

   pip install -r requirements.txt

4. Create and apply database migrations:

   python manage.py migrate

5. (Optional) Create a superuser to access the admin site:

   python manage.py createsuperuser

6. (Optional) Build Tailwind CSS (if you plan to edit styles):

   # requires Node.js and npm
   npm install
   npx tailwindcss -i ./static/src/input.css -o ./static/dist/output.css --watch

   The project includes a prebuilt stylesheet at `static/dist/output.css`.

7. Collect static files (for production/static testing):

   python manage.py collectstatic --noinput

8. Run the development server:

   python manage.py runserver

Open http://127.0.0.1:8000 in your browser.

## Configuration / Environment

- Set `SECRET_KEY` and `DEBUG` in your environment or `settings.py` for local development.
- Configure `ALLOWED_HOSTS` when deploying to production.

## Important Files

- [manage.py](ECOTRACK-main/ECOTRACK-main/manage.py) — Django entrypoint
- [requirements.txt](ECOTRACK-main/ECOTRACK-main/requirements.txt) — Python dependencies
- [tailwind.config.js](ECOTRACK-main/ECOTRACK-main/tailwind.config.js) — Tailwind configuration
- [static/src/input.css](ECOTRACK-main/ECOTRACK-main/static/src/input.css) — Tailwind input
- [static/dist/output.css](ECOTRACK-main/ECOTRACK-main/static/dist/output.css) — Prebuilt stylesheet
- [templates/base.html](ECOTRACK-main/ECOTRACK-main/templates/base.html) — Global layout & shell

## Accessibility & UX Notes

- Responsive layout and accessible tab controls are implemented in templates.
- Use semantic HTML and focus-visible styles when extending components.

## Contributing

- Fork the repo, open a feature branch, and send a pull request.
- Run tests and linters (if added) before submitting PRs.

## License

MIT — see LICENSE (add one if needed).

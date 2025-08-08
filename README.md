# familyhub-mealboard

## Google Calendar dinner plans

The application can fetch upcoming dinner plans from a shared Google Calendar.
Events within a 7‑day window around today are returned by the `/api/meals`
endpoint as a dictionary keyed by ISO date strings.

### Setup
1. **Create a Google service account** and download its JSON key.
2. **Share the calendar** with the service account's e‑mail (read access is
   enough).
3. Set the following environment variables:

   - `GOOGLE_APPLICATION_CREDENTIALS`: Path to the downloaded JSON key file.
   - `FAMILYHUB_CALENDAR_ID`: ID of the shared calendar.
   - Optional `FAMILYHUB_TZ`: Timezone name (defaults to `America/Chicago`).

With these variables configured, the `/api/meals` route will return the
meal plan as JSON and can be consumed by the frontend.
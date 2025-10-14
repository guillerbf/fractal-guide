# Fractal Guide MVP

Run the Streamlit app locally:

1) Install deps

```
poetry install
```

2) Export your OpenAI key

```
cp .env.example .env
echo "OPENAI_API_KEY=sk-..." >> .env
```

3) Launch the app

```
poetry run streamlit run fractal_guide/app.py
```

Notes:
- On mobile, allow location and camera permissions when prompted.
- If reverse geocoding fails, the app will still show approximate coordinates.

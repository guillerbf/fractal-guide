Flow:
- Reverse-geocode to a place string → “You’re in/near Piazza X.”
- System prompt: “You are a local guide. Use only location context + user photo/text. If unsure, ask.”
- User sees a 60–90s overview; follow-ups use the same thread context.
- When entering a church, append “User is inside [Church Name]” to context.

Protective tweaks:
- Always ask one clarifier when ambiguity > threshold: “Is this the Fountain of the Four Rivers or the Church of Sant’Agnese in Agone?” with two tappable chips.
- Add a style rule: “If you don’t know the exact artist/date, give a range and say you’re unsure.”
- Strip absolutes: prefer “likely”, “generally attributed to” when confidence is low.
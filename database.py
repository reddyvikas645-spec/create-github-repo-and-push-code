import sqlite3

# Connect to SQLite database
connection = sqlite3.connect("tourism.db")
cursor = connection.cursor()

# Create places table
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS places (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        state TEXT NOT NULL,
        description TEXT,
        history TEXT,
        attractions TEXT,
        hotel TEXT,
        food TEXT
    )
    """
)

# Add tourist places
places = [
    (
        "Taj Mahal",
        "Agra, Uttar Pradesh",
        "The Taj Mahal is one of India's most famous monuments.",
        "The Taj Mahal was built by Mughal emperor Shah Jahan in memory of Mumtaz Mahal.",
        "Taj Mahal, Agra Fort, Mehtab Bagh",
        "Hotel Taj Resorts, Hotel Atithi",
        "Petha, Mughlai Food",
    ),
    (
        "Goa",
        "Goa",
        "Goa is famous for beaches, nightlife and Portuguese heritage.",
        "Goa has a rich history influenced by Portuguese culture and Indian traditions.",
        "Baga Beach, Calangute Beach, Fort Aguada",
        "Taj Exotica, Resort Rio",
        "Fish Curry, Vindaloo",
    ),
    (
        "Mysore Palace",
        "Mysuru, Karnataka",
        "Mysore Palace is a famous historical palace in Karnataka.",
        "The palace was associated with the Wadiyar dynasty and was rebuilt in the early 20th century.",
        "Mysore Palace, Chamundi Hills, Brindavan Gardens",
        "Radisson Blu, Hotel Pai Vista",
        "Mysore Pak, Dosa",
    ),
    (
        "Hampi",
        "Karnataka",
        "Hampi is famous for ancient temples, ruins and beautiful landscapes.",
        "Hampi was the capital of the Vijayanagara Empire.",
        "Virupaksha Temple, Vittala Temple, Hampi Bazaar",
        "Clarks Inn, Hampi Heritage",
        "Bisi Bele Bath, Dosa",
    ),
    (
        "Kerala",
        "Kerala",
        "Kerala is famous for backwaters, beaches, mountains and natural beauty.",
        "Kerala has a long history connected with spice trade and maritime commerce.",
        "Alleppey, Munnar, Kochi",
        "Kumarakom Lake Resort, Abad Turtle Beach",
        "Appam, Kerala Sadya",
    ),
]

# Insert data
cursor.executemany(
    """
    INSERT INTO places
    (name, state, description, history, attractions, hotel, food)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """,
    places,
)

# Save changes
connection.commit()

# Close database
connection.close()

print("Database created successfully!")
print("Tourist places added successfully!")

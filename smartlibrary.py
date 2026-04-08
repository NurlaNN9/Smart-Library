import flet as ft
import sqlite3
import hashlib
import os
import re
# ─── Database setup ──────────────────────────────────────────
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "smartlib_users.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT    UNIQUE NOT NULL,
            email    TEXT    UNIQUE NOT NULL,
            password TEXT    NOT NULL,
            created  TEXT    DEFAULT (datetime('now'))
        )
    """)
    conn.commit()
    conn.close()

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def db_register(username, email, password):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                  (username.strip(), email.strip().lower(), hash_password(password)))
        conn.commit()
        conn.close()
        return True, "Account created!"
    except sqlite3.IntegrityError as e:
        msg = "Username already taken." if "username" in str(e) else "Email already registered."
        return False, msg

def db_login(username_or_email, password):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    val = username_or_email.strip().lower()
    c.execute(
        "SELECT id, username, email FROM users WHERE (LOWER(username)=? OR LOWER(email)=?) AND password=?",
        (val, val, hash_password(password))
    )
    row = c.fetchone()
    conn.close()
    if row:
        return True, "Welcome back!", {"id": row[0], "username": row[1], "email": row[2]}
    return False, "Invalid username or password.", {}

init_db()


# ─── Colour tokens ────────────────────────────────────────────
LIGHT_BG_DARK = "#f5f7fb"
LIGHT_BG_CARD = "#ffffff"
LIGHT_BG_NAV = "#eef2f7"
LIGHT_TEXT_PRI = "#1f2937"
LIGHT_TEXT_SEC = "#6b7280"
LIGHT_BORDER = "#d1d5db"
LIGHT_PALE_PURP = "#4f46e5"
#------------------------
BG_DARK   = "#0f0f13"
BG_CARD   = "#1a1a24"
BG_NAV    = "#12121e"
ACCENT    = "#6c63ff"
ACCENT2   = "#a78bfa"
TEXT_PRI  = "#f0f0f8"
TEXT_SEC  = "#8888aa"
TAG_PHY   = "#6c63ff"
TAG_EBOOK = "#22c55e"
BORDER    = "#2a2a3a"
PALE_PURP = "#d1d1f0"

# ─── Book data ───────────────────────────────────────────────
BOOKS = [
    {"title": "1984",                         "author": "George Orwell",       "genre": "Fiction",          "tag": "Physical", "tag_col": TAG_PHY,   "cover": "https://m.media-amazon.com/images/S/compressed.photo.goodreads.com/books/1327144697i/3744438.jpg", "icon": "remove_red_eye"},
    {"title": "The Age of AI",  "author": "Kissinger, Schmidt, Huttenlocher",  "genre": "Technology",  "tag": "E-Book",  "tag_col": TAG_EBOOK,  "cover": "https://m.media-amazon.com/images/I/51iRpsYsVqL._SL500_.jpg",  "icon": "psychology"},
    {"title": "The Social Network",                   "author": "Ben Mezrich",        "genre": "Business",  "tag": "E-Book",   "tag_col": TAG_EBOOK, "cover": "https://m.media-amazon.com/images/I/814tEvXpsyL._AC_UF1000,1000_QL80_.jpg", "icon": "group"},
    {"title": "Surely You're Joking, Mr. Feynman!",      "author": "Richard Feynman",    "genre": "Science",     "tag": "E-Book",   "tag_col": TAG_EBOOK, "cover": "https://static.insales-cdn.com/images/products/1/4717/698307181/9781784877798.jpg", "icon": "science"},
    {"title": "Homo Deus",                            "author": "Yuval Noah Harari",  "genre": "History",   "tag": "Physical", "tag_col": TAG_PHY,   "cover": "https://m.media-amazon.com/images/I/71FX96Ae-PL._AC_UF1000,1000_QL80_.jpg", "icon": "history_edu"},
    {"title": "The Great Gatsby",              "author": "F. Scott Fitzgerald", "genre": "Fiction",          "tag": "E-Book",   "tag_col": TAG_EBOOK, "cover": "https://cdn.waterstones.com/bookjackets/large/9781/5248/9781524879761.jpg", "icon": "auto_stories"},
    {"title": "Sapiens: A Brief History",      "author": "Yuval Noah Harari",   "genre": "History",          "tag": "Physical", "tag_col": TAG_PHY,   "cover": "https://m.media-amazon.com/images/I/712Uo++xK2L._AC_UF1000,1000_QL80_.jpg", "icon": "history_edu"},
    {"title": "Outliers",                                "author": "Malcolm Gladwell",   "genre": "Psychology",  "tag": "E-Book",   "tag_col": TAG_EBOOK, "cover": "https://m.media-amazon.com/images/S/compressed.photo.goodreads.com/books/1344266315i/3228917.jpg", "icon": "star"},
    {"title": "The Hitchhiker's Guide to the Galaxy",    "author": "Douglas Adams",      "genre": "Fiction",     "tag": "Physical", "tag_col": TAG_PHY,   "cover": "https://m.media-amazon.com/images/I/81BbVc2uRIL._AC_UF1000,1000_QL80_.jpg", "icon": "rocket_launch"},
    {"title": "The Phoenix Project",                     "author": "Gene Kim",           "genre": "Technology",  "tag": "Physical", "tag_col": TAG_PHY,   "cover": "https://itrevolution.com/wp-content/uploads/2018/02/TPP_Front_4th-ed_foil-comp_RGB-scaled.jpg", "icon": "developer_mode"},
    {"title": "Python for Data Analysis",      "author": "Wes McKinney",        "genre": "Technology",       "tag": "E-Book",   "tag_col": TAG_EBOOK, "cover": "https://wesmckinney.com/book/images/cover.png", "icon": "code"},
    {"title": "Designing Data-Intensive Apps", "author": "Martin Kleppmann",    "genre": "Technology",       "tag": "Physical", "tag_col": TAG_PHY,   "cover": "https://www.oreilly.com/covers/urn:orm:book:9781491903063/300w/", "icon": "storage"},
    {"title": "Thinking, Fast and Slow",       "author": "Daniel Kahneman",     "genre": "Psychology",       "tag": "E-Book",   "tag_col": TAG_EBOOK, "cover": "https://m.media-amazon.com/images/I/61fdrEuPJwL._AC_UF1000,1000_QL80_.jpg", "icon": "psychology"},
    {"title": "The Lean Startup",              "author": "Eric Ries",           "genre": "Business",         "tag": "Physical", "tag_col": TAG_PHY,   "cover": "https://m.media-amazon.com/images/I/71sxTeZIi6L._AC_UF1000,1000_QL80_.jpg", "icon": "rocket_launch"},
    {"title": "Guns, Germs, and Steel",        "author": "Jared Diamond",       "genre": "History",          "tag": "E-Book",   "tag_col": TAG_EBOOK, "cover": "https://m.media-amazon.com/images/I/61V8g4GgqdL._AC_UF1000,1000_QL80_.jpg", "icon": "public"},
    {"title": "Deep Learning",                 "author": "Ian Goodfellow",      "genre": "Technology",       "tag": "Physical", "tag_col": TAG_PHY,   "cover": "https://mit-press-new-us.imgix.net/covers/9780262035613.jpg?auto=format&w=298", "icon": "memory"},
    {"title": "Superintelligence",             "author": "Nick Bostrom",         "genre": "Technology",       "tag": "E-Book",   "tag_col": TAG_EBOOK, "cover": "https://m.media-amazon.com/images/I/71UvMcdcE9L._AC_UF1000,1000_QL80_.jpg", "icon": "psychology"},
    {"title": "The Pragmatic Programmer",      "author": "Andrew Hunt",         "genre": "Technology",       "tag": "Physical", "tag_col": TAG_PHY,   "cover": "https://m.media-amazon.com/images/I/71f1jieYHNL._AC_UF1000,1000_QL80_.jpg", "icon": "code"},
    {"title": "Zero to One",                   "author": "Peter Thiel",         "genre": "Business",         "tag": "E-Book",   "tag_col": TAG_EBOOK, "cover": "https://m.media-amazon.com/images/I/71uAI28kJuL.jpg", "icon": "rocket_launch"},
    {"title": "Shoe Dog",                     "author": "Phil Knight",         "genre": "Business",         "tag": "Physical", "tag_col": TAG_PHY,   "cover": "https://upload.wikimedia.org/wikipedia/commons/d/df/Shoe_dog_book_cover.jpg", "icon": "directions_run"},
    {"title": "Atomic Habits",                "author": "James Clear",         "genre": "Self-Help",        "tag": "E-Book",   "tag_col": TAG_EBOOK, "cover": "https://jamesclear.com/wp-content/uploads/2025/06/atomic-habits-dots.png", "icon": "loop"},
    {"title": "Clean Code",                    "author": "Robert C. Martin",    "genre": "Technology",       "tag": "Physical", "tag_col": TAG_PHY,   "cover": "https://www.oreilly.com/library/cover/9780136083238/1200w630h/", "icon": "menu_book"},
    {"title": "Brave New World",              "author": "Aldous Huxley",       "genre": "Fiction",          "tag": "E-Book",   "tag_col": TAG_EBOOK, "cover": "https://m.media-amazon.com/images/I/71GNqqXuN3L._AC_UF1000,1000_QL80_.jpg", "icon": "science"},
    {"title": "The Mythical Man-Month",       "author": "Frederick Brooks",    "genre": "Technology",       "tag": "Physical", "tag_col": TAG_PHY,   "cover": "https://m.media-amazon.com/images/S/compressed.photo.goodreads.com/books/1348430512i/13629.jpg", "icon": "groups"},
    {"title": "Computer Networking",          "author": "James Kurose",        "genre": "Technology",       "tag": "E-Book",   "tag_col": TAG_EBOOK, "cover": "https://m.media-amazon.com/images/I/81ewUnANZPL._AC_UF1000,1000_QL80_.jpg", "icon": "router"},
    {"title": "Code",                         "author": "Charles Petzold",     "genre": "Technology",       "tag": "Physical", "tag_col": TAG_PHY,   "cover": "https://m.media-amazon.com/images/I/61Hc-9h+-XL._AC_UF1000,1000_QL80_.jpg", "icon": "settings_input_component"},
    {"title": "Rich Dad Poor Dad",            "author": "Robert Kiyosaki",     "genre": "Business",         "tag": "E-Book",   "tag_col": TAG_EBOOK, "cover": "https://m.media-amazon.com/images/I/81N9xAIkohL._AC_UF1000,1000_QL80_.jpg", "icon": "attach_money"},
    {"title": "A Brief History of Time",      "author": "Stephen Hawking",     "genre": "Science",          "tag": "Physical", "tag_col": TAG_PHY,   "cover": "https://shop.rmg.co.uk/cdn/shop/products/brief-history-of-time.jpg?v=1739787294", "icon": "flare"},
    {"title": "The Selfish Gene",             "author": "Richard Dawkins",     "genre": "Science",          "tag": "E-Book",   "tag_col": TAG_EBOOK, "cover": "https://cdn.webshopapp.com/shops/297859/files/320363663/700x700x2/richard-dawkins-the-selfish-gene.jpg", "icon": "biotech"},
    {"title": "Fahrenheit 451",               "author": "Ray Bradbury",        "genre": "Fiction",          "tag": "Physical", "tag_col": TAG_PHY,   "cover": "https://upload.wikimedia.org/wikipedia/en/d/db/Fahrenheit_451_1st_ed_cover.jpg", "icon": "local_fire_department"},
    {"title": "The Alchemist",                "author": "Paulo Coelho",        "genre": "Fiction",          "tag": "E-Book",   "tag_col": TAG_EBOOK, "cover": "https://static.wixstatic.com/media/8cc233_da3154cf2cdd4e979a841903fb3cf770~mv2.jpg/v1/fill/w_1585,h_2400,al_c,q_90/The%20Alchemist%20cover.jpg", "icon": "diamond"},
    {"title": "Man's Search for Meaning",     "author": "Viktor Frankl",       "genre": "Psychology",       "tag": "Physical", "tag_col": TAG_PHY,   "cover": "https://m.media-amazon.com/images/I/819Pl1nP0ZL.jpg", "icon": "self_improvement"},
    {"title": "Life 3.0",                     "author": "Max Tegmark",         "genre": "Technology",       "tag": "E-Book",   "tag_col": TAG_EBOOK, "cover": "https://m.media-amazon.com/images/I/71nZodv-FSL._AC_UF1000,1000_QL80_.jpg", "icon": "science"},
    {"title": "Human Compatible",             "author": "Stuart Russell",      "genre": "Technology",       "tag": "Physical", "tag_col": TAG_PHY,   "cover": "https://m.media-amazon.com/images/S/compressed.photo.goodreads.com/books/1561637199i/44767248.jpg", "icon": "psychology"},
    {"title": "The Alignment Problem",        "author": "Brian Christian",     "genre": "Technology",       "tag": "E-Book",   "tag_col": TAG_EBOOK, "cover": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRQamM15zj4KSsF5w-h3NL47DxUOYt6KmXGmg&s", "icon": "balance"},
    {"title": "Introduction to Algorithms",   "author": "Cormen, Leiserson",    "genre": "Technology",       "tag": "Physical", "tag_col": TAG_PHY,   "cover": "https://mit-press-new-us.imgix.net/covers/9780262046305.jpg?auto=format&w=298", "icon": "functions"},
    {"title": "Art of Computer Programming",   "author": "Donald Knuth",        "genre": "Technology",       "tag": "E-Book",   "tag_col": TAG_EBOOK, "cover": "https://m.media-amazon.com/images/I/61tIrzRmFdL._AC_UF1000,1000_QL80_.jpg", "icon": "terminal"},
    {"title": "The Subtle Art of Not Giving a F*ck", "author": "Mark Manson",        "genre": "Self-Help", "tag": "E-Book",   "tag_col": TAG_EBOOK, "cover": "https://m.media-amazon.com/images/I/71QKQ9mwV7L._AC_UF1000,1000_QL80_.jpg", "icon": "self_improvement"},
    {"title": "Hands-On Machine Learning",    "author": "Aurélien Géron",      "genre": "Technology",       "tag": "Physical", "tag_col": TAG_PHY,   "cover": "https://m.media-amazon.com/images/I/81qHV3ACapL._AC_UF1000,1000_QL80_.jpg", "icon": "model_training"},
    {"title": "Good to Great",                "author": "Jim Collins",         "genre": "Business",         "tag": "E-Book",   "tag_col": TAG_EBOOK, "cover": "https://m.media-amazon.com/images/I/51IPJiX34fL._AC_UF1000,1000_QL80_.jpg", "icon": "trending_up"},
    {"title": "The Hard Thing About Hard Things", "author": "Ben Horowitz",    "genre": "Business",         "tag": "Physical", "tag_col": TAG_PHY,   "cover": "https://m.media-amazon.com/images/I/81hMWhbHKAL._AC_UF1000,1000_QL80_.jpg", "icon": "work_history"},
    {"title": "Blue Ocean Strategy",          "author": "Chan Kim",            "genre": "Business",         "tag": "E-Book",   "tag_col": TAG_EBOOK, "cover": "https://m.media-amazon.com/images/I/91YCWH4jFdL._AC_UF1000,1000_QL80_.jpg", "icon": "sailing"},
    {"title": "Start with Why",               "author": "Simon Sinek",         "genre": "Business",         "tag": "Physical", "tag_col": TAG_PHY,   "cover": "https://m.media-amazon.com/images/I/71NBZIExBCL._AC_UF1000,1000_QL80_.jpg", "icon": "lightbulb"},
    {"title": "Deep Work",                    "author": "Cal Newport",         "genre": "Self-Help",        "tag": "E-Book",   "tag_col": TAG_EBOOK, "cover": "https://m.media-amazon.com/images/I/71pqZChaJkL._AC_UF894,1000_QL80_.jpg", "icon": "timer"},
    {"title": "Grit",                         "author": "Angela Duckworth",    "genre": "Psychology",       "tag": "Physical", "tag_col": TAG_PHY,   "cover": "https://m.media-amazon.com/images/S/compressed.photo.goodreads.com/books/1632024090i/27213329.jpg", "icon": "mountain"},
    {"title": "Thinking in Bets",             "author": "Annie Duke",          "genre": "Business",         "tag": "E-Book",   "tag_col": TAG_EBOOK, "cover": "https://m.media-amazon.com/images/I/71WOIOz0ihL._AC_UF1000,1000_QL80_.jpg", "icon": "casino"},
    {"title": "Flow",                         "author": "M. Csikszentmihalyi", "genre": "Psychology",       "tag": "Physical", "tag_col": TAG_PHY,   "cover": "https://m.media-amazon.com/images/I/610GM3WYL7L._AC_UF1000,1000_QL80_.jpg", "icon": "water_drop"},
    {"title": "The Picture of Dorian Gray",   "author": "Oscar Wilde",         "genre": "Fiction",          "tag": "E-Book",   "tag_col": TAG_EBOOK, "cover": "https://d28hgpri8am2if.cloudfront.net/book_images/onix/cvr9781625587534/the-picture-of-dorian-gray-9781625587534_hr.jpg", "icon": "portrait"},
    {"title": "Pride and Prejudice",          "author": "Jane Austen",         "genre": "Fiction",          "tag": "Physical", "tag_col": TAG_PHY,   "cover": "https://m.media-amazon.com/images/I/81Scutrtj4L._UF1000,1000_QL80_.jpg", "icon": "favorite"},
    {"title": "The Catcher in the Rye",       "author": "J.D. Salinger",       "genre": "Fiction",          "tag": "E-Book",   "tag_col": TAG_EBOOK, "cover": "https://m.media-amazon.com/images/S/compressed.photo.goodreads.com/books/1398034300i/5107.jpg", "icon": "person_search"},
    {"title": "Moby Dick",                    "author": "Herman Melville",     "genre": "Fiction",          "tag": "Physical", "tag_col": TAG_PHY,   "cover": "https://bookmanager.com/i/m?b=rBSsMLeAZlbH_8bDoVHfdA", "icon": "sailing"},
    {"title": "The Innovators",              "author": "Walter Isaacson",       "genre": "Technology",  "tag": "E-Book",   "tag_col": TAG_EBOOK, "cover": "https://d28hgpri8am2if.cloudfront.net/book_images/onix/cvr9781476708706/the-innovators-9781476708706_hr.jpg", "icon": "lightbulb"},
    {"title": "Educated",                    "author": "Tara Westover",         "genre": "Self-Help",   "tag": "Physical", "tag_col": TAG_PHY,   "cover": "https://m.media-amazon.com/images/S/compressed.photo.goodreads.com/books/1506026635i/35133922.jpg", "icon": "school"},
    {"title": "The Power of Habit",          "author": "Charles Duhigg",        "genre": "Psychology",  "tag": "E-Book",   "tag_col": TAG_EBOOK, "cover": "https://charlesduhigg.com/wp-content/uploads/2025/01/power-of-habit-large-flat.webp", "icon": "loop"},
    {"title": "Dune",                        "author": "Frank Herbert",         "genre": "Fiction",     "tag": "Physical", "tag_col": TAG_PHY,   "cover": "https://m.media-amazon.com/images/I/81Ua99CURsL._AC_UF1000,1000_QL80_.jpg", "icon": "public"},
    {"title": "The Black Swan",              "author": "Nassim Nicholas Taleb", "genre": "Business",    "tag": "E-Book",   "tag_col": TAG_EBOOK, "cover": "https://m.media-amazon.com/images/S/compressed.photo.goodreads.com/books/1714172313i/242472.jpg", "icon": "casino"},
    {"title": "Cosmos",                      "author": "Carl Sagan",            "genre": "Science",     "tag": "Physical", "tag_col": TAG_PHY,   "cover": "https://www.bookowlsbd.com/cdn/shop/files/Cosmos_CarlSagan.jpg?v=1738523784", "icon": "flare"},
    {"title": "Crime and Punishment",        "author": "Fyodor Dostoevsky",     "genre": "Fiction",     "tag": "E-Book",   "tag_col": TAG_EBOOK, "cover": "https://m.media-amazon.com/images/I/71O2XIytdqL._AC_UF1000,1000_QL80_.jpg", "icon": "gavel"},
    {"title": "Never Split the Difference",  "author": "Chris Voss",            "genre": "Business",    "tag": "Physical", "tag_col": TAG_PHY,   "cover": "https://m.media-amazon.com/images/I/81PPq8CP4sL._AC_UF1000,1000_QL80_.jpg", "icon": "handshake"},
    {"title": "The Gene",                    "author": "Siddhartha Mukherjee",  "genre": "Science",     "tag": "E-Book",   "tag_col": TAG_EBOOK, "cover": "https://d28hgpri8am2if.cloudfront.net/book_images/onix/cvr9781476733500/the-gene-9781476733500_hr.jpg", "icon": "biotech"},
    {"title": "Database System Concepts",    "author": "Silberschatz, Korth",   "genre": "Technology",  "tag": "Physical", "tag_col": TAG_PHY,   "cover": "https://www.db-book.com/images/db7-cover.jpg", "icon": "storage"},
    {"title": "The Art of War",                    "author": "Sun Tzu",           "genre": "Business",    "tag": "E-Book",   "tag_col": TAG_EBOOK, "cover": "https://fingerprintpublishing.com/cache/public/uploads/books/9788172345242.jpg-544x550.jpg", "icon": "military_tech"},
    {"title": "A Random Walk Down Wall Street",    "author": "Burton Malkiel",    "genre": "Business",    "tag": "Physical", "tag_col": TAG_PHY,   "cover": "https://m.media-amazon.com/images/I/61l80PpNErL._AC_UF1000,1000_QL80_.jpg", "icon": "trending_up"},
    {"title": "The Double Helix",                  "author": "James Watson",      "genre": "Science",     "tag": "E-Book",   "tag_col": TAG_EBOOK, "cover": "https://d28hgpri8am2if.cloudfront.net/book_images/cvr9780743216302_9780743216302_hr.jpg", "icon": "biotech"},
    {"title": "Neuromancer",                       "author": "William Gibson",    "genre": "Fiction",     "tag": "Physical", "tag_col": TAG_PHY,   "cover": "https://images.penguinrandomhouse.com/cover/9780441007462", "icon": "memory"},
    {"title": "Thinking in Systems",               "author": "Donella Meadows",   "genre": "Technology",  "tag": "E-Book",   "tag_col": TAG_EBOOK, "cover": "https://m.media-amazon.com/images/S/compressed.photo.goodreads.com/books/1735956251i/18891716.jpg", "icon": "account_tree"},
    {"title": "The Design of Everyday Things",     "author": "Don Norman",        "genre": "Technology",  "tag": "Physical", "tag_col": TAG_PHY,   "cover": "https://m.media-amazon.com/images/I/71sF8kuMW3L._AC_UF1000,1000_QL80_.jpg", "icon": "design_services"},
    {"title": "Clean Architecture",  "author": "Robert C. Martin",  "genre": "Technology",  "tag": "Physical",  "tag_col": TAG_PHY,  "cover": "https://m.media-amazon.com/images/I/71stxGw9JgL.jpg",  "icon": "architecture"},
    {"title": "The Silk Roads",                              "author": "Peter Frankopan",       "genre": "History",  "tag": "Physical", "tag_col": TAG_PHY,   "cover": "https://m.media-amazon.com/images/S/compressed.photo.goodreads.com/books/1472636067i/25812847.jpg", "icon": "public"},
    {"title": "Genghis Khan and the Making of the Modern World", "author": "Jack Weatherford", "genre": "History",  "tag": "E-Book",   "tag_col": TAG_EBOOK, "cover": "https://m.media-amazon.com/images/I/81U2T-DMAaL._AC_UF1000,1000_QL80_.jpg", "icon": "history_edu"},
    {"title": "The Emperor of All Maladies",                 "author": "Siddhartha Mukherjee",  "genre": "Science",  "tag": "Physical", "tag_col": TAG_PHY,   "cover": "https://d28hgpri8am2if.cloudfront.net/book_images/onix/cvr9781668047033/the-emperor-of-all-maladies-9781668047033_hr.jpg", "icon": "biotech"},
    {"title": "Seven Brief Lessons on Physics",              "author": "Carlo Rovelli",         "genre": "Science",  "tag": "E-Book",   "tag_col": TAG_EBOOK, "cover": "https://m.media-amazon.com/images/I/81Iz11keeTL._AC_UF894,1000_QL80_.jpg", "icon": "flare"},

]
REVIEWS = {
    "1984": "A chilling dystopian masterpiece. Orwell's vision of a totalitarian future remains terrifyingly relevant. Essential reading for everyone.",
    "The Age of AI": "Kissinger, Schmidt and Huttenlocher explore how AI is reshaping civilization, knowledge, and geopolitics. Thought-provoking and urgent.",
    "The Social Network": "The gripping true story behind Facebook's founding. A tale of ambition, betrayal, and billion-dollar consequences.",
    "Surely You're Joking, Mr. Feynman!": "Hilarious and brilliant memoirs of a Nobel-winning physicist. Science has never felt this fun and human.",
    "Homo Deus": "Harari projects humanity's future — from defeating death to merging with AI. Bold, controversial, and fascinating.",
    "The Great Gatsby": "Fitzgerald's lyrical portrait of the Jazz Age and the hollow American Dream. A timeless tragedy of love and illusion.",
    "Sapiens: A Brief History": "A sweeping journey through 70,000 years of human history. Harari makes you rethink everything you know about our species.",
    "Outliers": "Gladwell reveals the hidden factors behind extraordinary success. The 10,000-hour rule will change how you view talent.",
    "The Hitchhiker's Guide to the Galaxy": "Absurdly funny sci-fi comedy. The answer to life, the universe and everything is 42. Read it to understand why.",
    "The Phoenix Project": "A novel about IT, DevOps and saving a company from disaster. Surprisingly gripping — a must for tech professionals.",
    "Python for Data Analysis": "The definitive guide to data wrangling with pandas by its creator. Practical, dense, and invaluable for data work.",
    "Designing Data-Intensive Apps": "Kleppmann's deep dive into databases, streams and distributed systems. The bible of modern backend engineering.",
    "Thinking, Fast and Slow": "Kahneman reveals the two systems driving our decisions. A landmark work in behavioral psychology and economics.",
    "The Lean Startup": "Eric Ries redefines how companies are built. The build-measure-learn loop is now standard startup gospel.",
    "Guns, Germs, and Steel": "Diamond explains why some civilizations dominated others through geography and biology — not race or intelligence.",
    "Deep Learning": "The comprehensive academic textbook on neural networks by the field's pioneers. Dense but indispensable for AI researchers.",
    "Superintelligence": "Bostrom's landmark warning about the existential risks of advanced AI. Elon Musk called it a must-read.",
    "The Pragmatic Programmer": "Timeless wisdom for software craftspeople. From code hygiene to career growth — every developer should own this.",
    "Zero to One": "Thiel argues great companies build monopolies by creating something entirely new. Contrarian, sharp, and provocative.",
    "Shoe Dog": "Phil Knight's raw memoir of building Nike from nothing. One of the greatest entrepreneurship stories ever told.",
    "Atomic Habits": "Clear's practical system for building good habits and breaking bad ones. Small changes, remarkable results.",
    "Clean Code": "Martin's guide to writing readable, maintainable code. Every messy codebase could be saved by this book.",
    "Brave New World": "Huxley's dystopia of pleasure and control feels more relevant than ever in the age of social media and dopamine.",
    "The Mythical Man-Month": "Brooks' classic insight: adding people to a late project makes it later. Software truths that never age.",
    "Computer Networking": "Kurose's textbook covers the internet from top to bottom. The standard reference for networking students worldwide.",
    "Code": "Petzold walks you from morse code to microprocessors. The most elegant explanation of how computers actually work.",
    "Rich Dad Poor Dad": "Kiyosaki's financial education classic. Challenges conventional wisdom about money, assets and building wealth.",
    "A Brief History of Time": "Hawking makes black holes and the Big Bang accessible to everyone. A miracle of scientific communication.",
    "The Selfish Gene": "Dawkins reframes evolution from the gene's perspective. Introduced the concept of the 'meme' to the world.",
    "Fahrenheit 451": "Bradbury's burning vision of a future without books. A love letter to reading and a warning about censorship.",
    "The Alchemist": "Coelho's allegorical journey about following your dreams. Simple, spiritual, and beloved by millions worldwide.",
    "Man's Search for Meaning": "Frankl's account of surviving the Holocaust and finding purpose in suffering. Profoundly moving and life-changing.",
    "Life 3.0": "Tegmark explores what it means to be human in the age of AI. Optimistic, rigorous, and genuinely exciting.",
    "Human Compatible": "Stuart Russell proposes a new framework for AI safety. The most important AI book written by an insider.",
    "The Alignment Problem": "Christian investigates the challenge of making AI do what we actually want. Urgent and brilliantly reported.",
    "Introduction to Algorithms": "CLRS — the definitive algorithms textbook. Dense, comprehensive, and on every serious programmer's shelf.",
    "Art of Computer Programming": "Knuth's magnum opus. The most rigorous and complete work on algorithms ever written. A lifetime of reading.",
    "The Subtle Art of Not Giving a F*ck": "Manson's counterintuitive guide to living a good life by caring less about the wrong things. Refreshingly honest.",
    "Hands-On Machine Learning": "Géron's practical guide to ML with Scikit-Learn and TensorFlow. The best hands-on ML book available today.",
    "Good to Great": "Collins' research on what separates truly great companies from merely good ones. Data-driven and insightful.",
    "The Hard Thing About Hard Things": "Horowitz gives brutally honest advice on the hardest parts of running a startup. No sugarcoating.",
    "Blue Ocean Strategy": "Kim and Mauborgne show how to create uncontested market space instead of competing. A strategy classic.",
    "Start with Why": "Sinek argues that inspiring leaders all think from the inside out — starting with purpose, not product.",
    "Deep Work": "Newport makes the case for focused, distraction-free work as the superpower of the 21st century.",
    "Grit": "Duckworth's research proves passion and perseverance matter more than talent. Grit is the secret to success.",
    "Thinking in Bets": "Poker champion Annie Duke teaches decision-making under uncertainty. Outcomes don't equal decision quality.",
    "Flow": "Csikszentmihalyi's research on peak happiness and total absorption in meaningful work. A psychology classic.",
    "The Picture of Dorian Gray": "Wilde's only novel — a dark, witty tale of vanity, corruption and the price of eternal youth.",
    "Pride and Prejudice": "Austen's perfect comedy of manners. Elizabeth Bennet remains one of fiction's greatest heroines.",
    "The Catcher in the Rye": "Holden Caulfield's voice is unlike any other. A raw, funny, heartbreaking portrait of teenage alienation.",
    "Moby Dick": "Melville's epic obsession with a white whale. Dense, symbolic, and one of literature's greatest achievements.",
    "The Innovators": "Isaacson chronicles the creative geniuses who built the digital revolution. Inspiring and meticulously researched.",
    "Educated": "Westover's breathtaking memoir of growing up off-grid and teaching herself into Cambridge. Unforgettable.",
    "The Power of Habit": "Duhigg uncovers the science behind why habits exist and how to change them. Practical and eye-opening.",
    "Dune": "Herbert's epic of politics, religion and ecology on a desert planet. The greatest science fiction novel ever written.",
    "The Black Swan": "Taleb explains how rare, unpredictable events shape history. A book that changes how you see the world.",
    "Cosmos": "Sagan's poetic journey through the universe. Still the most beautiful introduction to science ever written.",
    "Crime and Punishment": "Dostoevsky's psychological masterpiece about guilt and redemption. Raskolnikov's torment feels intensely real.",
    "Never Split the Difference": "FBI negotiator Voss shares techniques that work in business and life. Gripping and immediately useful.",
    "The Gene": "Mukherjee's sweeping history of genetics, from Mendel to CRISPR. Beautifully written and deeply important.",
    "Database System Concepts": "Silberschatz's authoritative textbook on database theory and design. The standard reference for DB students.",
    "The Art of War": "Sun Tzu's 2,500-year-old strategy guide still applies to business and leadership today. Timeless wisdom in brevity.",
    "A Random Walk Down Wall Street": "Malkiel's classic argument for index investing over stock picking. Your portfolio will thank you.",
    "The Double Helix": "Watson's personal account of discovering DNA's structure. Controversial, candid and historically essential.",
    "Neuromancer": "Gibson invented cyberpunk with this novel. Matrix, cyberspace, AI — all traced back to this 1984 masterpiece.",
    "Thinking in Systems": "Meadows reveals the hidden structures driving world events. Essential for anyone trying to understand complexity.",
    "The Design of Everyday Things": "Norman explains why bad design is everywhere and how good design thinks about people first.",
    "Clean Architecture": "Martin extends Clean Code to system design. How to build software that stays maintainable for decades.",
    "The Silk Roads": "Frankopan rewrites world history from Central Asia outward. Everything you thought you knew gets reframed.",
    "Genghis Khan and the Making of the Modern World": "Weatherford rehabilitates the Mongol legacy. Their empire connected and transformed the entire world.",
    "The Emperor of All Maladies": "Mukherjee's biography of cancer is both science and poetry. A Pulitzer Prize winner for good reason.",
    "Seven Brief Lessons on Physics": "Rovelli distills modern physics into 79 breathtaking pages. The most beautiful science book of the decade.",
}

def get_review_for_book(book):
    title = book.get("title", "")
    if title in REVIEWS:
        return REVIEWS[title]

    format_text = "digital favorite" if book.get("tag") == "E-Book" else "shelf staple"
    genre = book.get("genre", "General")
    author = book.get("author", "Unknown author")
    return f"{title} by {author} is a strong {genre.lower()} pick and a {format_text}. Add it to your reading list for this month."

def matches_prefix_query(book, query):
    q = query.strip().lower()
    if not q:
        return True

    # Prefix-only search on field starts (not middle words).
    q_parts = [part for part in q.split() if part]
    fields = [
        str(book.get("title", "")).lower().strip(),
        str(book.get("author", "")).lower().strip(),
        str(book.get("genre", "")).lower().strip(),
        str(book.get("tag", "")).lower().strip(),
    ]
    if len(q_parts) <= 1:
        return any(field.startswith(q) for field in fields)

    return all(any(field.startswith(part) for field in fields) for part in q_parts)

def search_priority(book, query):
    q = query.strip().lower()
    title = str(book.get("title", "")).lower().strip()
    author = str(book.get("author", "")).lower().strip()
    genre = str(book.get("genre", "")).lower().strip()
    tag = str(book.get("tag", "")).lower().strip()

    if not q:
        return (0, title)

    if title.startswith(q):
        return (0, title)
    if author.startswith(q):
        return (1, title)
    if genre.startswith(q):
        return (2, title)
    if tag.startswith(q):
        return (3, title)

    # Fallback for multi-word query handling.
    first_token = q.split()[0]
    if title.startswith(first_token):
        return (4, title)
    if author.startswith(first_token):
        return (5, title)
    if genre.startswith(first_token):
        return (6, title)
    if tag.startswith(first_token):
        return (7, title)

    return (99, title)

CATEGORIES = ["All", "Technology", "Business", "Fiction", "Self-Help", "Psychology", "Science", "History"]

VIEW_MODES = ["Small", "Medium", "Large", "Extra Large", "Detailed List"]

# ─── API-safe helpers ────────────────────────────────────────
def ps(h, v):    return ft.Padding(left=h, right=h, top=v, bottom=v)
def pa(n):       return ft.Padding(left=n, right=n, top=n, bottom=n)
def ba(w, c):    return ft.Border(left=ft.BorderSide(w, c), right=ft.BorderSide(w, c), top=ft.BorderSide(w, c), bottom=ft.BorderSide(w, c))
def bbtm(c):     return ft.Border(bottom=ft.BorderSide(1, c))
def brtop(r):    return ft.BorderRadius.only(top_left=r, top_right=r)
def brbot(r):    return ft.BorderRadius.only(bottom_left=r, bottom_right=r)

# ─── Reusable widgets ────────────────────────────────────────
def tag_chip(label, color):
    return ft.Container(
        content=ft.Text(label, size=9, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
        bgcolor=color, border_radius=4, padding=ps(6, 2),
    )

def nav_link(text, active=False, on_click=None):
    t = ft.Text(text, size=13, color=ACCENT if active else TEXT_SEC, weight=ft.FontWeight.W_600 if active else ft.FontWeight.W_500)
    c = ft.Column([t], spacing=4, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    if active:
        c.controls.append(ft.Container(bgcolor=ACCENT, height=2, width=40, border_radius=2))
    
    def on_hover(e):
        t.color = PALE_PURP if e.data == "true" and not active else (ACCENT if active else TEXT_SEC)
        t.update()

    return ft.Container(content=c, on_hover=on_hover, on_click=on_click)

def show_snack(page, title):
    page.snack_bar = ft.SnackBar(content=ft.Text(f'Opening "{title}"…'), bgcolor=ACCENT)
    page.snack_bar.open = True
    page.update()

def book_card(book, page, mode="Large"):
    is_ebook  = book["tag"] == "E-Book"
    btn_label = "Read Now" if is_ebook else "View Details"
    btn_col   = TAG_EBOOK  if is_ebook else ACCENT
    cref      = ft.Ref[ft.Container]()

    widths  = {"Small": 160, "Medium": 195, "Large": 230, "Extra Large": 280, "Detailed List": 0}
    heights = {"Small": 130, "Medium": 170, "Large": 220, "Extra Large": 280, "Detailed List": 160}

    w = widths.get(mode, 175)
    h = heights.get(mode, 175)
    fs = 11 if "Small" in mode else (14 if mode == "Extra Large" else (13 if mode == "Large" else 12))

    review_text = get_review_for_book(book)

    # ── List View Rendering ──
    if "List" in mode:
        return ft.Container(
            border=ba(1, BORDER), border_radius=10, bgcolor=BG_CARD, padding=pa(15), expand=True,
            content=ft.Row([
                ft.Container(width=100, height=140, border_radius=8, clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                             content=ft.Image(src=book["cover"], fit=ft.BoxFit.COVER, gapless_playback=True)),
                ft.Column([
                    ft.Row([ft.Text(book["title"], size=16, weight=ft.FontWeight.BOLD, color=TEXT_PRI), tag_chip(book["tag"], book["tag_col"])]),
                    ft.Text(f"by {book['author']}", size=13, color=TEXT_SEC),
                    ft.Text(book["genre"], size=11, color=ACCENT2),
                    ft.Container(height=4),
                    ft.Text(review_text, size=12, color=TEXT_SEC, max_lines=2, overflow=ft.TextOverflow.ELLIPSIS),
                    ft.Container(expand=True),
                    ft.FilledButton(btn_label, height=32, on_click=lambda e, t=book["title"]: show_snack(page, t),
                                   style=ft.ButtonStyle(bgcolor=btn_col, color=ft.Colors.WHITE, shape=ft.RoundedRectangleBorder(radius=6))),
                ], expand=True, spacing=4)
            ], spacing=20, vertical_alignment=ft.CrossAxisAlignment.START)
        )

    # ── Flip state ──
    flipped = {"value": False}
    front_ref = ft.Ref[ft.Container]()
    back_ref  = ft.Ref[ft.Container]()

    def on_cover_click(e):
        flipped["value"] = not flipped["value"]
        if front_ref.current:
            front_ref.current.visible = not flipped["value"]
            front_ref.current.update()
        if back_ref.current:
            back_ref.current.visible = flipped["value"]
            back_ref.current.update()


    # ── Hover ──
    def hover(e):
        c = cref.current
        if not c: return
        c.shadow = ft.BoxShadow(blur_radius=22, color="#9333eaff", spread_radius=2) if e.data == "true" else ft.BoxShadow(blur_radius=10, color="#22000000")
        c.border = ba(1, ACCENT) if e.data == "true" else ba(1, BORDER)
        c.update()

    # ── Front face (cover image) ──
    front = ft.Container(
        ref=front_ref,
        visible=True,
        height=h,
        bgcolor=BG_DARK,
        border_radius=brtop(10),
        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
        on_click=on_cover_click,
        tooltip="Click to see review",
        content=ft.Stack([
            ft.Image(src=book["cover"], fit=ft.BoxFit.COVER, width=w, height=h, gapless_playback=True),
            ft.Container(padding=pa(10), content=tag_chip(book["tag"], book["tag_col"])),
            ft.Container(
                right=8, bottom=8,
                content=ft.Container(
                    bgcolor="#00000088", border_radius=6, padding=ps(6, 3),
                    content=ft.Row([
                        ft.Icon(ft.Icons.FLIP_TO_BACK, color=ft.Colors.WHITE70, size=10),
                        ft.Text("Review", size=9, color=ft.Colors.WHITE70),
                    ], spacing=4, tight=True)
                )
            ),
        ]),
    )

    # ── Back face (review) ──
    back = ft.Container(
        ref=back_ref,
        visible=False,
        height=h,
        bgcolor=BG_CARD,
        border_radius=brtop(10),
        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
        on_click=on_cover_click,
        tooltip="Click to go back",
        padding=pa(14),
        content=ft.Column(
            spacing=8,
            controls=[
                ft.Row([
                    ft.Icon(ft.Icons.FORMAT_QUOTE, color=ACCENT2, size=16),
                    ft.Text("Review", size=10, color=ACCENT2, weight=ft.FontWeight.BOLD),
                ], spacing=6),
                ft.Text(
                    review_text,
                    size=11,
                    color=TEXT_PRI,
                    max_lines=7,
                    overflow=ft.TextOverflow.ELLIPSIS,
                ),
                ft.Container(expand=True),
                ft.Row([
                    ft.Icon(ft.Icons.FLIP_TO_FRONT, color=TEXT_SEC, size=10),
                    ft.Text("Click to flip back", size=9, color=TEXT_SEC),
                ], spacing=4),
            ]
        ),
    )

    return ft.Container(
        ref=cref, on_hover=hover, border=ba(1, BORDER), border_radius=10,
        shadow=ft.BoxShadow(blur_radius=10, color="#22000000"), width=w,
        content=ft.Column(spacing=0, controls=[
            ft.Stack(controls=[front, back]),
            ft.Container(bgcolor=BG_CARD, padding=pa(10), border_radius=brbot(10),
                content=ft.Column(spacing=3, controls=[
                    ft.Text(book["title"], size=fs, weight=ft.FontWeight.BOLD, color=TEXT_PRI, max_lines=2, overflow=ft.TextOverflow.ELLIPSIS),
                    ft.Text(book["author"], size=fs-2, color=TEXT_SEC, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                    ft.Text(book["genre"], size=fs-3, color=TEXT_SEC),
                    ft.Container(height=6),
                    ft.FilledButton(btn_label, height=28, on_click=lambda e, t=book["title"]: show_snack(page, t),
                        style=ft.ButtonStyle(bgcolor=btn_col, color=ft.Colors.WHITE,
                                             shape=ft.RoundedRectangleBorder(radius=6), padding=ps(8, 4))),
                ])),
        ]),
    )

def book_table(books):
    return ft.DataTable(
        border=ba(1, BORDER), border_radius=10, bgcolor=BG_NAV,
        column_spacing=40,
        columns=[
            ft.DataColumn(ft.Text("Title", color=TEXT_PRI, weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Author", color=TEXT_PRI, weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Genre", color=TEXT_PRI, weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Format", color=TEXT_PRI, weight=ft.FontWeight.BOLD)),
        ],
        rows=[
            ft.DataRow(cells=[
                ft.DataCell(ft.Text(b["title"], color=TEXT_PRI)),
                ft.DataCell(ft.Text(b["author"], color=TEXT_SEC)),
                ft.DataCell(ft.Text(b["genre"], color=TEXT_SEC)),
                ft.DataCell(tag_chip(b["tag"], b["tag_col"])),
            ]) for b in books
        ]
    )

def dashboard_metric_card(title, value, subtitle, color):
    return ft.Container(
        expand=True,
        bgcolor=BG_CARD,
        border=ba(1, BORDER),
        border_radius=12,
        padding=pa(16),
        content=ft.Column(
            spacing=8,
            controls=[
                ft.Row(
                    [
                        ft.Container(width=14, height=14, border_radius=7, bgcolor=color),
                        ft.Text(title, size=10, color=TEXT_SEC, weight=ft.FontWeight.W_600),
                    ],
                    spacing=8,
                ),
                ft.Text(value, size=24, color=TEXT_PRI, weight=ft.FontWeight.BOLD),
                ft.Text(subtitle, size=10, color=TEXT_SEC),
            ],
        ),
    )

# ─── Main ───────────────────────────────────────────────────
def auth_page(page: ft.Page, on_success):
    page.title = "Smart Library – Sign In"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = BG_DARK
    page.padding = 0

    state = {"mode": "login"}
    err_ref = ft.Ref[ft.Text]()
    usr_ref = ft.Ref[ft.TextField]()
    email_ref = ft.Ref[ft.TextField]()
    pwd_ref = ft.Ref[ft.TextField]()
    confirm_ref = ft.Ref[ft.TextField]()
    title_ref = ft.Ref[ft.Text]()
    sub_ref = ft.Ref[ft.Text]()
    btn_ref = ft.Ref[ft.FilledButton]()
    toggle_ref = ft.Ref[ft.TextButton]()
    email_row_ref = ft.Ref[ft.Container]()
    confirm_row_ref = ft.Ref[ft.Container]()

    def field(hint, icon, password=False, ref=None):
        return ft.TextField(
            ref=ref, hint_text=hint, password=password, can_reveal_password=password,
            prefix_icon=icon, border=ft.InputBorder.OUTLINE, border_color=BORDER,
            focused_border_color=ACCENT, color=TEXT_PRI,
            hint_style=ft.TextStyle(color=TEXT_SEC), bgcolor=BG_CARD,
            border_radius=10, text_size=13, cursor_color=ACCENT,
            content_padding=ft.Padding(left=14, right=14, top=14, bottom=14),
        )

    def show_err(msg, ok=False):
        err_ref.current.value = msg
        err_ref.current.color = TAG_EBOOK if ok else ft.Colors.RED_300
        err_ref.current.update()

    def switch_mode(e=None):
        state["mode"] = "signup" if state["mode"] == "login" else "login"
        is_signup = state["mode"] == "signup"
        title_ref.current.value = "Create Account" if is_signup else "Welcome Back"
        sub_ref.current.value = "Join Smart Library today" if is_signup else "Sign in to your library"
        btn_ref.current.text = "Create Account" if is_signup else "Sign In"
        toggle_ref.current.content = ft.Text(
            "Already have an account? Sign In" if is_signup else "Don't have an account? Sign Up",
            size=12, color=ACCENT
        )
        email_row_ref.current.visible = is_signup
        confirm_row_ref.current.visible = is_signup
        err_ref.current.value = ""
        for r in [usr_ref, email_ref, pwd_ref, confirm_ref]:
            if r.current: r.current.value = ""
        page.update()

    def do_submit(e=None):
        username = usr_ref.current.value.strip()
        password = pwd_ref.current.value
        if state["mode"] == "login":
            if not username or not password:
                show_err("Please fill in all fields."); return
            ok, msg, user = db_login(username, password)
            if ok:
                show_err(msg, ok=True)
                page.clean()
                on_success(page, user)
            else:
                show_err(msg)
        else:
            email = email_ref.current.value.strip()
            confirm = confirm_ref.current.value
            if not username or not email or not password or not confirm:
                show_err("Please fill in all fields."); return
            if "@" not in email:
                show_err("Enter a valid email address."); return
            if len(password) < 6:
                show_err("Password must be at least 6 characters."); return
            if password != confirm:
                show_err("Passwords do not match."); return
            ok, msg = db_register(username, email, password)
            if ok:
                show_err(msg, ok=True)
                state["mode"] = "login"
                switch_mode()
            else:
                show_err(msg)

    card = ft.Container(
        width=420, bgcolor=BG_CARD, border=ba(1, BORDER), border_radius=16, padding=pa(36),
        content=ft.Column(spacing=0, controls=[
            ft.Row([
                ft.Container(content=ft.Icon(ft.Icons.AUTO_STORIES, color=ft.Colors.WHITE, size=18),
                             bgcolor=ACCENT, border_radius=6, padding=pa(6)),
                ft.Text("Smart Library", size=16, weight=ft.FontWeight.BOLD, color=TEXT_PRI),
            ], spacing=10),
            ft.Container(height=24),
            ft.Text(ref=title_ref, value="Welcome Back", size=26, weight=ft.FontWeight.BOLD, color=TEXT_PRI),
            ft.Container(height=4),
            ft.Text(ref=sub_ref, value="Sign in to your library", size=13, color=TEXT_SEC),
            ft.Container(height=28),
            ft.Text("Username or Email", size=12, color=TEXT_SEC, weight=ft.FontWeight.W_500),
            ft.Container(height=6),
            field("Enter username or email", ft.Icons.PERSON_OUTLINE, ref=usr_ref),
            ft.Container(height=14),
            ft.Container(ref=email_row_ref, visible=False, content=ft.Column(spacing=0, controls=[
                ft.Text("Email Address", size=12, color=TEXT_SEC, weight=ft.FontWeight.W_500),
                ft.Container(height=6),
                field("Enter your email", ft.Icons.EMAIL_OUTLINED, ref=email_ref),
                ft.Container(height=14),
            ])),
            ft.Text("Password", size=12, color=TEXT_SEC, weight=ft.FontWeight.W_500),
            ft.Container(height=6),
            field("Enter password", ft.Icons.LOCK_OUTLINE, password=True, ref=pwd_ref),
            ft.Container(height=14),
            ft.Container(ref=confirm_row_ref, visible=False, content=ft.Column(spacing=0, controls=[
                ft.Text("Confirm Password", size=12, color=TEXT_SEC, weight=ft.FontWeight.W_500),
                ft.Container(height=6),
                field("Re-enter password", ft.Icons.LOCK_RESET_OUTLINED, password=True, ref=confirm_ref),
                ft.Container(height=14),
            ])),
            ft.Text(ref=err_ref, value="", size=12, color=ft.Colors.RED_300),
            ft.Container(height=10),
            ft.FilledButton("Sign In", ref=btn_ref, width=float("inf"), height=44,
                            on_click=do_submit,
                            style=ft.ButtonStyle(bgcolor=ACCENT, color=ft.Colors.WHITE,
                                                 shape=ft.RoundedRectangleBorder(radius=10))),
            ft.Container(height=16),
            ft.Row([ft.TextButton(
                ref=toggle_ref,
                content=ft.Text("Don't have an account? Sign Up", size=12, color=ACCENT),
                on_click=switch_mode,
            )], alignment=ft.MainAxisAlignment.CENTER),
        ])
    )

    page.add(ft.Container(
        expand=True, bgcolor=BG_DARK,
        content=ft.Column([card], alignment=ft.MainAxisAlignment.CENTER,
                          horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        padding=pa(20),
    ))



def main(page: ft.Page, user: dict = None):
    if user is None:
        user = {"username": "Guest", "email": ""}
    logged_user = user["username"]
    logged_initials = "".join(w[0].upper() for w in logged_user.split()[:2]) or "U"

    page.title = "Smart Library"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = BG_DARK
    page.padding = 0
    page.window.min_width = 900
    page.window.maximized = True
    page.scroll = ft.ScrollMode.AUTO

    if not hasattr(page, "active_page"):
        page.active_page = "Books"
    if not hasattr(page, "search_query"):
        page.search_query = ""
    state = {"cat": "All", "q": page.search_query, "view_mode": "Large", "active_page": page.active_page}
    cat_row_ref = ft.Ref[ft.Row]()
    grid_ref = ft.Ref[ft.Row]()
    dashboard_reco_row_ref = ft.Ref[ft.Row]()
    if not hasattr(page, "theme_dark"):
        page.theme_dark = True
    theme_btn_ref = ft.Ref[ft.IconButton]()

    def apply_theme():
        global BG_DARK, BG_CARD, BG_NAV, TEXT_PRI, TEXT_SEC, BORDER, PALE_PURP

        if page.theme_dark:
            BG_DARK = "#0f0f13"
            BG_CARD = "#1a1a24"
            BG_NAV = "#12121e"
            TEXT_PRI = "#f0f0f8"
            TEXT_SEC = "#8888aa"
            BORDER = "#2a2a3a"
            PALE_PURP = "#d1d1f0"
            page.theme_mode = ft.ThemeMode.DARK
        else:
            BG_DARK = LIGHT_BG_DARK
            BG_CARD = LIGHT_BG_CARD
            BG_NAV = LIGHT_BG_NAV
            TEXT_PRI = LIGHT_TEXT_PRI
            TEXT_SEC = LIGHT_TEXT_SEC
            BORDER = LIGHT_BORDER
            PALE_PURP = LIGHT_PALE_PURP
            page.theme_mode = ft.ThemeMode.LIGHT

        page.bgcolor = BG_DARK

    def toggle_theme(e):
        page.theme_dark = not page.theme_dark
        page.clean()
        main(page)

    apply_theme()

    card_cache = {}

    def get_card(book, mode):
        key = (book["title"], mode)
        if key not in card_cache:
            card_cache[key] = book_card(book, page, mode)
        return card_cache[key]

    def filtered():
        q, cat = state["q"], state["cat"]
        books = [
            b for b in BOOKS
            if (cat == "All" or b["genre"] == cat)
            and matches_prefix_query(b, q)
        ]
        return sorted(books, key=lambda b: search_priority(b, q))

    def search_matches(limit=6):
        q = state["q"].strip()
        if not q:
            return []
        matches = [
            b for b in BOOKS
            if matches_prefix_query(b, q)
        ]
        return sorted(matches, key=lambda b: search_priority(b, q))[:limit]

    def dashboard_recommended_books():
        # Keep dashboard recommendations stable; do not change by navbar search.
        return BOOKS[55:63] if len(BOOKS) >= 63 else BOOKS[-8:]

    def dashboard_recent_digital_books():
        # Safe slice to avoid index errors when dataset size changes.
        recent_books = [b for b in BOOKS if b.get("tag") == "E-Book"][-4:]
        if len(recent_books) < 4:
            recent_books = BOOKS[-4:]
        time_labels = ["2 hours ago", "Yesterday", "3 days ago", "1 week ago"]
        pairs = list(zip(recent_books, time_labels))
        if len(pairs) < 4:
            missing = 4 - len(pairs)
            filler_books = BOOKS[:missing]
            pairs.extend(zip(filler_books, time_labels[len(pairs):]))
        return pairs

    def refresh_dashboard_search():
        if not dashboard_reco_row_ref.current:
            return
        dashboard_reco_row_ref.current.controls = [dashboard_reco_card(b) for b in dashboard_recommended_books()]
        dashboard_reco_row_ref.current.update()

    def refresh():
        if not grid_ref.current:
            return
        mode = state["view_mode"]
        books = filtered()

        if "List" in mode:
            grid_ref.current.controls = [ft.Column([get_card(b, mode) for b in books], spacing=15)]
        else:
            grid_ref.current.controls = [get_card(b, mode) for b in books]

        grid_ref.current.update()

    def cycle_view_mode(e):
        curr_idx = VIEW_MODES.index(state["view_mode"])
        next_idx = (curr_idx + 1) % len(VIEW_MODES)
        state["view_mode"] = VIEW_MODES[next_idx]
        preview_idx = (next_idx + 1) % len(VIEW_MODES)
        e.control.tooltip = f"Switch to {VIEW_MODES[preview_idx]} View"
        e.control.icon = ft.Icons.VIEW_LIST if "List" in VIEW_MODES[next_idx] else ft.Icons.GRID_VIEW
        e.control.update()
        refresh()

    def pick_cat(cat):
        state["cat"] = cat
        refresh_chips()
        refresh()

    def refresh_chips():
        chips = []
        for cat in CATEGORIES:
            active = cat == state["cat"]
            chips.append(
                ft.Container(
                    content=ft.Text(cat, size=11, color=ft.Colors.WHITE if active else TEXT_SEC),
                    bgcolor=ACCENT if active else BG_CARD,
                    border=ba(1, ACCENT if active else BORDER),
                    border_radius=18,
                    padding=ps(16, 8),
                    on_click=lambda e, c=cat: pick_cat(c),
                )
            )
        cat_row_ref.current.controls = chips
        cat_row_ref.current.update()

    def on_search(e):
        val = e.control.value
        if val == state["q"]:
            return
        state["q"] = val
        page.search_query = val
        if state["active_page"] == "Books":
            refresh()


    def set_active_page(target):
            page.active_page = target
            state["active_page"] = target
            page.clean()
            main(page, user)
            if target == "Settings":
                import asyncio
                async def delayed_reload():
                    await asyncio.sleep(0.1)
                    reload_users()
                page.run_task(delayed_reload)
    
    def do_logout(e):
        import asyncio
        async def _logout_task():
            # Give the popup menu a tiny moment to close smoothly before destroying the page
            await asyncio.sleep(0.1) 
            page.clean()
            page.active_page = "Books"
            page.search_query = ""
            auth_page(page, on_success=main)
            
        page.run_task(_logout_task)

    # ── Navbar ──────────────────────────────────────────────
    navbar = ft.Container(bgcolor=BG_NAV, padding=ps(34, 12), border=bbtm(BORDER),
        content=ft.Row(vertical_alignment=ft.CrossAxisAlignment.CENTER, controls=[
            ft.Container(content=ft.Row([
                ft.Container(content=ft.Icon(ft.Icons.AUTO_STORIES, color=ft.Colors.WHITE, size=18), bgcolor=ACCENT, border_radius=6, padding=pa(4)),
                ft.Text("Smart Library", size=16, weight=ft.FontWeight.BOLD, color=TEXT_PRI),
            ], spacing=10)),
            ft.Container(width=30),
            ft.Row([
                nav_link("Dashboard", state["active_page"] == "Dashboard", lambda e: set_active_page("Dashboard")),
                nav_link("Books", state["active_page"] == "Books", lambda e: set_active_page("Books")),
                nav_link("Settings", state["active_page"] == "Settings", lambda e: set_active_page("Settings")),
            ], spacing=20),
            ft.Container(expand=True),
            ft.Container(width=280, height=38, bgcolor=BG_CARD, border=ba(1, BORDER), border_radius=8,
                content=ft.TextField(hint_text="Search catalog, books, authors…", hint_style=ft.TextStyle(color=TEXT_SEC, size=11),
                    border=ft.InputBorder.NONE, color=TEXT_PRI, bgcolor="transparent", content_padding=ft.Padding(left=10, right=10, top=5, bottom=0),
                    text_size=12, value=state["q"], on_change=on_search, prefix_icon=ft.Icons.SEARCH)),
                    ft.Container(width=20),
            ft.IconButton(
                ref=theme_btn_ref,
                icon=ft.Icons.LIGHT_MODE if page.theme_dark else ft.Icons.DARK_MODE,
                icon_color=TEXT_SEC,
                icon_size=22,
                tooltip="Switch to light mode" if page.theme_dark else "Switch to dark mode",
                on_click=toggle_theme,
        ),
ft.Container(width=8),
ft.Stack([ft.Icon(ft.Icons.NOTIFICATIONS_OUTLINED, color=TEXT_SEC, size=24),
    ft.Container(bgcolor=ft.Colors.RED_ACCENT, width=8, height=8, border_radius=4, right=2, top=2, border=ba(1, BG_NAV))]),
ft.Container(width=20),
            ft.Row([ft.VerticalDivider(width=1, color=BORDER), ft.Container(width=10),
                ft.Column([ft.Text(logged_user, size=11, weight=ft.FontWeight.BOLD, color=TEXT_PRI),
                    ft.Container(content=ft.Text("GOLD MEMBER", size=8, weight=ft.FontWeight.BOLD, color="#DAA520"), bgcolor="#3d2b00", border_radius=4, padding=ps(6, 2))], spacing=2, horizontal_alignment=ft.CrossAxisAlignment.END),
                ft.Container(width=10),
                ft.PopupMenuButton(
                    tooltip="Account Menu",
                    content=ft.Container(
                        width=32, height=32,
                        content=ft.Stack([
                            ft.CircleAvatar(content=ft.Text(logged_initials, size=10, weight=ft.FontWeight.BOLD), bgcolor=ACCENT, color=ft.Colors.WHITE, radius=16),
                            ft.Container(bgcolor=ft.Colors.GREEN_ACCENT, width=10, height=10, border_radius=5, right=0, bottom=0, border=ba(2, BG_NAV))
                        ])
                    ),
                    items=[
                        ft.PopupMenuItem(
                            content=ft.Row([
                                ft.Icon(ft.Icons.LOGOUT, size=18, color=TEXT_SEC),
                                ft.Text("Log Out", size=13, color=TEXT_PRI)
                            ]),
                            on_click=do_logout
                        )
                    ]
                )],
                spacing=0, vertical_alignment=ft.CrossAxisAlignment.CENTER),
        ]))

    def dashboard_reco_card(book):
        card_w = 220
        image_h = 100
        return ft.Container(
            width=card_w,
            border=ba(1, BORDER),
            border_radius=12,
            bgcolor=BG_CARD,
            content=ft.Column(
                spacing=0,
                controls=[
                    ft.Container(
                        height=image_h,
                        border_radius=brtop(12),
                        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                        content=ft.Stack(
                            controls=[
                                ft.Image(src=book["cover"], fit=ft.BoxFit.COVER, width=card_w, height=image_h),
                                ft.Container(
                                    left=8,
                                    top=8,
                                    bgcolor=BG_NAV,
                                    border_radius=6,
                                    padding=ps(7, 3),
                                    content=ft.Text(book["genre"], size=8, color=TEXT_PRI, weight=ft.FontWeight.W_600),
                                ),
                            ]
                        ),
                    ),
                    ft.Container(
                        padding=pa(12),
                        content=ft.Column(
                            spacing=6,
                            controls=[
                                ft.Row(
                                    [
                                        ft.Text(book["title"], size=11, color=TEXT_PRI, weight=ft.FontWeight.BOLD, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS, expand=True),
                                        ft.Icon(ft.Icons.STAR_BORDER_ROUNDED, size=12, color=TEXT_SEC),
                                        ft.Text("4.8", size=9, color=TEXT_PRI, weight=ft.FontWeight.W_600),
                                    ],
                                    spacing=4,
                                    tight=True,
                                ),
                                ft.Text(book["author"], size=9, color=TEXT_SEC, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                                ft.Row(
                                    [
                                        ft.Icon(ft.Icons.MENU_BOOK_OUTLINED, size=10, color=TEXT_SEC),
                                        ft.Text(book["tag"], size=9, color=TEXT_SEC),
                                        ft.Container(expand=True),
                                        ft.Text("Library", size=9, color=TEXT_SEC),
                                    ],
                                    tight=True,
                                ),
                                ft.FilledButton(
                                    "Borrow",
                                    width=card_w,
                                    height=28,
                                    on_click=lambda e, t=book["title"]: show_snack(page, t),
                                    style=ft.ButtonStyle(
                                        bgcolor=ACCENT2,
                                        color=TEXT_PRI,
                                        shape=ft.RoundedRectangleBorder(radius=8),
                                        padding=ps(0, 10),
                                    ),
                                ),
                            ],
                        ),
                    ),
                ],
            ),
        )

    def dashboard_digital_book_card(book, time_label):
        return ft.Container(
            width=126,
            content=ft.Column(
                spacing=4,
                controls=[
                    ft.Container(
                        width=126,
                        height=172,
                        border_radius=10,
                        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                        content=ft.Image(src=book["cover"], fit=ft.BoxFit.COVER),
                    ),
                    ft.Text(book["title"], size=11, color=TEXT_PRI, weight=ft.FontWeight.W_600, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                    ft.Text(book["author"], size=9, color=TEXT_SEC, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                    ft.Row(
                        [
                            ft.Icon(ft.Icons.ACCESS_TIME, size=10, color=TEXT_SEC),
                            ft.Text(time_label, size=9, color=TEXT_SEC),
                        ],
                        spacing=4,
                    ),
                ],
            ),
        )

    dashboard_table_rows = [
        {"title": "Thinking, Fast and Slow", "author": "Daniel Kahneman", "borrowed": "Oct 12, 2023", "due": "Oct 26, 2023", "overdue": True},
        {"title": "The Pragmatic Programmer", "author": "Andrew Hunt", "borrowed": "Oct 05, 2023", "due": "Nov 05, 2023", "overdue": False},
        {"title": "Dune", "author": "Frank Herbert", "borrowed": "Oct 18, 2023", "due": "Nov 01, 2023", "overdue": False},
        {"title": "Atomic Habits", "author": "James Clear", "borrowed": "Oct 10, 2023", "due": "Oct 24, 2023", "overdue": True},
        {"title": "The Silent Patient", "author": "Alex Michaelides", "borrowed": "Oct 15, 2023", "due": "Oct 29, 2023", "overdue": False},
    ]
    recent_digital = dashboard_recent_digital_books()
    digital_col_1 = [dashboard_digital_book_card(book, t_label) for book, t_label in recent_digital[:2]]
    digital_col_2 = [dashboard_digital_book_card(book, t_label) for book, t_label in recent_digital[2:4]]

    # ── Dashboard ───────────────────────────────────────────
    dashboard = ft.Container(
        bgcolor=BG_DARK,
        padding=ps(40, 30),
        expand=True,
        content=ft.Column(
            spacing=18,
            controls=[
                ft.Row(
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    spacing=22,
                    controls=[
                        ft.Column(
                            expand=True,
                            spacing=14,
                            controls=[
                                ft.Text("Welcome back,", size=45/1.5, color=TEXT_PRI, weight=ft.FontWeight.BOLD),
                                ft.Text("Nurlan.", size=45/1.5, color=ACCENT2, weight=ft.FontWeight.BOLD),
                                ft.Text(
                                    "You've read 124 pages since your last visit. Your current goals are on track for this\nmonth. Explore your dashboard to manage your books and fines.",
                                    size=13,
                                    color=TEXT_SEC,
                                ),
                                ft.Row(
                                    spacing=14,
                                    controls=[
                                        ft.FilledButton(
                                            "Browse Catalog",
                                            style=ft.ButtonStyle(
                                                bgcolor="#6f5fa8",
                                                color=TEXT_PRI,
                                                shape=ft.RoundedRectangleBorder(radius=12),
                                                padding=ps(20, 12),
                                            ),
                                        ),
                                        ft.OutlinedButton(
                                            "View Reading History",
                                            style=ft.ButtonStyle(
                                                color=TEXT_PRI,
                                                side=ft.BorderSide(1, "#3a3351"),
                                                bgcolor=BG_NAV,
                                                shape=ft.RoundedRectangleBorder(radius=12),
                                                padding=ps(20, 12),
                                            ),
                                        ),
                                    ],
                                ),
                            ],
                        ),
                        ft.Container(
                            width=460,
                            gradient=ft.LinearGradient(
                                begin=ft.Alignment(-1, -1),
                                end=ft.Alignment(1, 1),
                                colors=["#201b34", "#1a172b"],
                            ),
                            border=ba(1, "#2b2740"),
                            border_radius=14,
                            padding=pa(22),
                            content=ft.Row(
                                [
                                    ft.Column(
                                        expand=True,
                                        spacing=12,
                                        controls=[
                                            ft.Row(
                                                [
                                                    ft.Container(
                                                        width=34,
                                                        height=34,
                                                        border_radius=8,
                                                        bgcolor="#5e5490",
                                                        alignment=ft.Alignment(0, 0),
                                                        content=ft.Icon(ft.Icons.MENU_BOOK_OUTLINED, size=18, color="#1a1730"),
                                                    ),
                                                    ft.Text("SmartLib", size=38/2, color="#8e84b3", weight=ft.FontWeight.W_700),
                                                ],
                                                spacing=10,
                                            ),
                                            ft.Text("CARD HOLDER", size=10, color="#8f86ab", weight=ft.FontWeight.W_600),
                                            ft.Text("Nurlan Orujov", size=17, color=TEXT_PRI, weight=ft.FontWeight.BOLD),
                                            ft.Row(
                                                [
                                                    ft.Column([ft.Text("MEMBER ID", size=10, color="#8f86ab", weight=ft.FontWeight.W_600), ft.Text("SL-9402-2024", size=13, color=TEXT_PRI, weight=ft.FontWeight.W_600)], spacing=2),
                                                    ft.Container(width=24),
                                                    ft.Column([ft.Text("EXPIRY DATE", size=10, color="#8f86ab", weight=ft.FontWeight.W_600), ft.Text("12 | 2026", size=13, color=TEXT_PRI, weight=ft.FontWeight.W_600)], spacing=2),
                                                ]
                                            ),
                                        ],
                                    ),
                                    ft.Column(
                                        spacing=8,
                                        horizontal_alignment=ft.CrossAxisAlignment.END,
                                        controls=[
                                            ft.Container(
                                                bgcolor="#f1b72f",
                                                border_radius=14,
                                                padding=ps(14, 6),
                                                content=ft.Text("Gold Member", size=10, color="#312200", weight=ft.FontWeight.BOLD),
                                            ),
                                            ft.Container(height=2),
                                            ft.Container(
                                                width=120,
                                                height=90,
                                                content=ft.Stack(
                                                    controls=[
                                                        # Shelf line
                                                        ft.Container(
                                                            left=2,
                                                            right=2,
                                                            bottom=4,
                                                            height=2,
                                                            bgcolor="#34304a",
                                                            border_radius=2,
                                                        ),
                                                        # Organized "books"
                                                        ft.Container(
                                                            width=16,
                                                            height=78,
                                                            right=86,
                                                            bottom=6,
                                                            border_radius=8,
                                                            bgcolor="#5c5873",
                                                        ),
                                                        ft.Container(
                                                            width=14,
                                                            height=66,
                                                            right=64,
                                                            bottom=6,
                                                            border_radius=8,
                                                            bgcolor="#4f4a68",
                                                        ),
                                                        ft.Container(
                                                            width=12,
                                                            height=72,
                                                            right=46,
                                                            bottom=6,
                                                            border_radius=8,
                                                            bgcolor="#615c7d",
                                                        ),
                                                        ft.Container(
                                                            width=14,
                                                            height=62,
                                                            right=28,
                                                            bottom=6,
                                                            border_radius=8,
                                                            bgcolor="#534e6d",
                                                        ),
                                                        # One leaning book for realism
                                                        ft.Container(
                                                            width=14,
                                                            height=80,
                                                            right=8,
                                                            bottom=6,
                                                            border_radius=8,
                                                            bgcolor="#696484",
                                                            rotate=ft.Rotate(0.36),
                                                        ),
                                                    ],
                                                ),
                                            ),
                                        ],
                                    ),
                                ]
                            ),
                        ),
                    ],
                ),
                ft.Row(
                    spacing=12,
                    controls=[
                        dashboard_metric_card("Books With You", "5", "3 physical + 2 digital", ACCENT2),
                        dashboard_metric_card("E-Book Reads", "12", "Current month", TAG_EBOOK),
                        dashboard_metric_card("Late Fee Due", "$18.50", "Please pay soon", ft.Colors.RED_ACCENT),
                        dashboard_metric_card("Reading Goal", "5/10", "50% complete", TAG_EBOOK),
                    ],
                ),
                ft.Row(
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    spacing=14,
                    controls=[
                        ft.Container(
                            expand=2,
                            bgcolor=BG_CARD,
                            border=ba(1, BORDER),
                            border_radius=12,
                            padding=pa(0),
                            content=ft.Column(
                                spacing=0,
                                controls=[
                                    ft.Container(
                                        padding=ps(20, 16),
                                        content=ft.Row(
                                            [
                                                ft.Row(
                                                    [
                                                        ft.Icon(ft.Icons.AUTO_STORIES_OUTLINED, size=18, color=TEXT_SEC),
                                                        ft.Column(
                                                            [
                                                                ft.Text("My Physical Books", size=38/2, color=TEXT_PRI, weight=ft.FontWeight.BOLD),
                                                                ft.Text("Management of your active physical library loans.", size=11, color=TEXT_SEC),
                                                            ],
                                                            spacing=2,
                                                        ),
                                                    ],
                                                    spacing=8,
                                                ),
                                                ft.Container(expand=True),
                                                ft.Container(
                                                    bgcolor=BG_NAV,
                                                    border_radius=16,
                                                    padding=ps(14, 8),
                                                    content=ft.Text("Active Loans: 5", size=11, color=TEXT_PRI, weight=ft.FontWeight.W_600),
                                                ),
                                            ],
                                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                        ),
                                    ),
                                    ft.Container(
                                        bgcolor=BG_NAV,
                                        border=bbtm(BORDER),
                                        border_radius=brtop(0),
                                        padding=ps(20, 12),
                                        content=ft.Row(
                                        [
                                            ft.Text("Book Title", size=12, color=TEXT_PRI, weight=ft.FontWeight.W_600, expand=2),
                                            ft.Text("Borrowed Date", size=12, color=TEXT_PRI, weight=ft.FontWeight.W_600, expand=1),
                                            ft.Text("Due Date", size=12, color=TEXT_PRI, weight=ft.FontWeight.W_600, expand=1),
                                            ft.Text("Action", size=12, color=TEXT_PRI, weight=ft.FontWeight.W_600, text_align=ft.TextAlign.RIGHT, expand=1),
                                        ]
                                    ),
                                    ),
                                    *[
                                        ft.Column(
                                            spacing=0,
                                            controls=[
                                                ft.Container(
                                                    padding=ps(20, 16),
                                                    content=ft.Row(
                                                        [
                                                            ft.Column(
                                                                [
                                                                    ft.Text(row["title"], size=16, color=TEXT_PRI, weight=ft.FontWeight.W_600, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                                                                    ft.Text(row["author"], size=11, color=TEXT_SEC),
                                                                ],
                                                                spacing=2,
                                                                expand=2,
                                                            ),
                                                            ft.Text(row["borrowed"], size=12, color=TEXT_PRI, expand=1),
                                                            ft.Row(
                                                                [
                                                                    ft.Icon(ft.Icons.ERROR_OUTLINE, size=14, color=ft.Colors.RED_300) if row["overdue"] else ft.Container(width=14),
                                                                    ft.Text(
                                                                        row["due"],
                                                                        size=12,
                                                                        color=ft.Colors.RED_300 if row["overdue"] else TEXT_PRI,
                                                                        weight=ft.FontWeight.W_600 if row["overdue"] else ft.FontWeight.W_500,
                                                                    ),
                                                                ],
                                                                spacing=8,
                                                                expand=1,
                                                            ),
                                                            ft.Text("Request Extension", size=12, color=TEXT_PRI, text_align=ft.TextAlign.RIGHT, expand=1),
                                                        ],
                                                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                                    ),
                                                ),
                                                ft.Divider(color=BORDER, height=1, thickness=1),
                                            ],
                                        ) for row in dashboard_table_rows
                                    ],
                                    ft.Container(
                                        alignment=ft.Alignment(0, 0),
                                        padding=ps(0, 14),
                                        content=ft.TextButton(
                                            "See loan history  >",
                                            style=ft.ButtonStyle(color=TEXT_PRI),
                                        ),
                                    ),
                                ],
                            ),
                        ),
                        ft.Container(
                            width=300,
                            content=ft.Column(
                            spacing=12,
                            controls=[
                                ft.Container(
                                    bgcolor=BG_CARD,
                                    border=ba(1, BORDER),
                                    border_radius=12,
                                    padding=pa(12),
                                    content=ft.Column(
                                        spacing=8,
                                        controls=[
                                            ft.Row(
                                                [
                                                    ft.Icon(ft.Icons.MENU_BOOK_OUTLINED, size=17, color=TEXT_SEC),
                                                    ft.Text("My Digital Library", size=33/2, color=TEXT_PRI, weight=ft.FontWeight.BOLD),
                                                ],
                                                spacing=5,
                                            ),
                                            ft.Text("Recently accessed digital resources.", size=11, color=TEXT_SEC),
                                            ft.Row(
                                                spacing=8,
                                                vertical_alignment=ft.CrossAxisAlignment.START,
                                                alignment=ft.MainAxisAlignment.START,
                                                controls=[
                                                    ft.Column(spacing=8, width=126, controls=digital_col_1),
                                                    ft.Column(spacing=8, width=126, controls=digital_col_2),
                                                ],
                                            ),
                                            ft.FilledButton(
                                                "Go to Digital Reader",
                                                width=264,
                                                style=ft.ButtonStyle(
                                                    bgcolor=ft.Colors.WHITE,
                                                    color="#111827",
                                                    shape=ft.RoundedRectangleBorder(radius=8),
                                                    padding=ps(0, 12),
                                                ),
                                            ),
                                        ],
                                    ),
                                ),
                                ft.Container(
                                    bgcolor=BG_CARD,
                                    border=ba(1, BORDER),
                                    border_radius=12,
                                    padding=pa(14),
                                    content=ft.Column(
                                        spacing=10,
                                        controls=[
                                            ft.Row(
                                                [
                                                    ft.Icon(ft.Icons.RECEIPT_LONG_OUTLINED, size=16, color=ft.Colors.RED_300),
                                                    ft.Text("Outstanding Fines", size=15, color=ft.Colors.RED_300, weight=ft.FontWeight.BOLD),
                                                ],
                                                spacing=6,
                                            ),
                                            ft.Text("Unpaid late fees require immediate attention.", size=10, color=TEXT_SEC),
                                            ft.Container(
                                                bgcolor="#3a1018",
                                                border_radius=12,
                                                padding=ps(14, 12),
                                                content=ft.Row(
                                                    [
                                                        ft.Text("Total Unpaid", size=13/1.2, color="#f2cbd1"),
                                                        ft.Container(expand=True),
                                                        ft.Text("$18.50", size=38/2, color=ft.Colors.RED_ACCENT, weight=ft.FontWeight.BOLD),
                                                    ]
                                                ),
                                            ),
                                            ft.Row([ft.Text("Thinking, Fast and Slow (12 days)", size=10, color=TEXT_SEC), ft.Container(expand=True), ft.Text("$12.00", size=10, color=TEXT_PRI)]),
                                            ft.Row([ft.Text("Atomic Habits (4 days)", size=10, color=TEXT_SEC), ft.Container(expand=True), ft.Text("$6.50", size=10, color=TEXT_PRI)]),
                                            ft.FilledButton(
                                                "Pay Now (Card/Apple Pay)",
                                                style=ft.ButtonStyle(
                                                    bgcolor=ft.Colors.RED_ACCENT,
                                                    color=ft.Colors.WHITE,
                                                    shape=ft.RoundedRectangleBorder(radius=8),
                                                    padding=ps(14, 12),
                                                ),
                                            ),
                                        ],
                                    ),
                                ),
                            ],
                        )),
                    ],
                ),
                ft.Container(height=8),
                ft.Row([
                    ft.Row(
                        [
                            ft.Icon(ft.Icons.STAR_BORDER_ROUNDED, size=18, color=TEXT_PRI),
                            ft.Text("Recommended for You", size=23, color=TEXT_PRI, weight=ft.FontWeight.BOLD),
                        ],
                        spacing=8,
                    ),
                    ft.Container(expand=True),
                    ft.Text("See All Suggestions  >", size=13/1.4, color=TEXT_SEC, weight=ft.FontWeight.W_500),
                ]),
                ft.Row(
                    ref=dashboard_reco_row_ref,
                    spacing=14,
                    wrap=True,
                    run_spacing=14,
                    controls=[dashboard_reco_card(b) for b in dashboard_recommended_books()],
                ),
            ],
        ),
    )

# ─── CRUD helpers ────────────────────────────────────────────
    def db_get_all_users():
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT id, username, email, created FROM users ORDER BY id DESC")
        rows = c.fetchall()
        conn.close()
        return rows

    def db_update_user(user_id, new_username, new_email):
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("UPDATE users SET username=?, email=? WHERE id=?",
                      (new_username.strip(), new_email.strip().lower(), user_id))
            conn.commit()
            conn.close()
            return True, "User updated."
        except sqlite3.IntegrityError as e:
            msg = "Username taken." if "username" in str(e) else "Email already used."
            return False, msg

    def db_delete_user(user_id):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("DELETE FROM users WHERE id=?", (user_id,))
        conn.commit()
        conn.close()

    # ─── Settings / CRUD page ────────────────────────────────────
    crud_list_ref = ft.Ref[ft.Column]()
    crud_msg_ref  = ft.Ref[ft.Text]()

    def build_user_row(uid, uname, uemail, ucreated):
        # Added label="Username" and label="Email" so the user knows what field is what
        name_field  = ft.TextField(value=uname, label="Username", text_size=12, color=TEXT_PRI,
                                   bgcolor=BG_CARD, border_color=BORDER,
                                   focused_border_color=ACCENT, border_radius=8,
                                   content_padding=ft.Padding(left=10, right=10, top=8, bottom=8),
                                   expand=True)
        email_field = ft.TextField(value=uemail, label="Email", text_size=12, color=TEXT_PRI,
                                   bgcolor=BG_CARD, border_color=BORDER,
                                   focused_border_color=ACCENT, border_radius=8,
                                   content_padding=ft.Padding(left=10, right=10, top=8, bottom=8),
                                   expand=True)

        def save(e):
            # FIXED INDENTATION HERE
            new_name = name_field.value.strip()
            new_email = email_field.value.strip()

            # 1. Check for empty fields
            if not new_name or not new_email:
                crud_msg_ref.current.value = "Username and Email cannot be empty."
                crud_msg_ref.current.color = ft.Colors.RED_300
                crud_msg_ref.current.update()
                return

            # 2. Strict Email Validation using Regex
            email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]{2,}+$"
            if not re.match(email_regex, new_email):
                crud_msg_ref.current.value = "Invalid email format (e.g., user@domain.com)."
                crud_msg_ref.current.color = ft.Colors.RED_300
                crud_msg_ref.current.update()
                return

            # 3. Proceed with database update if validation passes
            ok, msg = db_update_user(uid, new_name, new_email)
            crud_msg_ref.current.value = msg
            crud_msg_ref.current.color = TAG_EBOOK if ok else ft.Colors.RED_300
            crud_msg_ref.current.update()
            
            if ok:
                reload_users()

        def delete(e):
            db_delete_user(uid)
            crud_msg_ref.current.value = f"User #{uid} deleted."
            crud_msg_ref.current.color = ft.Colors.RED_300
            crud_msg_ref.current.update()
            reload_users()

        return ft.Container(
            bgcolor=BG_CARD, border=ba(1, BORDER), border_radius=10,
            padding=pa(14),
            content=ft.Column(spacing=8, controls=[
                ft.Row([
                    ft.Text(f"#{uid}", size=11, color=ACCENT, weight=ft.FontWeight.BOLD, width=30),
                    ft.Text(f"Joined: {ucreated[:10]}", size=10, color=TEXT_SEC),
                ]),
                ft.Row([name_field, email_field], spacing=10),
                ft.Row([
                    ft.FilledButton("Save", height=32,
                        on_click=save,
                        style=ft.ButtonStyle(bgcolor=ACCENT, color=ft.Colors.WHITE,
                                             shape=ft.RoundedRectangleBorder(radius=8))),
                    ft.FilledButton("Delete", height=32,
                        on_click=delete,
                        style=ft.ButtonStyle(bgcolor=ft.Colors.RED_400, color=ft.Colors.WHITE,
                                             shape=ft.RoundedRectangleBorder(radius=8))),
                ], spacing=10),
            ])
        )

    def reload_users():
        if not crud_list_ref.current:
            return
        rows = db_get_all_users()
        crud_list_ref.current.controls = [
            build_user_row(r[0], r[1], r[2], r[3]) for r in rows
        ] if rows else [ft.Text("No users found.", size=12, color=TEXT_SEC)]
        crud_list_ref.current.update()

    settings_page = ft.Container(
        bgcolor=BG_DARK, expand=True, padding=ps(40, 30),
        content=ft.Column(spacing=16, scroll=ft.ScrollMode.AUTO, controls=[
            ft.Text("Settings", size=28, color=TEXT_PRI, weight=ft.FontWeight.BOLD),
            ft.Text("Manage registered users — Edit or delete any account.", size=12, color=TEXT_SEC),
            ft.Divider(color=BORDER, height=1),
            ft.Row([
                ft.Icon(ft.Icons.PEOPLE_OUTLINE, color=ACCENT, size=18),
                ft.Text("User Management (CRUD)", size=15, color=TEXT_PRI, weight=ft.FontWeight.BOLD),
                ft.Container(expand=True),
                ft.FilledButton("Refresh", height=32,
                    on_click=lambda e: reload_users(),
                    style=ft.ButtonStyle(bgcolor=BG_CARD, color=TEXT_PRI,
                                         side=ft.BorderSide(1, BORDER),
                                         shape=ft.RoundedRectangleBorder(radius=8))),
            ], spacing=10),
            ft.Text(ref=crud_msg_ref, value="", size=12, color=TAG_EBOOK),
            ft.Column(ref=crud_list_ref, spacing=10,
                      controls=[ft.Text("Loading...", size=12, color=TEXT_SEC)]),
        ])
    )

    # ── Hero ────────────────────────────────────────────────
    hero_grad_1 = "#2a1040" if page.theme_dark else "#efe8ff"
    hero_grad_2 = "#0f0a1a" if page.theme_dark else "#f8f5ff"
    hero_badge_bg = "#252535" if page.theme_dark else "#e9defa"
    hero_title = "#ffffff" if page.theme_dark else "#2b1b35"
    hero_sub = "#ccccdd" if page.theme_dark else "#5d4b78"
    hero_desc = "#aaaacc" if page.theme_dark else "#6f5f86"
    hero_meta = "#8888aa" if page.theme_dark else "#7b6a92"
    hero_secondary_bg = ft.Colors.BLACK if page.theme_dark else "#f3f4f6"
    hero_secondary_border = ft.Colors.WHITE24 if page.theme_dark else "#d1d5db"
    hero_primary_btn = "#6b608a" if page.theme_dark else "#8b7bb8"

    hero = ft.Container(
        gradient=ft.LinearGradient(
            begin=ft.Alignment(-1, -0.5),
            end=ft.Alignment(1, 0.5),
            colors=[hero_grad_1, hero_grad_2],
        ),
        padding=ft.Padding(left=120, right=120, top=30, bottom=30),
        border_radius=20,
        margin=pa(20),
        content=ft.Row(
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20,
            controls=[
                ft.Column(
                    expand=True,
                    spacing=0,
                    controls=[
                        ft.Container(
                            bgcolor=hero_badge_bg,
                            border_radius=15,
                            padding=ps(12, 6),
                            content=ft.Row(
                                [
                                    ft.Text("◉", color=ACCENT2, size=12, weight=ft.FontWeight.BOLD),
                                    ft.Text(
                                        "FEATURED BOOK OF THE MONTH",
                                        size=9,
                                        color=ACCENT2,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                ],
                                spacing=6,
                                width=220,
                            ),
                        ),
                        ft.Container(height=30),
                        ft.Text(
                            "The Age of AI: And\nOur Human Future",
                            size=28,
                            weight=ft.FontWeight.BOLD,
                            color=hero_title,
                        ),
                        ft.Container(height=10),
                        ft.Text(
                            "by Henry A. Kissinger, Eric Schmidt, Daniel Huttenlocher",
                            size=13,
                            color=hero_sub,
                            weight=ft.FontWeight.W_500,
                        ),
                        ft.Container(height=24),
                        ft.Container(
                            width=480,
                            content=ft.Text(
                                "Three of the world's most accomplished thinkers come together to explore how Artificial Intelligence will change our relationships with knowledge, politics, and our very societies.",
                                size=13,
                                color=hero_desc,
                                weight=ft.FontWeight.W_400,
                            ),
                        ),
                        ft.Container(height=34),
                        ft.Row(
                            [
                                ft.Row(
                                    [
                                        ft.Icon(ft.Icons.STAR_ROUNDED, color="#f59e0b", size=14),
                                        ft.Text(
                                            "4.7 / 5.0",
                                            size=11,
                                            color="#2b1b35" if not page.theme_dark else "#f0f0f8",
                                            weight=ft.FontWeight.W_600,
                                        ),
                                        ft.Text("2.1k reviews", size=10, color=hero_meta),
                                    ],
                                    spacing=4,
                                ),
                                ft.Container(width=1, height=16, bgcolor=BORDER),
                                ft.Row(
                                    [
                                        ft.Icon(ft.Icons.MENU_BOOK_OUTLINED, color=ACCENT2, size=14),
                                        ft.Text("272 pages", size=11, color=hero_meta),
                                    ],
                                    spacing=4,
                                ),
                                ft.Container(width=1, height=16, bgcolor=BORDER),
                                ft.Row(
                                    [
                                        ft.Icon(ft.Icons.LANGUAGE, color=ACCENT2, size=14),
                                        ft.Text("English", size=11, color=hero_meta),
                                    ],
                                    spacing=4,
                                ),
                                ft.Container(width=1, height=16, bgcolor=BORDER),
                                ft.Row(
                                    [
                                        ft.Icon(ft.Icons.CALENDAR_TODAY_OUTLINED, color=ACCENT2, size=14),
                                        ft.Text("Nov 2021", size=11, color=hero_meta),
                                    ],
                                    spacing=4,
                                ),
                            ],
                            spacing=12,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        ft.Container(height=34),
                        ft.Row(
                            [
                                ft.FilledButton(
                                    "Borrow Now",
                                    on_click=lambda e: show_snack(page, "The Age of AI"),
                                    style=ft.ButtonStyle(
                                        bgcolor=hero_primary_btn,
                                        color=ft.Colors.WHITE,
                                        shape=ft.RoundedRectangleBorder(radius=8),
                                        padding=ps(24, 14),
                                        shadow_color="#9333ea22",
                                        elevation=6,
                                    ),
                                ),
                                ft.FilledButton(
                                    "Sample Read",
                                    style=ft.ButtonStyle(
                                        color=TEXT_PRI,
                                        bgcolor=hero_secondary_bg,
                                        side=ft.BorderSide(1, hero_secondary_border),
                                        shape=ft.RoundedRectangleBorder(radius=8),
                                        padding=ps(24, 14),
                                    ),
                                ),
                            ],
                            spacing=15,
                        ),
                    ],
                ),
                ft.Container(
                    width=260, height=370,
                    border_radius=12,
                    border=None,
                    margin=ft.Margin(left=0, right=40, top=0, bottom=0),
                    shadow=ft.BoxShadow(
                        blur_radius=50,
                        color="#0080FF" if page.theme_dark else "#71797E",
                        offset=ft.Offset(8, 12),
                        spread_radius=6,
            ),
            rotate=ft.Rotate(0.05),
                    content=ft.Container(
                        border_radius=12,
                        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                        content=ft.Image(
                            src="https://oxfordbookstore.com/cdn/shop/files/719tzOXIW0L.jpg?v=1762881145",
                            fit=ft.BoxFit.CONTAIN,
                        ),
                    ),
                ),
            ],
        ),
    )

    # ── Catalog ──────────────────────────────────────────────
    catalog = ft.Container(bgcolor=BG_DARK, padding=ps(80, 44),
        content=ft.Column(spacing=0, controls=[
            ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.END, controls=[
                ft.Column([ft.Text("Browse Catalog", size=22, weight=ft.FontWeight.BOLD, color=TEXT_PRI),
                    ft.Text("Find your next favorite read from our extensive digital collection.", size=12, color=TEXT_SEC)], spacing=4, expand=True),
                ft.Container(bgcolor=BG_NAV, padding=ps(14, 8), border_radius=15, border=ba(1, BORDER),
                    content=ft.Row([
                        ft.IconButton(ft.Icons.GRID_VIEW, icon_color=TEXT_SEC, icon_size=18, tooltip="Switch to Extra Large View", on_click=cycle_view_mode),
                        ft.VerticalDivider(width=1, color=BORDER),
                        ft.Text("SHOW ONLY AVAILABLE BOOKS", size=9, color=TEXT_SEC, weight=ft.FontWeight.BOLD),
                        ft.Switch(value=False, active_color=ACCENT),
                    ], spacing=12))]),
            ft.Container(height=26),
            ft.Row(ref=cat_row_ref, spacing=8, wrap=True, controls=[
                ft.Container(content=ft.Text(cat, size=11, color=ft.Colors.WHITE if cat == "All" else TEXT_SEC),
                    bgcolor=ACCENT if cat == "All" else BG_CARD, border=ba(1, ACCENT if cat == "All" else BORDER), border_radius=18, padding=ps(16, 8), on_click=lambda e, c=cat: pick_cat(c)) for cat in CATEGORIES]),
            ft.Container(height=16),
            ft.Container(bgcolor=BG_NAV, border_radius=12, border=ba(1, BORDER), padding=ps(16, 12),
                content=ft.Row([ft.Icon(ft.Icons.TUNE, size=14, color=TEXT_SEC), ft.Text("Advanced Search and Filter Options", size=12, color=TEXT_SEC)], spacing=10)),
            ft.Container(height=34),
            ft.Row(ref=grid_ref, controls=[book_card(b, page, state["view_mode"]) for b in BOOKS], wrap=True, spacing=16, run_spacing=24),
            ft.Container(height=40),
            ft.Container(bgcolor=BG_CARD, border_radius=12, border=ba(1, BORDER), alignment=ft.Alignment(0, 0), padding=ps(0, 34),
                content=ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4, controls=[
                    ft.Icon(ft.Icons.LIBRARY_BOOKS_OUTLINED, color=TEXT_SEC, size=38), ft.Container(height=10),
                    ft.Text("End of Current Catalog", size=15, weight=ft.FontWeight.W_600, color=TEXT_PRI, text_align=ft.TextAlign.CENTER),
                    ft.Text("We are constantly adding new titles.\nCheck back soon for more discoveries.", size=12, color=TEXT_SEC, text_align=ft.TextAlign.CENTER),
                    ft.Container(height=10), ft.TextButton("Request a New Book →", style=ft.ButtonStyle(color=ACCENT))])),
        ]))

    # ── Footer ───────────────────────────────────────────────
    footer = ft.Container(bgcolor=BG_NAV, padding=ps(80, 26),
        content=ft.Column(spacing=0, controls=[
            ft.Divider(color=BORDER, height=1), ft.Container(height=28),
            ft.Row(vertical_alignment=ft.CrossAxisAlignment.START, controls=[
                ft.Column([ft.Row([ft.Icon(ft.Icons.AUTO_STORIES, color=ACCENT, size=18), ft.Text("Smart Library", size=13, weight=ft.FontWeight.BOLD, color=TEXT_PRI)], spacing=6),
                    ft.Container(height=8), ft.Text("Empowering readers through modern\ntechnology since 2024.", size=11, color=TEXT_SEC)], expand=True, spacing=0),
                ft.Column([ft.Text("Support", size=12, weight=ft.FontWeight.BOLD, color=TEXT_PRI), ft.Container(height=8),
                    ft.TextButton("Help Center", style=ft.ButtonStyle(color=TEXT_SEC)), ft.TextButton("Loan Policies", style=ft.ButtonStyle(color=TEXT_SEC)), ft.TextButton("Contact Librarian", style=ft.ButtonStyle(color=TEXT_SEC))], spacing=0),
                ft.Container(width=44),
                ft.Column([ft.Text("Account", size=12, weight=ft.FontWeight.BOLD, color=TEXT_PRI), ft.Container(height=8),
                    ft.TextButton("Membership Details", style=ft.ButtonStyle(color=TEXT_SEC)), ft.TextButton("Privacy Settings", style=ft.ButtonStyle(color=TEXT_SEC)), ft.TextButton("Reading Preferences", style=ft.ButtonStyle(color=TEXT_SEC))], spacing=0)]),
            ft.Container(height=24), ft.Divider(color=BORDER, height=1), ft.Container(height=14),
            ft.Row([ft.Text("© 2026 SMART LIBRARY. ALL RIGHTS RESERVED.", size=10, color=TEXT_SEC), ft.Container(expand=True),
                ft.Text("SYSTEM ONLINE", size=10, color=TAG_EBOOK), ft.Container(width=18), ft.Text("VERSION 2.1.0", size=10, color=TEXT_SEC)])]))

    if state["active_page"] == "Dashboard":
        main_content = ft.Column(spacing=0, controls=[dashboard, footer])
    elif state["active_page"] == "Settings":
        main_content = settings_page
    else:
        main_content = ft.Column(spacing=0, controls=[hero, catalog, footer])

    page.add(ft.Column(spacing=0, expand=True, controls=[navbar, main_content]))

def start(page: ft.Page):
    auth_page(page, on_success=main)

ft.run(start)

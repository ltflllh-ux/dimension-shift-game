import sqlite3
from recipes import RECIPES

def setup_database():
    """
    SQLite veritabanını ve tarifler tablosunu oluşturur,
    ve başlangıç verilerini ekler.
    """
    conn = sqlite3.connect('scantocook/recipes.db')
    cursor = conn.cursor()

    # Tarifler tablosunu oluştur
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS recipes (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        instructions TEXT NOT NULL
    )
    ''')

    # Malzemeler tablosunu oluştur
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ingredients (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL UNIQUE
    )
    ''')

    # Tarif-Malzeme ilişkisi için bir birleşim tablosu oluştur
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS recipe_ingredients (
        recipe_id INTEGER,
        ingredient_id INTEGER,
        FOREIGN KEY (recipe_id) REFERENCES recipes (id),
        FOREIGN KEY (ingredient_id) REFERENCES ingredients (id)
    )
    ''')

    # Tarifleri ve malzemeleri veritabanına ekle
    for recipe in RECIPES:
        # Tarifin zaten var olup olmadığını kontrol et
        cursor.execute("SELECT id FROM recipes WHERE name = ?", (recipe["name"],))
        result = cursor.fetchone()
        if result is None:
            cursor.execute("INSERT INTO recipes (name, instructions) VALUES (?, ?)",
                           (recipe["name"], recipe["instructions"]))
            recipe_id = cursor.lastrowid

            for ingredient_name in recipe["ingredients"]:
                # Malzemenin zaten var olup olmadığını kontrol et, yoksa ekle
                cursor.execute("INSERT OR IGNORE INTO ingredients (name) VALUES (?)", (ingredient_name,))
                cursor.execute("SELECT id FROM ingredients WHERE name = ?", (ingredient_name,))
                ingredient_id = cursor.fetchone()[0]

                # Tarif ve malzeme arasındaki ilişkiyi ekle
                cursor.execute("INSERT INTO recipe_ingredients (recipe_id, ingredient_id) VALUES (?, ?)",
                               (recipe_id, ingredient_id))

    conn.commit()
    conn.close()
    print("Veritabanı başarıyla kuruldu ve başlangıç verileri eklendi.")

if __name__ == "__main__":
    setup_database()

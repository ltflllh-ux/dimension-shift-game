import sqlite3
from fastapi import FastAPI, File, UploadFile, HTTPException
from typing import List, Dict, Any
from collections import defaultdict

DATABASE_PATH = 'scantocook/recipes.db'

app = FastAPI()

def get_db_connection():
    """Veritabanına bir bağlantı oluşturur ve satırları sözlük olarak döndürecek şekilde yapılandırır."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def parse_receipt_mock(contents: bytes) -> List[str]:
    """Yapay zeka görme modelinin çıktısını taklit eder."""
    try:
        text = contents.decode("utf-8")
        lines = text.strip().splitlines()
        ingredients = [line.split(' ')[0] for line in lines if line]
        return ingredients
    except Exception:
        return []

def find_matching_recipes(user_ingredients: List[str]) -> List[Dict[str, Any]]:
    """Kullanıcının malzemeleriyle yapılabilecek tarifleri veritabanından verimli bir şekilde bulur."""
    if not user_ingredients:
        return []

    conn = get_db_connection()
    cursor = conn.cursor()

    placeholders = ','.join('?' for _ in user_ingredients)

    # Bu optimize edilmiş sorgu, tarifleri ve malzemelerini tek seferde alır.
    query = f"""
        SELECT
            r.id,
            r.name,
            r.instructions,
            i.name as ingredient_name
        FROM
            recipes r
        JOIN
            recipe_ingredients ri ON r.id = ri.recipe_id
        JOIN
            ingredients i ON ri.ingredient_id = i.id
        WHERE
            r.id IN (
                SELECT r.id
                FROM recipes r
                WHERE (
                    SELECT COUNT(*)
                    FROM recipe_ingredients ri
                    JOIN ingredients i ON ri.ingredient_id = i.id
                    WHERE ri.recipe_id = r.id AND i.name IN ({placeholders})
                ) = (
                    SELECT COUNT(*)
                    FROM recipe_ingredients ri
                    WHERE ri.recipe_id = r.id
                )
            )
    """

    cursor.execute(query, user_ingredients)
    rows = cursor.fetchall()
    conn.close()

    # Sonuçları tariflere göre grupla
    recipes_map = defaultdict(lambda: {"ingredients": []})
    for row in rows:
        recipes_map[row['id']]['name'] = row['name']
        recipes_map[row['id']]['instructions'] = row['instructions']
        recipes_map[row['id']]['ingredients'].append(row['ingredient_name'])

    return list(recipes_map.values())


@app.get("/")
def read_root():
    return {"message": "ScanToCook API'ye Hoş Geldiniz!"}

@app.post("/scan/")
async def create_upload_file(file: UploadFile = File(...)):
    """Bir dosya yüklemesini (fiş) kabul eder, malzemeleri işler ve eşleşen tarifleri döndürür."""
    contents = await file.read()
    extracted_ingredients = parse_receipt_mock(contents)

    # Veritabanı dosyasının var olup olmadığını kontrol et
    try:
        with open(DATABASE_PATH, 'r') as f:
            pass
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Veritabanı bulunamadı. Lütfen önce `database_setup.py` betiğini çalıştırın.")

    matching_recipes = find_matching_recipes(extracted_ingredients)

    return {
        "extracted_ingredients": extracted_ingredients,
        "matching_recipes": matching_recipes
    }

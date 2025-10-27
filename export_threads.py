import requests
import json
import time
import os
from collections import Counter, defaultdict
from dotenv import load_dotenv

load_dotenv("config.env")

API_URL = os.getenv("API_URL")
CREATOR_USER_ID = os.getenv("CREATOR_USER_ID")
BEARER_TOKEN = os.getenv("BEARER_TOKEN")

HEADERS = {
    "accept": "application/json",
    "authorization": f"Bearer {BEARER_TOKEN}"
}

def check_all_same(s):
    return len(set(s)) == 1

def check_palindrome(s):
    return s == s[::-1] and len(s) >= 5

def check_alternating(s):
    if len(s) < 4:
        return False
    unique = set(s)
    if len(unique) != 2:
        return False
    return all(s[i] != s[i+1] for i in range(len(s)-1))

def check_triple_pattern(s):
    if len(s) != 7:
        return False
    if s[0] == s[1] == s[2] and s[4] == s[5] == s[6]:
        if s[0] == s[4] and s[3] != s[0]:
            return True
    return False

def check_mirror_with_center(s):
    if len(s) < 5:
        return False
    if s[0] == s[-1] and s[0] != s[1]:
        middle = s[1:-1]
        if len(set(middle)) == 1 and middle[0] != s[0] and len(middle) >= 3:
            return True
    return False

def check_sequential_ascending(s):
    if len(s) < 4:
        return False
    for i in range(len(s) - 1):
        if int(s[i+1]) != int(s[i]) + 1:
            return False
    return True

def check_sequential_descending(s):
    if len(s) < 4:
        return False
    for i in range(len(s) - 1):
        if int(s[i+1]) != int(s[i]) - 1:
            return False
    return True

def check_mostly_same(s):
    if len(s) < 5:
        return False
    counter = Counter(s)
    most_common = counter.most_common(1)[0]
    if most_common[1] >= len(s) - 1:
        return True
    return False

def check_repeating_pair(s):
    if len(s) < 4 or len(s) % 2 != 0:
        return False
    half = len(s) // 2
    return s[:half] == s[half:] and half >= 2

def check_repeating_triple(s):
    if len(s) < 6 or len(s) % 3 != 0:
        return False
    third = len(s) // 3
    pattern = s[:third]
    return pattern * 3 == s and third >= 2

def analyze_id(thread_id):
    s = str(thread_id)
    patterns = []
    
    if check_all_same(s):
        patterns.append({"name": "ВСЕ_ОДИНАКОВЫЕ", "emoji": "💎", "priority": 10})
    
    if check_sequential_ascending(s):
        patterns.append({"name": "ВОЗРАСТАЮЩАЯ_ПОСЛЕДОВАТЕЛЬНОСТЬ", "emoji": "📈", "priority": 9})
    
    if check_sequential_descending(s):
        patterns.append({"name": "УБЫВАЮЩАЯ_ПОСЛЕДОВАТЕЛЬНОСТЬ", "emoji": "📉", "priority": 9})
    
    if check_palindrome(s):
        patterns.append({"name": "ПАЛИНДРОМ", "emoji": "🔄", "priority": 8})
    
    if check_alternating(s):
        patterns.append({"name": "ЧЕРЕДОВАНИЕ", "emoji": "🔀", "priority": 7})
    
    if check_triple_pattern(s):
        patterns.append({"name": "XXXYXXX", "emoji": "⭐", "priority": 7})
    
    if check_mirror_with_center(s):
        patterns.append({"name": "XYYYYYX", "emoji": "✨", "priority": 7})
    
    if check_repeating_triple(s):
        patterns.append({"name": "ПОВТОР_ТРОЙКИ", "emoji": "🔁", "priority": 6})
    
    if check_repeating_pair(s):
        patterns.append({"name": "ПОВТОР_ПАРЫ", "emoji": "♻️", "priority": 5})
    
    if check_mostly_same(s):
        patterns.append({"name": "ПОЧТИ_ВСЕ_ОДИНАКОВЫЕ", "emoji": "💫", "priority": 4})
    
    return patterns

def fetch_page(page):
    params = {
        "creator_user_id": CREATOR_USER_ID,
        "page": page
    }
    
    try:
        response = requests.get(API_URL, headers=HEADERS, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе страницы {page}: {e}")
        return None

def export_all_threads():
    all_threads = []
    current_page = 1
    total_pages = None
    
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║           🚀 ЭКСПОРТ ДАННЫХ С API                                  ║")
    print("╚════════════════════════════════════════════════════════════════════╝\n")
    
    while True:
        print(f"⏳ Получаем страницу {current_page}...", end=" ")
        
        data = fetch_page(current_page)
        
        if data is None:
            print("❌ Ошибка! Пропускаем страницу.")
            current_page += 1
            continue
        
        if total_pages is None:
            total_pages = data.get("links", {}).get("pages", 0)
            total_threads = data.get("threads_total", 0)
            print(f"\n📊 Всего страниц: {total_pages}, всего тредов: {total_threads}\n")
        
        threads = data.get("threads", [])
        all_threads.extend(threads)
        print(f"✅ Получено {len(threads)} тредов (всего: {len(all_threads)})")
        
        next_page = data.get("links", {}).get("next")
        if not next_page or current_page >= total_pages:
            break
        
        current_page += 1
        time.sleep(0.5)
    
    print(f"\n✨ Собрано {len(all_threads)} тредов\n")
    
    thread_ids = [thread["thread_id"] for thread in all_threads]
    
    with open("thread_ids.json", "w", encoding="utf-8") as f:
        json.dump(thread_ids, f, ensure_ascii=False, indent=2)
    
    print(f"💾 Экспортировано {len(thread_ids)} ID в файл: thread_ids.json\n")
    
    return thread_ids

def analyze_thread_ids(thread_ids):
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║           🔍 АНАЛИЗ ID НА КРУТЫЕ КОМБИНАЦИИ                        ║")
    print("╚════════════════════════════════════════════════════════════════════╝\n")
    
    print(f"📝 Анализируем {len(thread_ids)} ID...\n")
    
    pattern_groups = defaultdict(list)
    pattern_stats = Counter()
    all_cool_ids = []
    
    for thread_id in thread_ids:
        patterns = analyze_id(thread_id)
        if patterns:
            patterns.sort(key=lambda x: x["priority"], reverse=True)
            
            all_cool_ids.append({
                "id": thread_id,
                "patterns": [p["name"] for p in patterns],
                "top_priority": patterns[0]["priority"]
            })
            
            main_pattern = patterns[0]["name"]
            pattern_groups[main_pattern].append({
                "id": thread_id,
                "emoji": patterns[0]["emoji"],
                "all_patterns": [p["name"] for p in patterns]
            })
            
            for pattern in patterns:
                pattern_stats[pattern["name"]] += 1
    
    all_cool_ids.sort(key=lambda x: x["top_priority"], reverse=True)
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║           🌟 НАЙДЕННЫЕ КРУТЫЕ ID                                   ║")
    print("╚════════════════════════════════════════════════════════════════════╝\n")
    
    for pattern_name in sorted(pattern_groups.keys(), key=lambda x: len(pattern_groups[x]), reverse=True):
        ids_list = pattern_groups[pattern_name]
        emoji = ids_list[0]["emoji"] if ids_list else ""
        
        print(f"\n{emoji} {pattern_name} ({len(ids_list)} шт.)")
        print("─" * 70)
        for item in ids_list[:10]:
            extra = f" + {', '.join(item['all_patterns'][1:])}" if len(item['all_patterns']) > 1 else ""
            print(f"  • {item['id']}{extra}")
        
        if len(ids_list) > 10:
            print(f"  ... и еще {len(ids_list) - 10}")
    
    print("\n\n╔════════════════════════════════════════════════════════════════════╗")
    print("║           📊 СТАТИСТИКА                                            ║")
    print("╚════════════════════════════════════════════════════════════════════╝\n")
    
    for pattern, count in pattern_stats.most_common():
        print(f"  {pattern:40s} {count:4d} шт.")
    
    print(f"\n{'─' * 70}")
    print(f"  💎 Всего найдено крутых ID: {len(all_cool_ids)} из {len(thread_ids)}")
    print(f"  📈 Процент крутых ID: {len(all_cool_ids) / len(thread_ids) * 100:.2f}%")
    print(f"{'─' * 70}\n")
    
    output_data = {
        "summary": {
            "total_analyzed": len(thread_ids),
            "cool_ids_found": len(all_cool_ids),
            "percentage": round(len(all_cool_ids) / len(thread_ids) * 100, 2)
        },
        "by_pattern": {
            pattern: [item["id"] for item in ids_list]
            for pattern, ids_list in pattern_groups.items()
        },
        "pattern_statistics": dict(pattern_stats),
        "top_ids": all_cool_ids[:50]
    }
    
    with open("cool_thread_ids.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"💾 Результаты сохранены в cool_thread_ids.json\n")

def main():
    print("\n")
    print("████████████████████████████████████████████████████████████████████")
    print("█                                                                  █")
    print("█           🎯 АНАЛИЗАТОР КРУТЫХ ID ТРЕДОВ                         █")
    print("█                                                                  █")
    print("████████████████████████████████████████████████████████████████████")
    print("\n")
    
    thread_ids = export_all_threads()
    analyze_thread_ids(thread_ids)
    
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║           ✅ ГОТОВО!                                               ║")
    print("╚════════════════════════════════════════════════════════════════════╝\n")

if __name__ == "__main__":
    main()

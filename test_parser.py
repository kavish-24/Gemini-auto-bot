import re

test_response = """नमस्कार पळोवया प्रुडंट खबरो --- Konkani Prime News_100817_segment_001 ---,टॅंकरवाल्यांक ना धरबांद गोंयभरच्या वॉटर टॅंकरांचें ट्रान्स्पोर्ट डिपोर्टमेन्ट करतलो सेफ्टीऑडिट --- Konkani Prime News_100817_segment_002 ---,कोर्टान मागलें केंद्र कर्नाटकाकडच्यान एफिडॅव्हिट. --- Konkani Prime News_100817_segment_003 ---,10 वर्सां उपरांत आयरिश म्हण्टा हरकत ना."""

# Remove header
test_response = re.sub(r'^file_name\s*,\s*matched_text\s*\n?', '', test_response, flags=re.IGNORECASE)

# Pattern
pattern = r'---\s*([^-]+?)\s*---\s*,\s*(.+?)(?=\s*---\s*[^-]+?\s*---|$)'

matches = []
for match in re.finditer(pattern, test_response, re.MULTILINE | re.DOTALL):
    file_name = match.group(1).strip()
    matched_text = match.group(2).strip()
    matches.append((file_name, matched_text))
    print(f"Match {len(matches)}: {file_name}")
    print(f"  Text: {matched_text[:50]}...")
    print()

print(f"\nTotal matches: {len(matches)}")

from flask import Flask, request
import requests
import arabic_reshaper
from bidi.algorithm import get_display

app = Flask(__name__)

# פונקציה לעיבוד טקסט עברי (תיקון כיווניות)
def fix_text_direction(text):
    reshaped_text = arabic_reshaper.reshape(text)
    return get_display(reshaped_text)

# פונקציה לשליפת דף גמרא מ-Sefaria
def get_talmud_page(masechet, daf, amud="a"):
    url = f"https://www.sefaria.org/api/texts/{masechet}.{daf}{amud}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        gemara_text = data.get('he', [])
        if gemara_text:
            return "<br>".join([fix_text_direction(line) for line in gemara_text])
        else:
            return fix_text_direction("הטקסט לא נמצא בדף זה.")
    else:
        return fix_text_direction("שגיאה בשליפת הנתונים מ-Sefaria.")

# פונקציה לשליפת מפרשים (רש"י, תוספות וכו') מ-Sefaria
def get_commentaries(masechet, daf, amud="a"):
    url = f"https://www.sefaria.org/api/texts/{masechet}.{daf}{amud}?commentary=1"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        commentaries = data.get("commentary", [])
        results = []
        for commentary in commentaries:
            title = commentary.get("collectiveTitle", {}).get("he", "מפרש לא ידוע")
            texts = commentary.get("he", [])
            if texts:
                text = texts[0]
            else:
                text = "לא נמצא טקסט"
            results.append(f"<b>{fix_text_direction(title)}</b>: {fix_text_direction(text)}")
        return "<br>".join(results)
    else:
        return fix_text_direction("שגיאה בשליפת המפרשים.")

# נתיב API לקריאה של דף גמרא
@app.route('/talmud', methods=['GET'])
def get_talmud():
    try:
        masechet = request.args.get('masechet')
        daf = request.args.get('daf')
        amud = request.args.get('amud', 'a')
        
        if not masechet or not daf:
            return "נא לספק שם מסכת ודף.", 400
        
        gemara_text = get_talmud_page(masechet, daf, amud)
        commentaries = get_commentaries(masechet, daf, amud)
        
        html_output = f"""
        <html>
        <head>
            <meta charset="utf-8">
            <title>דף גמרא - {fix_text_direction(masechet)} דף {fix_text_direction(daf)} עמוד {fix_text_direction(amud)}</title>
        </head>
        <body dir="rtl" style="text-align: right; font-family: Arial, sans-serif;">
            <h1>גמרא - {fix_text_direction(masechet)} דף {fix_text_direction(daf)} עמוד {fix_text_direction(amud)}</h1>
            <p>{gemara_text}</p>
            <h2>מפרשים</h2>
            <p>{commentaries}</p>
        </body>
        </html>
        """
        
        return html_output
    except Exception as e:
        return f"שגיאה: {e}", 500

# הפעלת השרת
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

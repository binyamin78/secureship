# 🎬 תסריט הצגה ודמו (15 דקות)

**מועד:** יום חמישי 29.10, ‏19:15–19:30 · **מציגים:** בנימין שור, יוסף שוורץ

| זמן | חלק | מציג |
|---|---|---|
| 0:00–1:30 | הבעיה + המשפט האחד | בנימין |
| 1:30–3:00 | ארכיטקטורה: 4 התחנות | בנימין (① ②), יוסף (③ ④) |
| 3:00–7:00 | **דמו A:** המסוע עוצר, ואז עובר | בנימין |
| 7:00–11:00 | **דמו B:** ‏K8s מגן, מגדיל ומתקן | יוסף |
| 11:00–12:30 | ממצאים אמיתיים + לקחים | בנימין |
| 12:30–15:00 | שאלות | שניכם |

---

## ⏰ הכנה: 30 דקות לפני ההצגה

```bash
# 1. Docker Desktop פתוח ורץ (סמל הלוויתן ירוק)
cd ~/Downloads/secureship
./scripts/up.sh                       # 10–15 דקות! עדיף להשאיר את ה-Cluster רץ מהערב הקודם (לא להריץ down.sh)
export KUBECONFIG=$PWD/terraform/kubeconfig
kubectl -n secureship get pods        # 2 Pods במצב Running
```

**לשוניות פתוחות בדפדפן, לפי הסדר:**
1. ‏GitHub, ‏repo → **Actions**
2. ‏GitHub → **Pull requests**: ה-PR של דמו A פתוח מראש וכבר אדום (ראו למטה)
3. האפליקציה: http://localhost:8080
4. ‏Grafana: http://localhost:3000 → Dashboards → **SecureShip - DevBoard**
5. ‏Alertmanager: http://localhost:9093

**שני טרמינלים פתוחים** בתיקיית הפרויקט, עם `export KUBECONFIG=$PWD/terraform/kubeconfig`. הגדילו את הפונט (Ctrl +).

> ⚠️ ‏**ריצת CI לוקחת 2–3 דקות.** לכן פותחים את ה-PR ה"רע" **מראש** (בבוקר), ובהצגה מראים את התוצאה. בזמן ההצגה דוחפים את התיקון, וממשיכים לדבר בזמן שהוא רץ.

### הכנת ה-PR ה"רע" (בבוקר של ההצגה)
```bash
git checkout -b demo/vulnerable-flask
sed -i 's/Flask==3.1.3/Flask==3.1.2/' app/requirements.txt
git commit -am "Downgrade Flask"
git push -u origin demo/vulnerable-flask
gh pr create --title "Downgrade Flask" --body "demo"
git checkout main
```

---

## 🅰️ דמו A: "המסוע עוצר" (בנימין, 4 דקות)

**1. מראים את ה-PR האדום** (לשונית 2)
> "יוסף ביקש להוריד גרסה של Flask, כי משהו לא עבד לו. נראה מה המסוע אומר."

- לוחצים על ה-check שנכשל: **Gate 3 - Dependency scan**.
- מראים בלוג את השורה `flask 3.1.2 PYSEC-2026-2151 3.1.3`.
> "‏pip-audit השווה את הספריות שלנו למאגר החולשות העולמי ומצא חולשה ידועה. שימו לב ששער 4, בניית ה-Image, בכלל לא רץ. **שום דבר לא הגיע ל-Production.**"

**2. תרחיש בונוס: סוד בקוד** (אם יש זמן, אותו רעיון)
```bash
./scripts/demo-leak.sh     # מייצר מפתח AWS מזויף ואקראי, דוחף ל-branch ופותח PR
```
> ‏gitleaks בשער 1 נכשל: "leaks found: 1".
>
> 💡 **סיפור אמיתי להצגה:** בפעם הראשונה שדחפנו את הפרויקט, gitleaks **נכשל עלינו**: הוא מצא מפתח לדוגמה שכתבנו בתוך קובץ התיעוד הזה. הוצאנו את המפתח מהתיעוד, והוא נוצר עכשיו רק בזמן הדמו. את מה שכבר היה בהיסטוריה סימנו כ-false positive ב-`.gitleaksignore`, כי המפתח מזויף. (ראו שאלה 2 ב-qa.md: מפתח **אמיתי** היה צריך להחליף מיד.)

**3. הדרך הנכונה: commit תקין עובר**
מראים בלשונית Actions את הריצה האחרונה על `main`: כל 4 השערים ירוקים, ובסיכום "Image published" עם ה-SHA.
```bash
./scripts/deploy.sh <SHA מהסיכום>     # פורס את ה-Image שעבר את ה-CI
```
- מרעננים את http://localhost:8080. בפינה רואים `version <SHA>`.
> "זה בדיוק ה-commit שעבר את 4 השערים. תמיד אפשר לדעת איזה קוד רץ."

---

## 🅱️ דמו B: ‏"Kubernetes מגן, מגדיל ומתקן" (יוסף, 4 דקות)

**1. עומס, וה-HPA מגדיל** (טרמינל 1)
```bash
python scripts/load_test.py --seconds 150 --threads 30
```
**טרמינל 2:**
```bash
kubectl -n secureship get hpa,pods -w
```
- עוברים ל-**Grafana**. רואים את "Requests / sec" עולה, את "CPU per pod" עולה, ואחרי כ-35 שניות (נמדד בבדיקה) את "Pods running" עולה מ-2 ל-5, ואז ל-6.
- בטרמינל של ה-load test: "pods answering" עולה.
- ב-Alertmanager (לשונית 5) מופיעה ההתראה **DevBoardScaledUp**.
> "אף אחד לא נגע בכלום. ‏K8s ראה שה-CPU עבר 60% והוסיף Pods לבד. כשהעומס ייגמר הוא יקטין חזרה."

**2. ‏K8s דוחה Pod לא בטוח** (בזמן שהעומס רץ)
```bash
kubectl -n secureship run hacker --image=nginx
```
> התוצאה: `Error from server (Forbidden): ... violates PodSecurity "restricted:latest"`.
> "‏nginx הרגיל רץ כ-root. ה-Namespace שלנו מוגדר כ-restricted, אז Kubernetes עצמו מסרב להריץ אותו."

**3. גם אם פרצו, אי אפשר לצאת או לכתוב**
```bash
# ניסיון לכתוב קובץ בתוך ה-Container
kubectl -n secureship exec deploy/devboard -- sh -c 'echo hacked > /app/x'
#   -> Read-only file system

# ניסיון "להוריד כלי תקיפה" מהאינטרנט
kubectl -n secureship exec deploy/devboard -- python -c "import urllib.request; urllib.request.urlopen('http://example.com', timeout=5)"
#   -> Network is unreachable (NetworkPolicy חוסם יציאה)
```

**4. ריפוי עצמי**
```bash
kubectl -n secureship delete pod -l app=devboard --wait=false
kubectl -n secureship get pods -w
```
> "מחקנו את כל ה-Pods. תוך 4 שניות (נמדד בבדיקה) ה-Deployment הקים חדשים."

---

## 🧯 תוכנית גיבוי

| אם... | אז... |
|---|---|
| אין אינטרנט בכיתה | דמו B עובד בלי אינטרנט. בדמו A מראים צילומי מסך מוכנים מראש (`docs/screenshots/`, שם כבר יש צילום של Grafana אחרי scale-up). |
| ה-Cluster לא עולה | **הקלטת וידאו** של כל הדמו, שמוקלטת יום לפני. |
| ה-HPA לא עולה מהר | מגדילים עומס: `--threads 50`. בינתיים מסבירים את הנוסחה (שאלה 7 ב-qa.md). |
| שכחתם `KUBECONFIG` | `export KUBECONFIG=$PWD/terraform/kubeconfig` |

## ✅ אחרי ההצגה
```bash
./scripts/down.sh
```

---

## 📊 תוצאות הדמו האמיתי (25.10.2026)

> כל המספרים במצגת נמדדו בהרצה הזו. הסרטונים שמורים מקומית ב-`presentation/videos/` (לא ב-Git), לגיבוי בלי אינטרנט.

| מה | תוצאה | איפה |
|---|---|---|
| PR #1: הורדה ל-Flask 3.1.2 | שער 3 (pip-audit) נכשל אחרי 21 שניות: `PYSEC-2026-2151`. שער 4 לא רץ. | [PR #1](https://github.com/binyamin78/secureship/pull/1) |
| PR #2: מפתח AWS מזויף | שער 1 (gitleaks) נכשל אחרי 6 שניות: `leaks found: 1` | [PR #2](https://github.com/binyamin78/secureship/pull/2) |
| ריצה על `main` | 4 שערים ירוקים, 54 שניות (12s / 10s / 17s / 32s) | Actions |
| פריסה `deploy.sh b62999f` | 31 שניות, rolling update | `presentation/videos/deploy.webm` |
| Pod של root | `Forbidden`, ‏4 הפרות של Pod Security | `k8s-defense.webm` |
| עומס: 30 threads, ‏150 שניות | CPU שיא 207%, ‏HPA ביקש 6 Pods אחרי 32 שניות, ו-6 רצו אחרי 46 שניות. 2,170 בקשות, 0 שגיאות. ‏`DevBoardScaledUp` פעילה. | `hpa-scaling.webm` |
| מחיקת כל ה-Pods | ראשון מוכן אחרי 3.5 שניות, שניים אחרי 6.6 שניות. בהרצה "קרה" (Image לא על השרת): 46.7 שניות. | `self-heal.webm` |

**באג אמיתי שנמצא בזמן הדמו:** ‏gitleaks סרק את כל ה-branches, אז PR #2 הכשיל גם את `main`. תוקן ב-commit `b62999f` (`--log-opts=HEAD`).

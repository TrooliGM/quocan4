# TÆ° váº¥n hÆ°á»›ng nghiá»‡p 1:1

gitg## Thá»­ ngay trÃªn mÃ¡y

1. Cháº¡y website nhÆ° trÆ°á»›c: `python -m uvicorn app:app --reload` trong thÆ° má»¥c dá»± Ã¡n.
2. Má»Ÿ **http://localhost:8000**. DÃ¹ng cÃ¹ng Ä‘á»‹a chá»‰ nÃ y xuyÃªn suá»‘t khi thá»­ Ä‘Äƒng nháº­p.
3. ÄÄƒng nháº­p email hoáº·c Google. Sau khi Firebase vÃ  backend xÃ¡c thá»±c thÃ nh cÃ´ng, website tá»± má»Ÿ `/ai-career-advisor`.
4. Báº¥m **Báº¯t Ä‘áº§u tÆ° váº¥n vá»›i AI**, hoáº·c chá»n má»™t trong bá»‘n cÃ¢u há»i gá»£i Ã½. CÃ¢u há»i gá»£i Ã½ Ä‘Æ°á»£c Ä‘Æ°a vÃ o Ã´ nháº­p Ä‘á»ƒ báº¡n sá»­a rá»“i gá»­i.
5. GÃµ tin nháº¯n vÃ  báº¥m mÅ©i tÃªn gá»­i hoáº·c Enter. Shift + Enter Ä‘á»ƒ xuá»‘ng dÃ²ng.
6. Chá»n **LÆ°u cuá»™c trÃ² chuyá»‡nâ€¦** trÆ°á»›c khi báº¯t Ä‘áº§u náº¿u muá»‘n xem láº¡i vÃ  ghi nhá»› cho láº§n sau.

MÃ¡y Ä‘ang Ä‘Æ°á»£c báº­t `AI_DEMO_MODE=true` khi triá»ƒn khai tÃ­nh nÄƒng vÃ¬ chÆ°a cÃ³ khÃ³a DeepSeek. Banner vÃ  tá»«ng cÃ¢u tráº£ lá»i Ä‘á»u ghi rÃµ Ä‘Ã¢y lÃ  demo. Demo khÃ´ng phÃ¢n tÃ­ch nÄƒng lá»±c, khÃ´ng tá»± táº¡o há»“ sÆ¡ há»c sinh, khÃ´ng gá»i DeepSeek vÃ  khÃ´ng giáº£ giá»ng Google/Vbee.

Náº¿u Ä‘Ã£ Ä‘Äƒng nháº­p mÃ  Ä‘ang á»Ÿ trang chá»§, báº¥m **TÆ° váº¥n cÃ¹ng AI** trÃªn menu. KhÃ¡ch má»Ÿ trang tÆ° váº¥n Ä‘Æ°á»£c chuyá»ƒn vá» há»™p Ä‘Äƒng nháº­p cÅ©; khÃ´ng cÃ³ há»‡ thá»‘ng tÃ i khoáº£n thá»© hai.

## Báº­t AI tháº­t

Sá»­a `.env` trÃªn mÃ¡y (khÃ´ng gá»­i key vÃ o chat hoáº·c GitHub):

```dotenv
AI_DEMO_MODE=false
DEEPSEEK_API_KEY=YOUR_DEEPSEEK_API_KEY
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-flash
```

Dá»«ng server rá»“i cháº¡y láº¡i sau khi Ä‘á»•i `.env`. Model cÃ³ thá»ƒ thay Ä‘á»•i theo tÃ i khoáº£n DeepSeek. [TÃ i liá»‡u DeepSeek](https://api-docs.deepseek.com/api/create-chat-completion) mÃ´ táº£ endpoint, JSON output vÃ  model ID. KhÃ´ng Ä‘Æ°a khÃ³a vÃ o JavaScript.

Má»—i lÆ°á»£t gá»i DeepSeek Ä‘Ãºng má»™t láº§n qua LangGraph. CÃ¡c node táº£i há»“ sÆ¡, táº£i 20 tin nháº¯n gáº§n nháº¥t vÃ  tÃ³m táº¯t, chuáº©n bá»‹ danh má»¥c nghá», táº¡o tráº£ lá»i vÃ  trÃ­ch xuáº¥t há»“ sÆ¡ trong má»™t JSON, kiá»ƒm tra cáº¥u trÃºc rá»“i lÆ°u cáº·p tin nháº¯n. Danh sÃ¡ch gá»£i Ã½ nghá» Ä‘Æ°á»£c render tá»« JSON riÃªng; backend tá»« chá»‘i danh sÃ¡ch dÆ°á»›i ba nghá» hoáº·c trÃ¹ng tÃªn. Nghá» Ä‘Ã£ gá»£i Ã½ Ä‘Æ°á»£c Ä‘Æ°a láº¡i vÃ o ngá»¯ cáº£nh.

System prompt náº±m trong `advisor/prompt.txt`. Há»“ sÆ¡ lÃ  thÃ´ng tin ngÆ°á»i dÃ¹ng tá»± chia sáº», khÃ´ng pháº£i Ä‘iá»ƒm Ä‘Ã¡nh giÃ¡ nÄƒng lá»±c. Má»™t cÃ¢u há»i tiáº¿p ná»‘i má»—i lÆ°á»£t, khÃ´ng buá»™c chá»n nghá» hoáº·c táº¡o tá»· lá»‡ phÃ¹ há»£p.

## Micro vÃ  giá»ng Ä‘á»c

Hai dá»‹ch vá»¥ nÃ y cÃ³ tÃ i khoáº£n/cáº¥u hÃ¬nh riÃªng vá»›i Firebase Authentication. Báº­t Firebase khÃ´ng tá»± báº­t Google Speech hoáº·c Vbee.

**Google Cloud Speech-to-Text:** báº­t Speech-to-Text API trÃªn Google Cloud project, thiáº¿t láº­p quyá»n sá»­ dá»¥ng dá»‹ch vá»¥ vÃ  thÃ´ng tin xÃ¡c thá»±c server. Äáº·t credentials á»Ÿ ngoÃ i repository:

```dotenv
GOOGLE_CLOUD_PROJECT_ID=project_google_cloud_cá»§a_báº¡n
GOOGLE_APPLICATION_CREDENTIALS=C:/duong-dan-ngoai-du-an/credentials.json
```

ÄÃ¢y lÃ  credentials cho **Google Speech**, khÃ´ng pháº£i yÃªu cáº§u service account Ä‘á»ƒ Ä‘Äƒng nháº­p Firebase. KhÃ´ng commit hoáº·c gá»­i file credentials. MÃ¡y chá»§ dÃ¹ng OAuth scope cloud-platform gá»i [Google recognize REST API](https://docs.cloud.google.com/speech-to-text/docs/reference/rest/v1/speech/recognize).

Khi Ä‘Æ°á»£c cáº¥u hÃ¬nh, báº¥m micro Ä‘á»ƒ cáº¥p quyá»n vÃ  ghi Ã¢m. Browser ghi WAV mono 16-bit, chuyá»ƒn vá» 16 kHz; phÃ¡t hiá»‡n cÃ³ lá»i nÃ³i rá»“i tá»± dá»«ng khi im láº·ng 3 giÃ¢y. LÆ°á»£t ghi tá»‘i Ä‘a khoáº£ng 52 giÃ¢y, khÃ´ng nghe tháº¥y lá»i nÃ³i trong 12 giÃ¢y sáº½ há»§y. CÃ³ nÃºt dá»«ng vÃ  há»§y. VÄƒn báº£n **chá»‰ xuáº¥t hiá»‡n sau khi upload vÃ  nháº­n diá»‡n xong**, khÃ´ng cÃ³ transcript streaming. Báº¡n sá»­a vÄƒn báº£n rá»“i báº¥m Gá»­i. Micro luÃ´n táº¯t khi phÃ¡t Ã¢m thanh AI; khÃ´ng tá»± xin quyá»n micro khi má»Ÿ trang. NgÆ°á»¡ng VAD hiá»‡n lÃ  RMS cá»‘ Ä‘á»‹nh, cáº§n thá»­ trÃªn thiáº¿t bá»‹/mÃ´i trÆ°á»ng á»“n tháº­t.

**Vbee:** táº¡o á»©ng dá»¥ng API vÃ  láº¥y token, App ID, mÃ£ giá»ng tá»« [Vbee](https://api-docs.vbee.vn/tao-ung-dung-app-id-va-token).

```dotenv
VBEE_API_KEY=YOUR_VBEE_API_KEY
VBEE_APP_ID=YOUR_VBEE_APP_ID
VBEE_BASE_URL=https://api.vbee.vn/v1
VBEE_VOICE_ID=voiceCode_duoc_tai_khoan_cua_ban_ho_tro
```

DÃ¹ng [Vbee sync TTS v1](https://api-docs.vbee.vn/vbee-api/text-to-speech/realtime-api): giá»›i háº¡n 300 kÃ½ tá»±/request nÃªn backend bá» dáº¥u Markdown vÃ  chia Ä‘oáº¡n tá»‘i Ä‘a 280 kÃ½ tá»±; browser nháº­n/phÃ¡t tuáº§n tá»±. KhÃ´ng dÃ¹ng batch/webhook, khÃ´ng cáº§n polling tÃ¡c vá»¥ async. Giá»ng Ä‘á»c báº­t máº·c Ä‘á»‹nh khi Ä‘á»§ cáº¥u hÃ¬nh; cÃ³ thá»ƒ táº¯t á»Ÿ header, táº¡m dá»«ng/phÃ¡t tiáº¿p báº±ng thanh audio, dá»«ng hoáº·c nghe láº¡i tá»«ng cÃ¢u. Lá»i chÃ o chá»‰ tá»± phÃ¡t khi báº¥m báº¯t Ä‘áº§u phiÃªn má»›i, khÃ´ng phÃ¡t khi má»Ÿ láº¡i lá»‹ch sá»­. KhÃ´ng tá»± báº­t micro sau giá»ng Ä‘á»c; ngÆ°á»i dÃ¹ng báº¥m micro khi sáºµn sÃ ng. Náº¿u browser cháº·n autoplay, báº¥m **Nghe cÃ¢u tráº£ lá»i**.

Thiáº¿u cáº¥u hÃ¬nh: micro bá»‹ vÃ´ hiá»‡u hÃ³a vÃ  giao diá»‡n thÃ´ng bÃ¡o Ä‘ang chá» thiáº¿t láº­p. Lá»—i giá»ng nÃ³i khÃ´ng xÃ³a cÃ¢u tráº£ lá»i vÄƒn báº£n. Ã‚m thanh xá»­ lÃ½ trong RAM, khÃ´ng ghi vÃ o database cá»§a dá»± Ã¡n; Google/Vbee xá»­ lÃ½ dá»¯ liá»‡u theo chÃ­nh sÃ¡ch tÃ i khoáº£n dá»‹ch vá»¥ cá»§a báº¡n.

## Lá»‹ch sá»­, bá»™ nhá»› vÃ  quyá»n riÃªng tÆ°
- Má»i API `/api/ai/*`, `/api/voice/*` xÃ¡c minh Firebase ID token, tráº£ `Cache-Control: no-store` vÃ  kiá»ƒm tra UID tá»« token.
- KhÃ´ng chá»n lÆ°u: phiÃªn chá»‰ á»Ÿ RAM má»™t tiáº¿n trÃ¬nh, háº¿t háº¡n sau 2 giá» khÃ´ng hoáº¡t Ä‘á»™ng; dá»«ng server lÃ m máº¥t phiÃªn. KhÃ´ng ghi transcript/há»“ sÆ¡ phiÃªn nÃ y xuá»‘ng SQLite.
- Chá»n lÆ°u: SQLite `data/advisor.sqlite3`, cáº¥u hÃ¬nh báº±ng `DATABASE_URL=sqlite:///data/advisor.sqlite3`. CÃ³ lá»‹ch sá»­, há»“ sÆ¡ vÃ  tÃ³m táº¯t; tá»‘i Ä‘a 100 phiÃªn/tÃ i khoáº£n, 250 lÆ°á»£t há»i/phiÃªn.
- SQLite náº±m trÃªn mÃ¡y cháº¡y backend. DÃ¹ng cÃ¹ng Firebase trÃªn hai mÃ¡y khÃ´ng tá»± Ä‘á»“ng bá»™ lá»‹ch sá»­ nÃ y; muá»‘n Ä‘á»“ng bá»™ cáº§n dÃ¹ng chung má»™t backend vÃ  database.
- XÃ³a tá»«ng phiÃªn báº±ng nÃºt Ã— cáº¡nh lá»‹ch sá»­. **Há»“ sÆ¡ hÆ°á»›ng nghiá»‡p cá»§a tÃ´i â†’ XÃ³a toÃ n bá»™ lá»‹ch sá»­ vÃ  ghi nhá»›** xÃ³a dá»¯ liá»‡u tÆ° váº¥n cá»§a tÃ i khoáº£n trÃªn backend hiá»‡n táº¡i; khÃ´ng xÃ³a tÃ i khoáº£n Firebase.
- UUID giá»¯ cho gá»­i láº¡i khÃ´ng táº¡o tin nháº¯n trÃ¹ng trong cÃ¹ng tiáº¿n trÃ¬nh. Báº£n local cháº¡y má»™t worker; trÆ°á»›c khi dÃ¹ng nhiá»u worker/instance cáº§n chuyá»ƒn khÃ³a vÃ  idempotency sang database/kho dÃ¹ng chung.
- Markdown dÃ¹ng Marked vÃ  DOMPurify; khi CDN khÃ´ng táº£i Ä‘Æ°á»£c, hiá»ƒn thá»‹ an toÃ n báº±ng `textContent`. TÃªn, há»“ sÆ¡ vÃ  tháº» nghá» cÅ©ng dÃ¹ng `textContent`.

ChÆ°a triá»ƒn khai Firestore. SQLite hiá»‡n dÃ nh cho báº£n local, khÃ´ng phÃ¹ há»£p á»• Ä‘Ä©a táº¡m cá»§a Vercel. TrÆ°á»›c deployment cáº§n adapter database bá»n vá»¯ng dÃ¹ng chung, giá»›i háº¡n sá»­ dá»¥ng theo tÃ i khoáº£n vÃ  chÃ­nh sÃ¡ch giá»¯ dá»¯ liá»‡u. NgÆ°á»i dÃ¹ng hiá»‡n Ä‘Ã£ hoÃ£n deployment.

## Kiá»ƒm thá»­

```powershell
python -m unittest discover -s tests -v
```

Test HTTP dÃ¹ng mock kiá»ƒm tra payload/pháº£n há»“i DeepSeek/Google/Vbee; khÃ´ng chá»©ng minh tÃ i khoáº£n dá»‹ch vá»¥ tháº­t Ä‘Ã£ hoáº¡t Ä‘á»™ng. Test chá»¯ kÃ½ Firebase dÃ¹ng RSA sinh trong test. Kiá»ƒm thá»­ browser: `python tests/browser_smoke.py` náº¿u mÃ¡y cÃ³ Chrome vÃ  package `websockets`; fixture Firebase chá»‰ trong tiáº¿n trÃ¬nh test loopback, khÃ´ng dÃ¹ng Ä‘á»ƒ cháº¡y á»©ng dá»¥ng tháº­t.

Sau khi cÃ³ khÃ³a tháº­t cáº§n thá»­: Ä‘Äƒng nháº­p email/Google tháº­t, ngá»¯ cáº£nh nhiá»u lÆ°á»£t, gá»£i Ã½ nghá», ghi Ã¢m tiáº¿ng Viá»‡t vÃ  im láº·ng 3 giÃ¢y, sá»­a transcript, nghe lá»i chÃ o/cÃ¢u tráº£ lá»i, pause/replay/mute vÃ  lá»—i dá»‹ch vá»¥.

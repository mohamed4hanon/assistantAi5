import os
import time
import sys
import re
import speech_recognition as sr
from datetime import datetime
from google import genai
from google.genai import types
from gtts import gTTS
import RPi.GPIO as GPIO

# --- 💡 دالة بديلة ومستقلة تماماً لقراءة ملف .env بدون مكتبات خارجية ---
def load_custom_env(filepath=".env"):
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            for line in f:
                if line.strip() and not line.startswith("#"):
                    key, value = line.strip().split("=", 1)
                    os.environ[key.strip()] = value.strip()

# تشغيل الدالة لقراءة الملف المرفق وجلب المفتاح
load_custom_env()
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("[Error]: لم يتم العثور على مفتاح API! تأكد من وجود ملف .env بجانب الكود.")
    sys.exit(1)

# إعداد عميل Gemini
client = genai.Client(api_key=GEMINI_API_KEY)

# --- إعدادات دبابيس GPIO (الزر والـ LED) ---
BUTTON_PIN = 24  # استخدام GPIO 24 (الدبوس الفيزيائي 18) للزر
LED_PIN = 25     # استخدام GPIO 25 (الدبوس الفيزيائي 22) للـ LED

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # إعداد الزر
GPIO.setup(LED_PIN, GPIO.OUT)                             # إعداد الليد كمخرج
GPIO.output(LED_PIN, GPIO.LOW)                            # إطفاء الليد في البداية

current_date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

chat = client.chats.create(
    model="gemini-2.5-flash",
    config=types.GenerateContentConfig(
        system_instruction=(
            f"أنت مساعد ذكي وصوتي يعمل على رازيبري باي. تاريخ ووقت النظام الحالي هو: {current_date_time}. "
            f"أجب باختصار شديد ومناسب جداً للمحادثة الصوتية (سطر أو سطرين كحد أقصى) وبدون أي رموز تعبيرية أو علامات ماركداون كالنجمتين أو جداول."
        )
    )
)

def clean_text_for_speech(text):
    cleaned = re.sub(r'[*_`#\-]', '', text)
    return cleaned.strip()

def speak(text):
    cleaned_text = clean_text_for_speech(text)
    print(f"[Assistant is speaking...]")
    filename = f"response_{int(time.time())}.mp3"
    try:
        GPIO.output(LED_PIN, GPIO.HIGH)  # 💡 تشغيل الليد: المساعد يتحدث الآن
        tts = gTTS(text=cleaned_text, lang='ar', slow=False)
        tts.save(filename)
        os.system(f"mpg123 -q {filename}")
    except Exception as e:
        print(f"[Audio Error]: {e}")
    finally:
        GPIO.output(LED_PIN, GPIO.LOW)   # 💡 إطفاء الليد: انتهى المساعد من التحدث
        time.sleep(0.2)
        if os.path.exists(filename):
            try:
                os.remove(filename)
            except OSError:
                pass

def listen_and_process():
    recognizer = sr.Recognizer()
    recognizer.dynamic_energy_threshold = True
    
    with sr.Microphone() as source:
        print("[System]: أنا أستمع إليك الآن...")
        try:
            audio = recognizer.listen(source, timeout=3, phrase_time_limit=7)
            print("[System]: جاري معالجة وفهم الصوت...")
            user_text = recognizer.recognize_google(audio, language='ar-EG')
            print(f"[أنت]: {user_text}")
            return user_text
        except sr.WaitTimeoutError:
            print("[System]: لم يتم سماع صوت ضمن المهلة.")
            return None
        except sr.UnknownValueError:
            print("[System]: لم يتم فهم الصوت بشكل واضح.")
            return None
        except sr.RequestError:
            speak("عذراً، هناك مشكلة في الاتصال بالإنترنت.")
            return None
        except Exception as e:
            print(f"[Mic Error]: {e}")
            return None

if __name__ == "__main__":
    speak("مرحباً بك. اضغط على الزر في أي وقت للتحدث معي.")
    time.sleep(0.5)
    
    try:
        while True:
            print("\n[الوضع الحالي]: في انتظار الضغط على الزر للتحدث...")
            while GPIO.input(BUTTON_PIN) == GPIO.HIGH:
                time.sleep(0.1)
            
            print("[System]: تم استشعار الضغط على الزر!")
            query = listen_and_process()
            
            if query:
                if any(word in query for word in ["خروج", "إنهاء", "إغلاق", "توقف"]):
                    speak("إلى اللقاء! يومك سعيد.")
                    break
                    
                try:
                    print("[System]: Connecting to Gemini...")
                    GPIO.output(LED_PIN, GPIO.HIGH)  # 💡 تشغيل الليد أثناء انتظار رد الذكاء الاصطناعي
                    response = chat.send_message(query.strip())
                    ai_response = response.text
                    
                    print(f"[AI]: {ai_response}")
                    speak(ai_response)
                except Exception as e:
                    GPIO.output(LED_PIN, GPIO.LOW)   # إطفاء الليد في حال حدوث خطأ بالاتصال
                    print(f"[API Error]: {e}")
                    speak("حدث خطأ أثناء محاولة جلب الإجابة.")
            
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n[System]: تم إغلاق البرنامج يدوياً.")
    finally:
        GPIO.cleanup()  # تنظيف الدبابيس وإطفاء الليد بشكل آمن عند الخروج


import nltk
nltk.download('vader_lexicon')
nltk.download('punkt')

from flask import Flask, request, jsonify, render_template
from nltk.sentiment import SentimentIntensityAnalyzer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

app = Flask(__name__)

data = {
    "departments": {
        "cardiology": "The Cardiology department specializes in heart-related conditions and diseases. Doctors: Dr. Ahmed Hassan, Dr. Fatima Khan, Dr. Usman Malik. Available timings: Monday to Friday, 8 AM to 5 PM. Consultation fees: Rs. 1500-2000.",
        "neurology": "The Neurology department deals with brain and nervous system disorders. Doctors: Dr. Muhammad Ali, Dr. Sara Malik, Dr. Hassan Raza. Available timings: Monday to Saturday, 9 AM to 6 PM. Consultation fees: Rs. 1200-1800.",
        "orthopedics": "The Orthopedics department focuses on bones and joints. Doctors: Dr. Hassan Khan, Dr. Ayesha Ahmed, Dr. Khalid Ibrahim. Available timings: Monday to Friday, 10 AM to 4 PM. Consultation fees: Rs. 1300-1900.",
        "pediatrics": "The Pediatrics department cares for children and provides vaccination services. Doctors: Dr. Bilal Siddiqui, Dr. Hina Rashid, Dr. Zara Hassan. Available timings: Monday to Friday, 8 AM to 3 PM. Consultation fees: Rs. 1000-1500.",
        "general_medicine": "General Medicine department provides primary care and illness management. Doctors: Dr. Imran Sheikh, Dr. Nida Saeed, Dr. Farooq Ahmed. Available timings: Monday to Sunday, 7 AM to 10 PM. Consultation fees: Rs. 800-1200.",
        "dental": "Dental department provides comprehensive dental care and cosmetic dentistry. Doctors: Dr. Kamran Aziz, Dr. Zainab Ali, Dr. Rida Mirza. Available timings: Monday to Friday, 10 AM to 7 PM. Consultation fees: Rs. 1000-1600.",
        "dermatology": "Dermatology department handles skin diseases and allergies. Doctors: Dr. Rashid Malik, Dr. Samina Khan, Dr. Aliza Syed. Available timings: Tuesday to Saturday, 9 AM to 5 PM. Consultation fees: Rs. 1100-1700.",
        "ophthalmology": "Ophthalmology department provides eye care and vision correction. Doctors: Dr. Aamir Khan, Dr. Leila Ahmed, Dr. Nasir Hussain. Available timings: Monday to Friday, 11 AM to 6 PM. Consultation fees: Rs. 1000-1500.",
        "ent": "ENT (Ear, Nose, Throat) department specializes in hearing and respiratory issues. Doctors: Dr. Sohail Ahmed, Dr. Hadia Khan, Dr. Tariq Mehmood. Available timings: Wednesday to Sunday, 10 AM to 5 PM. Consultation fees: Rs. 900-1400.",
        "surgery": "General Surgery department performs surgical procedures. Doctors: Dr. Rizwan Ali, Dr. Munira Hassan, Dr. Asif Khan. Available timings: Monday to Friday, 9 AM to 4 PM. Consultation fees: Rs. 1600-2200."
    },
    "doctors": {
        "dr. ahmed hassan": "Dr. Ahmed Hassan is a senior cardiologist with 18 years of experience. Specializes in interventional cardiology and cardiac imaging. Qualifications: MBBS, MD Cardiology.",
        "dr. fatima khan": "Dr. Fatima Khan is a cardiologist specializing in heart disease prevention and management. Board certified with 12 years experience. Qualifications: MBBS, FCPS Cardiology.",
        "dr. usman malik": "Dr. Usman Malik is a cardiologist with expertise in echocardiography and arrhythmias. 10 years of experience. Qualifications: MBBS, MD Cardiology.",
        "dr. muhammad ali": "Dr. Muhammad Ali is a neurologist focusing on stroke treatment and epilepsy management. Has published over 20 research papers. Qualifications: MBBS, MD Neurology.",
        "dr. sara malik": "Dr. Sara Malik is a neurologist with expertise in migraine disorders and nervous system diseases. Speaks multiple languages. Qualifications: MBBS, FCPS Neurology.",
        "dr. hassan raza": "Dr. Hassan Raza is a neurologist specializing in movement disorders and Parkinson's disease. 8 years experience. Qualifications: MBBS, MD Neurology.",
        "dr. hassan khan": "Dr. Hassan Khan is an orthopedic surgeon specializing in joint replacements and arthroscopic surgery. 15 years of experience. Qualifications: MBBS, FCPS Orthopedics.",
        "dr. ayesha ahmed": "Dr. Ayesha Ahmed is an orthopedic specialist in sports medicine and fracture management. Treats professional athletes. Qualifications: MBBS, FCPS Orthopedics.",
        "dr. khalid ibrahim": "Dr. Khalid Ibrahim is an orthopedic surgeon with expertise in spine surgery and trauma. 12 years experience. Qualifications: MBBS, MD Orthopedics.",
        "dr. bilal siddiqui": "Dr. Bilal Siddiqui is a pediatrician with focus on neonatal care and childhood development. Very patient with children. Qualifications: MBBS, FCPS Pediatrics.",
        "dr. hina rashid": "Dr. Hina Rashid is a pediatrician specializing in immunization and child nutrition. 10 years of practice. Qualifications: MBBS, FCPS Pediatrics.",
        "dr. zara hassan": "Dr. Zara Hassan is a pediatrician with expertise in growth disorders and developmental issues. 7 years experience. Qualifications: MBBS, MD Pediatrics.",
        "dr. imran sheikh": "Dr. Imran Sheikh is a general physician providing comprehensive health checkups and disease management. Qualifications: MBBS, FCPS General Medicine.",
        "dr. nida saeed": "Dr. Nida Saeed is a general physician specializing in chronic disease management and preventive medicine. Qualifications: MBBS, FCPS General Medicine.",
        "dr. farooq ahmed": "Dr. Farooq Ahmed is a general physician with expertise in diabetes and hypertension management. 9 years experience. Qualifications: MBBS, FCPS General Medicine.",
        "dr. kamran aziz": "Dr. Kamran Aziz is a dentist specializing in cosmetic dentistry and teeth whitening. State-of-the-art equipment. Qualifications: BDS, MSc Prosthodontics.",
        "dr. zainab ali": "Dr. Zainab Ali is a dental surgeon specializing in orthodontics and implant dentistry. Qualifications: BDS, MSc Orthodontics.",
        "dr. rida mirza": "Dr. Rida Mirza is a dentist with expertise in root canal treatment and periodontics. 8 years experience. Qualifications: BDS, MSc Endodontics.",
        "dr. rashid malik": "Dr. Rashid Malik is a dermatologist specializing in acne treatment and skin allergies. 12 years experience. Qualifications: MBBS, FCPS Dermatology.",
        "dr. samina khan": "Dr. Samina Khan is a dermatologist specializing in laser therapy and cosmetic skin treatments. Qualifications: MBBS, FCPS Dermatology.",
        "dr. aliza syed": "Dr. Aliza Syed is a dermatologist with expertise in hair loss and skin infections. 9 years experience. Qualifications: MBBS, MD Dermatology.",
        "dr. aamir khan": "Dr. Aamir Khan is an ophthalmologist specializing in cataract surgery and LASIK procedures. Qualifications: MBBS, FCPS Ophthalmology.",
        "dr. leila ahmed": "Dr. Leila Ahmed is an eye specialist focusing on refractive errors and pediatric eye care. Qualifications: MBBS, FCPS Ophthalmology.",
        "dr. nasir hussain": "Dr. Nasir Hussain is an ophthalmologist with expertise in glaucoma and retinal diseases. 11 years experience. Qualifications: MBBS, MD Ophthalmology.",
        "dr. sohail ahmed": "Dr. Sohail Ahmed is an ENT specialist with expertise in hearing aids and voice disorders. 13 years experience. Qualifications: MBBS, FCPS ENT.",
        "dr. hadia khan": "Dr. Hadia Khan is an ENT surgeon specializing in nasal surgery and sinusitis treatment. Qualifications: MBBS, FCPS ENT.",
        "dr. tariq mehmood": "Dr. Tariq Mehmood is an ENT specialist with expertise in balance disorders and vertigo. 10 years experience. Qualifications: MBBS, MD ENT.",
        "dr. rizwan ali": "Dr. Rizwan Ali is a general surgeon specializing in laparoscopic and minimally invasive surgery. 16 years experience. Qualifications: MBBS, FCPS Surgery.",
        "dr. munira hassan": "Dr. Munira Hassan is a general surgeon with expertise in thyroid surgery and trauma care. Qualifications: MBBS, FCPS Surgery.",
        "dr. asif khan": "Dr. Asif Khan is a general surgeon specializing in abdominal surgery and colorectal procedures. 11 years experience. Qualifications: MBBS, MD Surgery."
    },
    "appointments": "To book an appointment, please call our reception at (92) 300-1234567 or use our online booking system at www.medicalcenter.com/appointments. Walk-ins are accepted for urgent cases. Emergency: 24/7 available.",
    "services": "We provide comprehensive healthcare services including: in-house laboratory with 500+ tests, 24-hour pharmacy, ambulance service, emergency care, ICU facilities, online consultation, home collection services, and same-day reports.",
    "timings": "General clinic hours: 8 AM to 10 PM daily except holidays. Emergency services available 24/7. Saturday and Sunday: Limited services available.",
    "location": "Our medical center is located in the heart of Lahore. Easy parking and public transport access available. Near Jilani Park, Mall Road.",
    "facilities": "State-of-the-art facilities including: 24-hour emergency, ICU beds, modern laboratory equipment, digital X-ray, ultrasound, CT scan, MRI, EKG/ECG, blood bank, oxygen supply, air ambulance service.",
    "tests": "Common tests available: Complete Blood Count, Blood Sugar, Thyroid Profile, Lipid Profile, Liver Function, Kidney Function, ECG/EKG, Ultrasound, X-ray, COVID-19 Testing.",
    "fees_info": "Consultation fees vary by department and doctor experience. General consultation: Rs. 800-2000. Lab tests: Rs. 300-5000. Imaging: Rs. 2000-15000. Emergency charges apply separately."
}

qa_pairs = [
    # Departments
    (["cardiology", "heart department", "heart doctor", "tell me about cardiology"], data["departments"]["cardiology"]),
    (["departments", "what departments", "list departments"], "We have 10 departments: Cardiology, Neurology, Orthopedics, Pediatrics, General Medicine, Dental, Dermatology, Ophthalmology, ENT, and Surgery."),
    (["cardiologist", "cardiologists", "heart specialist", "heart doctor"], "Our cardiologists are Dr. Ahmed Hassan, Dr. Fatima Khan, and Dr. Usman Malik."),

    (["neurology", "brain doctor", "nervous system", "tell me about neurology"], data["departments"]["neurology"]),
    (["neurologist", "neurologists", "brain specialist"], "Our neurologists are Dr. Muhammad Ali, Dr. Sara Malik, and Dr. Hassan Raza."),

    (["orthopedics", "orthopedic", "bone doctor", "joints"], data["departments"]["orthopedics"]),
    (["orthopedic doctors", "orthopedic specialist"], "Our orthopedic doctors are Dr. Hassan Khan, Dr. Ayesha Ahmed, and Dr. Khalid Ibrahim."),

    (["pediatrics", "children doctor", "child specialist"], data["departments"]["pediatrics"]),
    (["pediatricians", "children doctors"], "Our pediatricians are Dr. Bilal Siddiqui, Dr. Hina Rashid, and Dr. Zara Hassan."),

    (["general medicine", "general doctor", "general physician"], data["departments"]["general_medicine"]),
    (["general physicians", "general doctors"], "Our general physicians are Dr. Imran Sheikh, Dr. Nida Saeed, and Dr. Farooq Ahmed."),

    (["dental", "dentist", "teeth", "dental care"], data["departments"]["dental"]),
    (["dentists", "dental doctors"], "Our dentists are Dr. Kamran Aziz, Dr. Zainab Ali, and Dr. Rida Mirza."),

    (["dermatology", "skin doctor", "skin disease"], data["departments"]["dermatology"]),
    (["dermatologists", "skin specialist"], "Our dermatologists are Dr. Rashid Malik, Dr. Samina Khan, and Dr. Aliza Syed."),

    (["ophthalmology", "eye doctor", "eye care", "vision"], data["departments"]["ophthalmology"]),
    (["eye doctors", "eye specialist"], "Our eye doctors are Dr. Aamir Khan, Dr. Leila Ahmed, and Dr. Nasir Hussain."),

    (["ent", "ear nose throat", "hearing", "respiratory"], data["departments"]["ent"]),

    (["surgery", "surgeon", "surgical"], data["departments"]["surgery"]),

    # Appointment / Services
    (["book appointment", "appointment", "schedule", "booking"], data["appointments"]),
    (["contact hospital", "contact", "phone number"], data["appointments"]),

    (["services", "what services", "what facilities"], data["services"]),

    (["timing", "clinic timing", "working hours", "hours", "open", "when open"], data["timings"]),
    (["location", "address", "where located", "directions"], data["location"]),

    # Emergency
    (["emergency", "urgent", "emergency services"], "Yes, we have 24/7 emergency services available. Call us immediately at (92) 300-1234567."),
    (["online consultation", "telemedicine", "online doctor"], "Yes, we provide online consultation services. Call reception for more details."),

    # Doctors - Cardiology
    (["ahmed hassan", "dr. ahmed hassan", "Ahmed Hassan"], data["doctors"]["dr. ahmed hassan"]),
    (["fatima khan", "dr. fatima khan", "Fatima Khan"], data["doctors"]["dr. fatima khan"]),
    (["usman malik", "dr. usman malik", "Usman Malik"], data["doctors"]["dr. usman malik"]),

    # Doctors - Neurology
    (["muhammad ali", "dr. muhammad ali", "Muhammad Ali"], data["doctors"]["dr. muhammad ali"]),
    (["sara malik", "dr. sara malik", "Sara Malik"], data["doctors"]["dr. sara malik"]),
    (["hassan raza", "dr. hassan raza", "Hassan Raza"], data["doctors"]["dr. hassan raza"]),

    # Doctors - Orthopedics
    (["hassan khan", "dr. hassan khan", "Hassan Khan"], data["doctors"]["dr. hassan khan"]),
    (["ayesha ahmed", "dr. ayesha ahmed", "Ayesha Ahmed"], data["doctors"]["dr. ayesha ahmed"]),
    (["khalid ibrahim", "dr. khalid ibrahim", "Khalid Ibrahim"], data["doctors"]["dr. khalid ibrahim"]),

    # Doctors - Pediatrics
    (["bilal siddiqui", "dr. bilal siddiqui", "Bilal Siddiqui"], data["doctors"]["dr. bilal siddiqui"]),
    (["hina rashid", "dr. hina rashid", "Hina Rashid"], data["doctors"]["dr. hina rashid"]),
    (["zara hassan", "dr. zara hassan", "Zara Hassan"], data["doctors"]["dr. zara hassan"]),

    # Doctors - General Medicine
    (["imran sheikh", "dr. imran sheikh", "Imran Sheikh"], data["doctors"]["dr. imran sheikh"]),
    (["nida saeed", "dr. nida saeed", "Nida Saeed"], data["doctors"]["dr. nida saeed"]),
    (["farooq ahmed", "dr. farooq ahmed", "Farooq Ahmed"], data["doctors"]["dr. farooq ahmed"]),

    # Doctors - Dental
    (["kamran aziz", "dr. kamran aziz", "Kamran Aziz"], data["doctors"]["dr. kamran aziz"]),
    (["zainab ali", "dr. zainab ali", "Zainab Ali"], data["doctors"]["dr. zainab ali"]),
    (["rida mirza", "dr. rida mirza", "Rida Mirza"], data["doctors"]["dr. rida mirza"]),

    # Doctors - Dermatology
    (["rashid malik", "dr. rashid malik", "Rashid Malik"], data["doctors"]["dr. rashid malik"]),
    (["samina khan", "dr. samina khan", "Samina Khan"], data["doctors"]["dr. samina khan"]),
    (["aliza syed", "dr. aliza syed", "Aliza Syed"], data["doctors"]["dr. aliza syed"]),

    # Doctors - Ophthalmology
    (["aamir khan", "dr. aamir khan", "Aamir Khan"], data["doctors"]["dr. aamir khan"]),
    (["leila ahmed", "dr. leila ahmed", "Leila Ahmed"], data["doctors"]["dr. leila ahmed"]),
    (["nasir hussain", "dr. nasir hussain", "Nasir Hussain"], data["doctors"]["dr. nasir hussain"]),

    # Doctors - ENT
    (["sohail ahmed", "dr. sohail ahmed", "Sohail Ahmed"], data["doctors"]["dr. sohail ahmed"]),
    (["hadia khan", "dr. hadia khan", "Hadia Khan"], data["doctors"]["dr. hadia khan"]),
    (["tariq mehmood", "dr. tariq mehmood", "Tariq Mehmood"], data["doctors"]["dr. tariq mehmood"]),

    # Doctors - Surgery
    (["rizwan ali", "dr. rizwan ali", "Rizwan Ali"], data["doctors"]["dr. rizwan ali"]),
    (["munira hassan", "dr. munira hassan", "Munira Hassan"], data["doctors"]["dr. munira hassan"]),
    (["asif khan", "dr. asif khan", "Asif Khan"], data["doctors"]["dr. asif khan"]),

    # Facilities / Tests / Fees
    (["facilities", "equipment", "infrastructure"], data["facilities"]),
    (["icu", "intensive care"], "Yes, we have ICU facilities with skilled staff and modern equipment."),
    (["tests", "lab tests", "laboratory"], data["tests"]),
    (["fees", "cost", "consultation fees", "charges"], data["fees_info"]),

    # Equipment
    (["x-ray", "xray", "radiography"], "Yes, we have digital X-ray facilities with latest technology."),
    (["ct scan", "computed tomography"], "Yes, we have CT scan facility available."),
    (["mri", "magnetic resonance"], "Yes, we have MRI facility for detailed imaging."),
    (["ultrasound", "sonography", "ultrasonic"], "Yes, we have ultrasound facilities for diagnostic imaging."),

    # Services extra
    (["air ambulance", "ambulance", "medical transport"], "Yes, we provide air ambulance service for emergency transfers."),
    (["blood bank", "blood donation", "blood supply"], "Yes, we have a blood bank with various blood groups available."),
    (["insurance", "health insurance"], "Yes, we accept most major insurance companies. Contact reception."),
    (["payment", "payment methods", "how to pay"], "We accept cash, credit cards, debit cards, and online transfers."),

    (["home collection", "sample collection", "home visit"], "Yes, we provide home collection service for laboratory tests."),
    (["same day report", "fast report", "quick result"], "Yes, we provide same-day reports for most laboratory tests."),

    # Location / hospital info
    (["nearest hospital", "where is hospital", "location"], "We are located in Lahore near Jilani Park. Call for details."),
    (["visiting hours", "open hours", "when open"], "We are open 8 AM to 10 PM daily. Emergency 24/7."),
]

all_questions = []
answers_list = []

for questions, answer in qa_pairs:
    if isinstance(questions, list):
        all_questions.extend(questions)
        answers_list.extend([answer] * len(questions))
    else:
        all_questions.append(questions)
        answers_list.append(answer)

vectorizer = TfidfVectorizer(analyzer='char', ngram_range=(2, 3), lowercase=True)
tfidf_matrix = vectorizer.fit_transform(all_questions)
sia = SentimentIntensityAnalyzer()


def find_best_answer(user_question):
    """Find the best matching answer using TF-IDF semantic similarity"""
    try:
        
        user_tfidf = vectorizer.transform([user_question])
        
        similarities = cosine_similarity(user_tfidf, tfidf_matrix)[0]
        
        best_match_idx = np.argmax(similarities)
        best_similarity = similarities[best_match_idx]
        
        if best_similarity > 0.2:
            return answers_list[best_match_idx]
        else:
            return None
    except:
        return None


def analyze_sentiment(text):
    sentiment_score = sia.polarity_scores(text)

    if sentiment_score['compound'] >= 0.05:
        return "Positive Sentence"
    elif sentiment_score['compound'] <= -0.05:
        return "Negative Sentence"
    else:
        return "Neutral Sentence"


@app.route('/')
def home():
    return render_template('index.html')


@app.route("/ask", methods=["POST"])
def ask():
    user_message = request.json.get("question")
    
    response = find_best_answer(user_message)

    if response:
        return jsonify({
            "answer": response
        })
    else:
        return jsonify({
            "answer": "I'm sorry, I don't have information on that. Please contact our reception for more details."
        })


@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message")

    response = find_best_answer(user_message)

    if response:
        return jsonify({
            "reply": response
        })
    else:
        return jsonify({
            "reply": "Sorry, I don't understand that question."
        })

@app.route("/sentiment", methods=["POST"])
def sentiment():
    text = request.json.get("text")

    result = analyze_sentiment(text)

    return jsonify({
        "sentiment": result
    })


if __name__ == "__main__":
    app.run(debug=True)

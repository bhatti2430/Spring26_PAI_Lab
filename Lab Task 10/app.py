import nltk
nltk.download('vader_lexicon')
nltk.download('punkt')

from flask import Flask, request, jsonify, render_template
from nltk.chat.util import Chat
from nltk.sentiment import SentimentIntensityAnalyzer

app = Flask(__name__)

# Sample data for the medical center
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

# Predefined questions and answers
qa_pairs = [
    ("cardiology", data["departments"]["cardiology"]),
    ("Tell me about cardiology", data["departments"]["cardiology"]),
    ("What departments do you have?", "We have 8 departments: Cardiology, Neurology, Orthopedics, Pediatrics, General Medicine, Dental, Dermatology, and Ophthalmology."),
    ("cardiologists", "Our cardiologists are Dr. Ahmed Hassan and Dr. Fatima Khan."),
    ("Who are the cardiologists?", "Our cardiologists are Dr. Ahmed Hassan and Dr. Fatima Khan."),
    ("neurology", data["departments"]["neurology"]),
    ("What is neurology?", data["departments"]["neurology"]),
    ("Who are the neurologists?", "Our neurologists are Dr. Muhammad Ali and Dr. Sara Malik."),
    ("Tell me about orthopedics", data["departments"]["orthopedics"]),
    ("Who are the orthopedic doctors?", "Our orthopedic doctors are Dr. Hassan Khan and Dr. Ayesha Ahmed."),
    ("What is pediatrics?", data["departments"]["pediatrics"]),
    ("Who are the pediatricians?", "Our pediatricians are Dr. Bilal Siddiqui and Dr. Hina Rashid."),
    ("Tell me about general medicine", data["departments"]["general_medicine"]),
    ("Who are general physicians?", "Our general physicians are Dr. Imran Sheikh and Dr. Nida Saeed."),
    ("Tell me about dental", data["departments"]["dental"]),
    ("Who are the dentists?", "Our dentists are Dr. Kamran Aziz and Dr. Zainab Ali."),
    ("Tell me about dermatology", data["departments"]["dermatology"]),
    ("Who are the dermatologists?", "Our dermatologists are Dr. Rashid Malik and Dr. Samina Khan."),
    ("Tell me about ophthalmology", data["departments"]["ophthalmology"]),
    ("Who are the eye doctors?", "Our eye doctors are Dr. Aamir Khan and Dr. Leila Ahmed."),
    ("How to book an appointment?", data["appointments"]),
    ("How can I schedule a visit?", data["appointments"]),
    ("How do I contact the hospital?", data["appointments"]),
    ("What are your services?", data["services"]),
    ("What services do you provide?", data["services"]),
    ("What is your clinic timing?", data["timings"]),
    ("What are your working hours?", data["timings"]),
    ("Where is your hospital located?", data["location"]),
    ("What is your address?", data["location"]),
    ("Do you have emergency services?", "Yes, we have 24/7 emergency services available. Call us immediately at (92) 300-1234567."),
    ("Do you have online consultation?", "Yes, we provide online consultation services. Call our reception for more details."),
    ("ahmed hassan", data["doctors"]["dr. ahmed hassan"]),
    ("dr. ahmed hassan", data["doctors"]["dr. ahmed hassan"]),
    ("Tell me about Dr. Ahmed Hassan", data["doctors"]["dr. ahmed hassan"]),
    ("fatima khan", data["doctors"]["dr. fatima khan"]),
    ("dr. fatima khan", data["doctors"]["dr. fatima khan"]),
    ("Tell me about Dr. Fatima Khan", data["doctors"]["dr. fatima khan"]),
    ("muhammad ali", data["doctors"]["dr. muhammad ali"]),
    ("dr. muhammad ali", data["doctors"]["dr. muhammad ali"]),
    ("Tell me about Dr. Muhammad Ali", data["doctors"]["dr. muhammad ali"]),
    ("sara malik", data["doctors"]["dr. sara malik"]),
    ("dr. sara malik", data["doctors"]["dr. sara malik"]),
    ("Tell me about Dr. Sara Malik", data["doctors"]["dr. sara malik"]),
    ("Tell me about Dr. Hassan Khan", data["doctors"]["dr. hassan khan"]),
    ("Tell me about Dr. Ayesha Ahmed", data["doctors"]["dr. ayesha ahmed"]),
    ("Tell me about Dr. Bilal Siddiqui", data["doctors"]["dr. bilal siddiqui"]),
    ("Tell me about Dr. Hina Rashid", data["doctors"]["dr. hina rashid"]),
    ("Tell me about Dr. Imran Sheikh", data["doctors"]["dr. imran sheikh"]),
    ("Tell me about Dr. Nida Saeed", data["doctors"]["dr. nida saeed"]),
    ("Tell me about Dr. Kamran Aziz", data["doctors"]["dr. kamran aziz"]),
    ("Tell me about Dr. Zainab Ali", data["doctors"]["dr. zainab ali"]),
    ("Tell me about Dr. Rashid Malik", data["doctors"]["dr. rashid malik"]),
    ("Tell me about Dr. Samina Khan", data["doctors"]["dr. samina khan"]),
    ("Tell me about Dr. Aamir Khan", data["doctors"]["dr. aamir khan"]),
    ("Tell me about Dr. Leila Ahmed", data["doctors"]["dr. leila ahmed"]),
    ("Do you have pharmacy?", "Yes, we have an in-house pharmacy for your convenience."),
    ("Do you have laboratory?", "Yes, we have a modern in-house laboratory for quick test results."),
    ("Do you have ambulance service?", "Yes, we provide 24/7 ambulance service for emergencies."),
    ("What payment methods do you accept?", "We accept cash, credit cards, debit cards, and online transfers."),
    ("Do you provide home service?", "Yes, we provide home visit services. Call reception for booking."),
    ("ent", "ENT (Ear, Nose, Throat) department specializes in hearing and respiratory issues. Doctors: Dr. Sohail Ahmed, Dr. Hadia Khan. Available timings: Wednesday to Sunday, 10 AM to 5 PM."),
    ("ear nose throat", "ENT (Ear, Nose, Throat) department specializes in hearing and respiratory issues."),
    ("surgery", "General Surgery department performs surgical procedures. Doctors: Dr. Rizwan Ali, Dr. Munira Hassan. Available timings: Monday to Friday, 9 AM to 4 PM."),
    ("general surgery", data["departments"]["surgery"]),
    ("usman malik", data["doctors"]["dr. usman malik"]),
    ("dr. usman malik", data["doctors"]["dr. usman malik"]),
    ("hassan raza", data["doctors"]["dr. hassan raza"]),
    ("dr. hassan raza", data["doctors"]["dr. hassan raza"]),
    ("khalid ibrahim", data["doctors"]["dr. khalid ibrahim"]),
    ("dr. khalid ibrahim", data["doctors"]["dr. khalid ibrahim"]),
    ("zara hassan", data["doctors"]["dr. zara hassan"]),
    ("dr. zara hassan", data["doctors"]["dr. zara hassan"]),
    ("farooq ahmed", data["doctors"]["dr. farooq ahmed"]),
    ("dr. farooq ahmed", data["doctors"]["dr. farooq ahmed"]),
    ("rida mirza", data["doctors"]["dr. rida mirza"]),
    ("dr. rida mirza", data["doctors"]["dr. rida mirza"]),
    ("aliza syed", data["doctors"]["dr. aliza syed"]),
    ("dr. aliza syed", data["doctors"]["dr. aliza syed"]),
    ("nasir hussain", data["doctors"]["dr. nasir hussain"]),
    ("dr. nasir hussain", data["doctors"]["dr. nasir hussain"]),
    ("sohail ahmed", data["doctors"]["dr. sohail ahmed"]),
    ("dr. sohail ahmed", data["doctors"]["dr. sohail ahmed"]),
    ("hadia khan", data["doctors"]["dr. hadia khan"]),
    ("dr. hadia khan", data["doctors"]["dr. hadia khan"]),
    ("tariq mehmood", data["doctors"]["dr. tariq mehmood"]),
    ("dr. tariq mehmood", data["doctors"]["dr. tariq mehmood"]),
    ("rizwan ali", data["doctors"]["dr. rizwan ali"]),
    ("dr. rizwan ali", data["doctors"]["dr. rizwan ali"]),
    ("munira hassan", data["doctors"]["dr. munira hassan"]),
    ("dr. munira hassan", data["doctors"]["dr. munira hassan"]),
    ("asif khan", data["doctors"]["dr. asif khan"]),
    ("dr. asif khan", data["doctors"]["dr. asif khan"]),
    ("What facilities do you have?", data["facilities"]),
    ("What are your facilities?", data["facilities"]),
    ("Do you have ICU?", "Yes, we have ICU facilities with skilled staff and modern equipment."),
    ("Do you have laboratory?", "Yes, we have a modern in-house laboratory with 500+ tests available."),
    ("What tests are available?", data["tests"]),
    ("What are your fees?", data["fees_info"]),
    ("consultation fees", data["fees_info"]),
    ("Cost of consultation", data["fees_info"]),
    ("lab test cost", data["fees_info"]),
    ("How much does consultation cost?", data["fees_info"]),
    ("Do you have X-ray?", "Yes, we have digital X-ray facilities with latest technology."),
    ("Do you have CT scan?", "Yes, we have CT scan facility available."),
    ("Do you have MRI?", "Yes, we have MRI facility for detailed imaging."),
    ("Do you have ultrasound?", "Yes, we have ultrasound facilities for diagnostic imaging."),
    ("Do you provide air ambulance?", "Yes, we provide air ambulance service for emergency transfers."),
    ("air ambulance service", "Yes, we provide air ambulance service for emergency transfers and critical care transport."),
    ("Do you have blood bank?", "Yes, we have blood bank with various blood groups available."),
    ("blood bank", "Yes, we have a blood bank with various blood groups and blood products available."),
    ("Do you accept insurance?", "Yes, we accept most insurance companies. Please call for details."),
    ("insurance", "Yes, we accept most major insurance companies. Contact reception for more information."),
    ("What are your payment methods?", "We accept cash, credit cards, debit cards, and online transfers. Check facility also available."),
    ("payment methods", "We accept cash, credit cards, debit cards, and online transfers."),
    ("How do I get a home sample collection?", "Call our reception at (92) 300-1234567 to schedule home collection service."),
    ("home collection", "Yes, we provide home collection service for laboratory tests. Call reception to schedule."),
    ("same day report", "Yes, we provide same-day reports for most common tests. Ask at reception for details."),
    ("Do you have same day reports?", "Yes, we provide same-day reports for most laboratory tests."),
    ("Tell me about Dr. Usman Malik", data["doctors"]["dr. usman malik"]),
    ("Tell me about Dr. Hassan Raza", data["doctors"]["dr. hassan raza"]),
    ("Tell me about Dr. Khalid Ibrahim", data["doctors"]["dr. khalid ibrahim"]),
    ("Tell me about Dr. Zara Hassan", data["doctors"]["dr. zara hassan"]),
    ("Tell me about Dr. Farooq Ahmed", data["doctors"]["dr. farooq ahmed"]),
    ("Tell me about Dr. Rida Mirza", data["doctors"]["dr. rida mirza"]),
    ("Tell me about Dr. Aliza Syed", data["doctors"]["dr. aliza syed"]),
    ("Tell me about Dr. Nasir Hussain", data["doctors"]["dr. nasir hussain"]),
    ("Tell me about Dr. Sohail Ahmed", data["doctors"]["dr. sohail ahmed"]),
    ("Tell me about Dr. Hadia Khan", data["doctors"]["dr. hadia khan"]),
    ("Tell me about Dr. Tariq Mehmood", data["doctors"]["dr. tariq mehmood"]),
    ("Tell me about Dr. Rizwan Ali", data["doctors"]["dr. rizwan ali"]),
    ("Tell me about Dr. Munira Hassan", data["doctors"]["dr. munira hassan"]),
    ("Tell me about Dr. Asif Khan", data["doctors"]["dr. asif khan"]),
    ("What are the least expensive doctor?", "General physicians have lowest fees starting from Rs. 800. Emergency charges may apply."),
    ("nearest hospital", "We are located in the heart of Lahore near Jilani Park. Call for location details."),
    ("visiting hours", "We are open from 8 AM to 10 PM daily. Emergency available 24/7.")
 ]

chat_pairs = [(pattern, [reply]) for pattern, reply in qa_pairs]
chatbot = Chat(chat_pairs)
sia = SentimentIntensityAnalyzer()


def analyze_sentiment(text):
    sentiment_score = sia.polarity_scores(text)

    if sentiment_score['compound'] >= 0.05:
        return "Positive Sentence"
    elif sentiment_score['compound'] <= -0.05:
        return "Negative Sentence"
    else:
        return "Neutral Sentence"


# Homepage
@app.route('/')
def home():
    return render_template('index.html')


# Chatbot API
@app.route("/ask", methods=["POST"])
def ask():
    user_message = request.json.get("question")

    response = chatbot.respond(user_message)

    if response:
        return jsonify({
            "answer": response
        })
    else:
        return jsonify({
            "answer": "I'm sorry, I don't have information on that. Please contact our reception for more details."
        })


# Chat Endpoint (Alternative)
@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message")

    response = chatbot.respond(user_message)

    if response:
        return jsonify({
            "reply": response
        })
    else:
        return jsonify({
            "reply": "Sorry, I don't understand that question."
        })


# Sentiment API
@app.route("/sentiment", methods=["POST"])
def sentiment():
    text = request.json.get("text")

    result = analyze_sentiment(text)

    return jsonify({
        "sentiment": result
    })


if __name__ == "__main__":
    app.run(debug=True)

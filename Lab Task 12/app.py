import os
import pandas as pd
import numpy as np
import re
from flask import Flask, request, jsonify, render_template
from sentence_transformers import SentenceTransformer
import faiss

app = Flask(__name__)


CSV_FILE = 'qna_dataset.csv'
SIMILARITY_THRESHOLD = 0.1  

def preprocess_text(text):
    
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

print("\n" + "="*60)
print("Loading Sentence Transformer model (MiniLM)...")
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
print("Model loaded successfully")

print("Loading QnA dataset from CSV...")
df = pd.read_csv(CSV_FILE)
questions = df['question'].tolist()
answers = df['answer'].tolist()
print(f"Dataset loaded: {len(questions)} Q&A pairs")

print("Creating embeddings for all questions...")
embeddings = model.encode(questions, convert_to_numpy=True)
print(f"Embeddings created")

dimension = embeddings.shape[1]
faiss_index = faiss.IndexFlatL2(dimension)
faiss_index.add(embeddings.astype(np.float32))

print(f"FAISS index created")
print(f"  - Embedding dimension: {dimension}")
print(f"  - Total indexed questions: {len(questions)}")
print("="*60 + "\n")

def find_best_answer(user_question, top_k=3):
   
    query_embedding = model.encode([user_question], convert_to_numpy=True)
    
    distances, indices = faiss_index.search(query_embedding.astype(np.float32), top_k)
    
    results = []
    for idx, distance in zip(indices[0], distances[0]):
        similarity = np.exp(-distance)
        
        if similarity > SIMILARITY_THRESHOLD:
            results.append({
                'answer': answers[idx],
                'original_question': questions[idx],
                'similarity': float(similarity),
                'distance': float(distance)
            })
    
    return results


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


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/ask', methods=['POST'])
def ask():
    data = request.json
    user_question = data.get('question', '').strip()
    
    if not user_question:
        return jsonify({'error': 'Please provide a question'}), 400
    
  
    results = find_best_answer(user_question, top_k=5)
    
    if not results:
        return jsonify({
            'question': user_question,
            'answer': "I'm sorry, I couldn't find relevant information. Please try asking another question about our medical services.",
            'similarity': 0,
            'found': False
        })
    
    best_result = results[0]
    return jsonify({
        'question': user_question,
        'answer': best_result['answer'],
        'original_question': best_result['original_question'],
        'similarity': round(best_result['similarity'] * 100, 2),
        'found': True,
        'all_results': results
    })


@app.route('/stats', methods=['GET'])
def stats():
    """Return dataset and model statistics"""
    return jsonify({
        'total_questions': len(questions),
        'embedding_dimension': dimension,
        'model': 'all-MiniLM-L6-v2',
        'similarity_threshold': SIMILARITY_THRESHOLD,
        'index_type': 'FAISS (L2 distance)',
        'csv_file': CSV_FILE
    })


if __name__ == '__main__':
    print("\n" + "="*60)
    print("Medical Center QnA Bot Server Starting...")
    print("="*60)
    print(f"Dataset: {len(questions)} Q&A pairs loaded from {CSV_FILE}")
    print(f"Model: sentence-transformers/all-MiniLM-L6-v2")
    print(f"Embeddings: {dimension}-dimensional vectors")
    print(f"Search: FAISS with L2 distance")
    print("="*60)
    print("Open your browser: http://127.0.0.1:5000/")
    print("="*60 + "\n")
    
    app.run(debug=True, host='127.0.0.1', port=5000)

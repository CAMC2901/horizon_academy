"""
Static Responses Engine for Horizon Academy.
Intercepts common queries, greetings, identity questions, doubts, gibberish/nonsense,
and frequent requests to return instant answers with ZERO token consumption and zero LLM latency.
"""

import re
import os

ESCALATION_FORM_URL = os.getenv("ESCALATION_FORM_URL", "https://docs.google.com/forms/d/e/1FAIpQLSdAyhhqdotfhe9bwKaCC0faNaArmJLSjQOmuD9feRl0pEd95A/viewform")

GIBBERISH_RESPONSE = "No he podido entender tu mensaje. 🧐 Por favor, escribe tu consulta de forma clara sobre nuestros cursos de idiomas (Inglés, Francés, Alemán, Italiano), precios, horarios o matrículas."

STATIC_RULES = [
    # 1. SPECIFIC INTENT: PRICES, COSTS & TUITION FEES
    {
        "keywords": ["precio", "precios", "cuanto cuesta", "cuanto vale", "costo", "costos", "tarifas", "cuanto es la matricula", "valor del modulo", "mensualidad", "cuanto vale el modulo", "valor de la clase"],
        "response": "Nuestras tarifas en **Horizon Academy** son:\n- **Matrícula inicial**: $60.000 COP (pago único por programa).\n- **Módulo bimestral (2 meses)**: $480.000 COP.\n- **Material digital y plataforma**: ¡100% Incluido sin costo adicional!\n- **Descuentos**: 5% por pronto pago o 10% por paquete trimodular (3 módulos por adelantado)."
    },
    # 2. SPECIFIC INTENT: DISCOUNTS & SCHOLARSHIPS
    {
        "keywords": ["descuento", "descuentos", "promocion", "promociones", "oferta", "rebaja", "beca", "becas", "trimodular", "pronto pago"],
        "response": "En **Horizon Academy** contamos con excelentes facilidades y promociones:\n- **10% de descuento**: Al cancelar el Paquete Trimodular (3 módulos por adelantado).\n- **5% de descuento**: Por pronto pago cancelando 5 días antes del inicio de clases.\n- **Planes Corporativos**: Descuentos especiales para grupos de empresas."
    },
    # 3. SPECIFIC INTENT: PAYMENT METHODS
    {
        "keywords": ["metodo de pago", "medios de pago", "forma de pago", "como pagar", "nequi", "daviplata", "pse", "tarjeta de credito", "tarjeta de debito", "transferencia", "bancolombia", "cuotas"],
        "response": "Aceptamos múltiples medios de pago seguros:\n- **Online**: PSE, Nequi, Daviplata y Tarjetas de Crédito/Débito.\n- **Transferencia**: Bancolombia.\n- **Financiación**: Posibilidad de pagar módulo a módulo bimestralmente sin intereses adicionales."
    },
    # 4. SPECIFIC INTENT: SCHEDULES & TIMETABLES
    {
        "keywords": ["horario", "horarios", "que horarios", "franjas horarias", "dias de clase", "sabados", "sabatinos", "en la noche", "en la manana", "en la tarde", "a que hora"],
        "response": "Contamos con amplias franjas horarias adaptadas a tu tiempo:\n- **Plan Regular (Lunes a Jueves - 2h/día)**:\n  • Mañana: 6:00 AM - 8:00 AM\n  • Tarde: 2:00 PM - 4:00 PM\n  • Noche: 6:00 PM - 8:00 PM y 8:00 PM - 10:00 PM\n- **Plan Sabatino Intensivo (Sábados)**: 8:00 AM a 1:00 PM."
    },
    # 5. SPECIFIC INTENT: COURSES, PROGRAMS & LEVELS
    {
        "keywords": ["programas", "cursos", "niveles", "mcer", "a1", "a2", "b1", "b2", "c1", "cuantos niveles"],
        "response": "Ofrecemos programas en **Inglés, Francés, Alemán e Italiano** estructurados según el MCER:\n- **Nivel A1** (Principiante): 4 meses (2 módulos)\n- **Nivel A2** (Básico): 4 meses (2 módulos)\n- **Nivel B1** (Intermedio): 6 meses (3 módulos)\n- **Nivel B2** (Intermedio Alto): 6 meses (3 módulos)\n- **Nivel C1** (Avanzado): 4 meses (2 módulos)\nCada módulo bimestral consta de 40 horas lectivas guiadas con profesor en vivo."
    },
    # 6. SPECIFIC INTENT: LANGUAGES OFFERED
    {
        "keywords": ["idiomas", "dictan", "ensenan", "enseñan", "ingles", "frances", "aleman", "italiano", "lenguas", "ofrecen"],
        "response": "En **Horizon Academy** enseñamos **Inglés, Francés, Alemán e Italiano** con metodología 100% enfocada en conversación, clases en vivo con profesores expertos y contenido digital alineado al MCER."
    },
    # 7. SPECIFIC INTENT: NON-OFFERED LANGUAGES
    {
        "keywords": ["chino", "portugues", "coreano", "neerlandes", "japones", "arabe", "ruso", "otro idioma"],
        "response": "Actualmente, en **Horizon Academy** nos especializamos en **Inglés, Francés, Alemán e Italiano**. Si deseas solicitar información sobre futuras aperturas de otros idiomas, contáctanos aquí: " + ESCALATION_FORM_URL
    },
    # 8. SPECIFIC INTENT: METHODOLOGY & TEACHERS
    {
        "keywords": ["metodologia", "metodo de enseñanza", "como enseñan", "como dictan las clases", "como son las clases", "profesores", "docentes", "nativos"],
        "response": "Nuestra metodología combina clases sincrónicas en vivo con profesores expertos y nativos, material digital interactivo y ejercicios prácticos de conversación. Cada módulo bimestral incluye 40 horas lectivas y 20 horas de aprendizaje autónomo 24/7."
    },
    # 9. SPECIFIC INTENT: REGISTRATION & ENROLLMENT PROCESS
    {
        "keywords": ["como se matricula", "como me matriculo", "como hago la matricula", "como hago la inscripción", "como me inscribo", "proceso de matricula", "proceso de inscripción", "formulario de inscripcion", "inscribirme"],
        "response": "¡Es muy fácil! Puedes inscribirte directamente desde el botón **'Inscripciones'** en la parte superior de nuestra página web o diligenciar nuestro formulario. Solo necesitas tu documento de identidad. Si deseas asesoría personalizada, puedes escribirnos aquí: " + ESCALATION_FORM_URL
    },
    # 10. SPECIFIC INTENT: PLACEMENT TEST / EXAM
    {
        "keywords": ["examen de clasificacion", "prueba de nivel", "saber mi nivel", "homologacion", "evaluacion inicial", "nivelamento", "test gratis", "test de nivel"],
        "response": "Realizamos **exámenes de clasificación 100% gratuitos** online y presenciales para evaluar tu nivel actual (A1 a C1). La prueba dura 25 minutos. Si tienes conocimientos previos, puedes solicitar tu test registrándote en nuestra web o a través del formulario: " + ESCALATION_FORM_URL
    },
    # 11. SPECIFIC INTENT: CERTIFICATES & OFFICIAL VALIDATION
    {
        "keywords": ["certificado", "diploma", "constancia de estudio", "certificado de notas", "descargar certificado", "certificacion mcer", "avalado", "oficial"],
        "response": "Al aprobar cada nivel del MCER con nota mínima de 75/100, expedimos un **Certificado Digital con código QR de verificación institucional**. Si requieres una constancia de estudio vigente, solicítala mediante nuestro formulario: " + ESCALATION_FORM_URL
    },
    # 12. SPECIFIC INTENT: INTERNATIONAL EXAM PREPARATION
    {
        "keywords": ["ielts", "toefl", "delf", "dalf", "goethe", "testdaf", "celi", "examen internacional", "preparacion examenes"],
        "response": "Contamos con cursos especializados de preparación y simulación para exámenes internacionales: IELTS, TOEFL iBT, DELF/DALF (francés), Goethe/TestDaF (alemán) y CELI (italiano)."
    },
    # 13. SPECIFIC INTENT: MATERIALS & BOOKS
    {
        "keywords": ["libros", "libro", "material de estudio", "comprar libro", "costo de libros", "guia de estudio", "material digital", "plataforma"],
        "response": "¡No tienes que comprar libros costosos! Todo el material digital, libros interactivos y plataforma 24/7 vienen **100% incluidos sin costo adicional** en el valor de tu módulo."
    },
    # 14. SPECIFIC INTENT: MODALITIES (ONLINE VS PRESENCIAL)
    {
        "keywords": ["modalidad", "virtual o presencial", "clases online", "clases virtuales", "remoto", "en vivo", "sede fisica", "presencial"],
        "response": "Contamos con dos modalidades totalmente equivalentes:\n- **Virtual en Vivo**: Vía Zoom/Meet con docente en tiempo real y campus 24/7.\n- **Presencial**: En nuestra sede principal de Bogotá (Calle 72 # 11-40) con laboratorios multimedia."
    },
    # 15. SPECIFIC INTENT: LOCATION & ADDRESS
    {
        "keywords": ["ubicacion", "direccion", "donde quedan", "donde estan ubicados", "sede principal", "parqueadero", "bogota"],
        "response": "Nuestra sede principal presencial se encuentra ubicada en la **Calle 72 # 11-40, Bogotá D.C.** Contamos con aulas interactivas, laboratorios de conversación y parqueadero para estudiantes."
    },
    # 16. SPECIFIC INTENT: REQUIREMENTS & MINIMUM AGE
    {
        "keywords": ["requisitos", "edad minima", "ninos", "niños", "jovenes", "adultos", "edad para ingresar"],
        "response": "Nuestros programas están diseñados para jóvenes y adultos desde los 14 años de edad. Solo necesitas tu documento de identidad y ganas de aprender."
    },
    # 17. SPECIFIC INTENT: SCHEDULE CHANGES & MAKEUP CLASSES
    {
        "keywords": ["problema con el horario", "problema de horario", "cambiar de horario", "cambio de horario", "cruce de horario", "cruce de clases", "no puedo asistir", "reposicion de clase", "falte a clase", "perdi una clase"],
        "response": "Si tienes un cruce de horario o perdiste una sesión, las grabaciones quedan disponibles en plataforma hasta por 30 días. Para solicitudes formales de cambio de grupo, contacta a secretaría académica aquí: " + ESCALATION_FORM_URL
    },
    # 18. SPECIFIC INTENT: PAYMENTS, BILLING & REFUNDS
    {
        "keywords": ["devolucion", "reembolso", "problema con el pago", "error de pago", "factura electronica", "transferencia no refleja"],
        "response": "Para consultas sobre transacciones, facturación electrónica o solicitudes de reembolso, ponte en contacto directamente con el área de cartera aquí: " + ESCALATION_FORM_URL
    },
    # 19. SPECIFIC INTENT: CORPORATE & GROUP PLANS
    {
        "keywords": ["empresas", "planes corporativos", "descuento para empresas", "grupos empresariales", "capacitacion empresarial"],
        "response": "Ofrecemos programas de capacitación lingüística empresarial a la medida, con reportes periódicos de asistencia y avance para gestión de talento humano. Solicita tu cotización aquí: " + ESCALATION_FORM_URL
    },
    # 20. SPECIFIC INTENT: IDENTITY & NAME QUESTIONS
    {
        "keywords": ["como te llamas", "quien eres", "cual es tu nombre", "quien es usted", "presentate", "que eres"],
        "response": "¡Hola! Soy **Horizon**, el asistente virtual inteligente de **Horizon Academy**. Estoy aquí para ayudarte con toda la información sobre nuestros programas de idiomas, precios, horarios y matrículas."
    },
    # 21. SPECIFIC INTENT: HISTORY & YEARS OF EXPERIENCE
    {
        "keywords": ["hace cuanto", "cuantos anos", "cuantos años", "cuantos anos llevan", "cuantos años llevan", "trayectoria", "fundacion", "cuanto tiempo llevan", "historia de la academia", "experiencia"],
        "response": "Horizon Academy cuenta con más de 10 años de trayectoria formando estudiantes y profesionales con certificaciones internacionales."
    },
    # 22. SPECIFIC INTENT: HUMAN ASSISTANCE & DIRECT CONTACT
    {
        "keywords": ["humano", "asesor", "persona", "agente", "hablar con alguien", "atencion al cliente", "soporte humano", "hablar con un asesor"],
        "response": f"¡Por supuesto! Si deseas hablar directamente con un asesor humano de Horizon Academy, por favor diligencia nuestro formulario oficial aquí: {ESCALATION_FORM_URL}"
    },
    # 23. SPECIFIC INTENT: QUESTION OPENINGS & DOUBTS
    {
        "keywords": [
            "una pregunta", "tengo una duda", "una duda", "tengo una pregunta", 
            "quisiera preguntar", "quiero consultar", "una consulta", "tengo una consulta", 
            "puedo hacer una pregunta", "quiero preguntar", "hacer una pregunta", "tengo dudas"
        ],
        "response": "¡Claro que sí! Dime cuál es tu duda o pregunta y con mucho gusto te brindaré toda la información sobre nuestros cursos, horarios, precios o matrículas."
    },
    # 24. GENERAL GREETINGS
    {
        "keywords": ["hola", "hello", "buenas", "ola", "buenos dias", "buenas tardes", "buenas noches", "hey", "saludos", "que tal", "inicio"],
        "response": "¡Hola! Bienvenid@ a **Horizon Academy**. 🌍 Soy tu asistente virtual inteligente. ¿En qué te puedo ayudar hoy? Puedes preguntarme sobre precios, programas de idiomas, horarios, certificados o inscribirte directamente."
    },
    # 25. THANKS & FAREWELLS
    {
        "keywords": ["gracias", "muchas gracias", "chao", "adios", "hasta luego", "thanks", "thank you", "gachas", "excelente gracias", "vale gracias", "ok gracias"],
        "response": "¡Con mucho gusto! 😊 Estamos para servirte en Horizon Academy. ¡Que tengas un excelente día!"
    }
]

KEYBOARD_PATTERNS = ["qwerty", "asdfgh", "zxcvbn", "123456", "hjkl", "dfghj"]

def normalize_text(text: str) -> str:
    """Removes accents, punctuation, and converts text to lower case for reliable matching."""
    text = text.lower().strip()
    replacements = (
        ("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u"),
        ("ü", "u"), ("ñ", "n"), ("?", ""), ("¿", ""), ("!", ""), ("¡", ""),
        (",", ""), (".", ""), (";", ""), (":", "")
    )
    for a, b in replacements:
        text = text.replace(a, b)
    return text

def is_gibberish(text: str) -> bool:
    """
    Detects keyboard mashing, random consonants, or nonsense strings.
    Examples: 'hdysvbfs', 'dvcyusv', 'asdfghjkl', 'qwertyuiop'
    """
    cleaned = normalize_text(text).replace(" ", "")
    if not cleaned:
        return True
    
    # Check for keyboard sequence patterns (e.g. 'qwertyuiop', 'asdfghjkl')
    for pat in KEYBOARD_PATTERNS:
        if pat in cleaned:
            return True

    # Check for short repeated characters (e.g. 'aaaaa', 'hhhhh')
    if len(set(cleaned)) == 1 and len(cleaned) > 2:
        return True
        
    # Check vowel density and consonant streaks for strings of length >= 4
    if len(cleaned) >= 4:
        vowel_count = sum(1 for char in cleaned if char in "aeiou")
        vowel_ratio = vowel_count / len(cleaned)
        
        # Less than 20% vowels in a word of 4+ characters is usually gibberish
        if vowel_ratio < 0.20:
            return True
            
        # 4 or more consecutive consonants without a vowel is usually gibberish in Spanish
        consonants_streak = 0
        for char in cleaned:
            if char.isalpha() and char not in "aeiou":
                consonants_streak += 1
                if consonants_streak >= 4:
                    return True
            else:
                consonants_streak = 0

    # Catch very short gibberish words with too many consonants (e.g., 'jjb')
    if len(cleaned) == 3 and sum(1 for char in cleaned if char not in "aeiou") == 3:
        return True

    return False

def get_static_response(user_query: str):
    """
    Checks if user_query matches any static FAQ pattern or is gibberish.
    Returns response string if matched, or None if query requires RAG / LLM.
    """
    normalized_query = normalize_text(user_query)
    
    # 1. Check each static rule in priority order
    for rule in STATIC_RULES:
        for kw in rule["keywords"]:
            normalized_kw = normalize_text(kw)
            if normalized_kw in normalized_query:
                return rule["response"]
                
    # 2. Anti-Gibberish Verification Check
    if is_gibberish(user_query):
        return GIBBERISH_RESPONSE

    return None

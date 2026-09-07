"""
Skills & MCP Tools Module for Horizon Academy AI Assistant.
Provides specialized business logic calculations for tuition, discounts, placement test recommendations, level duration, and flexible installment plans.
"""

def calculate_tuition_fee(num_modules: int = 1, include_matricula: bool = False, pronto_pago: bool = False) -> str:
    """
    Skill: Calculates exact tuition fees, discounts, and total COP for Horizon Academy.
    - Base module cost: $480.000 COP
    - Matrícula (one-time): $60.000 COP
    - Trimodular discount (3+ modules): 10%
    - Pronto pago discount: 5%
    """
    base_module_price = 480000
    matricula_price = 60000 if include_matricula else 0
    
    total_modules_base = num_modules * base_module_price
    discount_text = ""
    discount_amount = 0
    
    if num_modules >= 3:
        discount_amount = total_modules_base * 0.10
        discount_text = " (Aplica 10% de descuento por Paquete Trimodular)"
    elif pronto_pago:
        discount_amount = total_modules_base * 0.05
        discount_text = " (Aplica 5% de descuento por Pronto Pago)"

    final_modules_total = total_modules_base - discount_amount
    grand_total = final_modules_total + matricula_price
    
    res = f"Para {num_modules} módulo(s): Subtotal módulos: ${total_modules_base:,.0f} COP."
    if discount_amount > 0:
        res += f" Descuento aplicado: ${discount_amount:,.0f} COP{discount_text}."
    if include_matricula:
        res += f" Matrícula inicial: $60.000 COP."
    res += f" Total final a pagar: ${grand_total:,.0f} COP."
    return res


def calculate_placement_test_recommendation(score: int) -> str:
    """
    Skill: Recommends starting MCER level and course roadmaps based on placement test score (0-100 pts).
    """
    score = max(0, min(100, score))
    
    if score <= 20:
        level = "A1 (Principiante)"
        modules_needed = 2
        months = 4
        advice = "Te recomendamos iniciar desde el Módulo 1 del Nivel A1 para construir bases sólidas de vocabulario y gramática."
    elif score <= 45:
        level = "A2 (Básico)"
        modules_needed = 2
        months = 4
        advice = "Tienes bases iniciales. Te recomendamos ingresar al Nivel A2 para fortalecer fluidez en conversaciones cotidianas."
    elif score <= 70:
        level = "B1 (Intermedio)"
        modules_needed = 3
        months = 6
        advice = "Posees un nivel funcional. En el Nivel B1 perfeccionarás tiempos verbales complejos y comunicación laboral."
    elif score <= 88:
        level = "B2 (Intermedio Alto)"
        modules_needed = 3
        months = 6
        advice = "¡Excelente nivel! El Nivel B2 te preparará para debates avanzados, argumentación fluida y certificación profesional."
    else:
        level = "C1 (Avanzado / Dominio Operativo)"
        modules_needed = 2
        months = 4
        advice = "¡Dominio avanzado! Te recomendamos el Nivel C1 enfocado en precisión lingüística, académica y negocios internacionales."
        
    return f"Con un puntaje de {score}/100 pts en tu examen de clasificación:\n" \
           f"• Nivel sugerido: **{level}**\n" \
           f"• Módulos requeridos para completar el nivel: {modules_needed} módulos ({months} meses)\n" \
           f"• Recomendación pedagógica: {advice}"


def calculate_total_course_hours(level_code: str) -> str:
    """
    Skill: Calculates total guided classroom hours and self-study platform hours for any MCER level or full program.
    """
    code = level_code.upper().strip()
    
    levels_data = {
        "A1": {"modules": 2, "guided_h": 80, "self_h": 40, "months": 4},
        "A2": {"modules": 2, "guided_h": 80, "self_h": 40, "months": 4},
        "B1": {"modules": 3, "guided_h": 120, "self_h": 60, "months": 6},
        "B2": {"modules": 3, "guided_h": 120, "self_h": 60, "months": 6},
        "C1": {"modules": 2, "guided_h": 80, "self_h": 40, "months": 4},
        "COMPLETO": {"modules": 12, "guided_h": 480, "self_h": 240, "months": 24}
    }
    
    info = levels_data.get(code, levels_data["B1"])
    total_h = info["guided_h"] + info["self_h"]
    
    return f"Para el Nivel **{code}**:\n" \
           f"• Número de módulos bimestrales: {info['modules']} módulo(s)\n" \
           f"• Horas lectivas guiadas con profesor en vivo: {info['guided_h']} horas\n" \
           f"• Horas de trabajo autónomo en plataforma 24/7: {info['self_h']} horas\n" \
           f"• Carga horaria total: **{total_h} horas** en {info['months']} meses."


def calculate_installment_plan(num_modules: int = 3) -> str:
    """
    Skill: Calculates bimestral installment payment plans for students paying per module.
    """
    base_module_price = 480000
    matricula = 60000
    
    first_payment = base_module_price + matricula
    subsequent_payments = base_module_price
    
    plan_details = f"Plan de pago por cuotas bimestrales para {num_modules} módulo(s):\n" \
                   f"• **Cuota 1 (Inscripción + Módulo 1)**: ${first_payment:,.0f} COP\n"
    
    for i in range(2, num_modules + 1):
        plan_details += f"• **Cuota {i} (Inicio Módulo {i})**: ${subsequent_payments:,.0f} COP\n"
        
    plan_details += f"*(Nota: Si cancelas la totalidad de los {num_modules} módulos por anticipado, obtienes un 10% de descuento en los módulos).* "
    return plan_details


def get_skills_instructions() -> str:
    """
    Returns skills rules to inject into the system prompt for dynamic calculation tasks.
    """
    return """
HERRAMIENTAS DE CÁLCULO Y SKILLS ACTIVAS (Úsalas para realizar cálculos y tareas numéricas sobre la documentación):
1. Skill de Tarifas y Descuentos (calculate_tuition_fee):
   - Módulo bimestral: $480.000 COP. Matrícula inicial: $60.000 COP.
   - Paquete Trimodular (3+ módulos): 10% de descuento sobre el costo total de los módulos.
   - Pronto Pago (5 días antes): 5% de descuento sobre el módulo.
2. Skill de Examen de Clasificación (calculate_placement_test_recommendation):
   - 0-20 pts -> Nivel A1 (2 módulos, 4 meses).
   - 21-45 pts -> Nivel A2 (2 módulos, 4 meses).
   - 46-70 pts -> Nivel B1 (3 módulos, 6 meses).
   - 71-88 pts -> Nivel B2 (3 módulos, 6 meses).
   - 89-100 pts -> Nivel C1 (2 módulos, 4 meses).
3. Skill de Carga Horaria (calculate_total_course_hours):
   - Nivel A1, A2 y C1: 2 módulos (80h guiadas + 40h autónomas = 120h totales).
   - Nivel B1 y B2: 3 módulos (120h guiadas + 60h autónomas = 180h totales).
   - Programa Completo (A1 a C1): 12 módulos (480h guiadas + 240h autónomas = 720h totales en 24 meses).
4. Skill de Plan de Cuotas (calculate_installment_plan):
   - Permite pagos módulo a módulo sin intereses (Cuota 1: $540.000 COP con matrícula, cuotas siguientes: $480.000 COP).
"""

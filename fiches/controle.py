# Contrôle (dominance) : corrections du NRC VAD.
# Le NRC note parfois le pouvoir de ce que le mot désigne (« oppression » : l'oppresseur)
# plutôt que le contrôle ressenti. Pour ces mots, on prend les formes anglaises qui
# décrivent l'état vécu (participes, adjectifs). Les autres mots gardent leurs termes `en`.
DO_TERMS = {
    "oppression": ["oppressed", "stifled"],
    "alarme": ["alarmed"],
    "terreur": ["terrified", "petrified"],
    "épouvante": ["terrified", "horrified"],
    "horreur": ["horrified"],
    "panique": ["panicked"],
    "affolement": ["panicked", "distraught"],
    "menacé·e (se sentir)": ["threatened", "vulnerable"],
    "pris·e au piège": ["trapped", "stuck"],
    "paralysé·e (se sentir)": ["frozen", "petrified"],
    "trahison (sentiment de)": ["betrayed", "deceived"],
    "supériorité (sentiment de)": ["superior", "smug", "haughty"],
    "commisération": ["sympathetic", "compassionate"],
    # Deuxième passe (réévaluation du 1er novembre 2026)
    "reconnaissance": ["grateful", "thankful"],
    "sollicitude": ["caring"],
    "irritation": ["irritated"],
    "humiliation": ["humiliated"],
    "mortification": ["mortified"],
    "détresse": ["distressed"],
    "deuil": ["bereaved", "grieving"],
    "choc": ["shocked"],
    "tourment": ["tormented"],
}
# Arbitrages théoriques (modèle PAD), contre le NRC qui les place bas même sur les formes ressenties.
DO_MANUAL = {"mépris": 0.30, "dédain": 0.30, "pitié": -0.20}

# Plancher du contrôle relatif (dc ≥ 0) pour la sous-famille Sérénité.
# Le NRC confond calme et faiblesse (calm, serene, relaxed sont tous notés bas), alors que le
# modèle PAD (Mehrabian) range « détendu » parmi les états maîtrisés, et que le NRC note
# « composed » (posé) à +0,36. Être apaisé·e ne veut pas dire perdre le contrôle.
DC_PLANCHER = {"calme", "détente", "quiétude", "paix intérieure", "harmonie", "soulagement",
               "bien-être", "apaisement", "sérénité"}

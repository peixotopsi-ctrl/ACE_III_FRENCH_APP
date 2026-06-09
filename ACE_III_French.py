import streamlit as st
import pandas as pd

# 1. Configuration de la page
st.set_page_config(
    page_title="ACE-III Calculateur Normatif",
    page_icon="🧠",
    layout="wide"
)

# 2. Titre et Description
st.title("🧠 Calculateur Normatif ACE-III")
st.markdown("""
**Ajustement Démographique pour la Population Française (Âge ≥ 60)** Cet outil calcule les moyennes attendues, les Z-scores résiduels et la classification clinique en fonction de l'âge et du niveau de scolarité du patient, en utilisant des modèles de régression linéaire multiple.
""")

# 3. Dictionnaire des Données Normatives
modeles = {
    "ACE-III Total": {"B0": 132.93, "B_age": -0.660, "B_edu": 0.170, "RSE": 10.70, "max": 100},
    "Attention":     {"B0": 19.00,  "B_age": -0.057, "B_edu": 0.100, "RSE": 2.33,  "max": 18},
    "Mémoire":       {"B0": 39.90,  "B_age": -0.269, "B_edu": 0.074, "RSE": 4.65,  "max": 26},
    "Fluence":       {"B0": 19.60,  "B_age": -0.128, "B_edu": 0.033, "RSE": 2.44,  "max": 14},
    "Langage":       {"B0": 30.70,  "B_age": -0.086, "B_edu": 0.012, "RSE": 2.37,  "max": 26},
    "Visuospatial":  {"B0": 25.30,  "B_age": -0.140, "B_edu": -0.054, "RSE": 2.62,  "max": 16}
}

# 4. Barre latérale (Saisie des données démographiques)
st.sidebar.header("📋 Données du Patient")
age = st.sidebar.number_input("Âge (années)", min_value=60, max_value=110, value=65, step=1)
scolarite = st.sidebar.number_input("Scolarité (années)", min_value=0, max_value=30, value=12, step=1)

st.sidebar.markdown("---")
st.sidebar.markdown("**Seuils Cliniques (Cut-offs) :**")
# O "r" antes das aspas resolve o aviso do LaTeX!
st.sidebar.markdown(r"🟢 **Normal :** $Z > -1.28$")
st.sidebar.markdown(r"🟠 **Risque :** $Z \le -1.28$ (P10)")
st.sidebar.markdown(r"🔴 **Déficit :** $Z \le -1.645$ (P5)")

# 5. Saisie des scores bruts
st.subheader("📊 Scores Bruts (Raw Scores)")
colonnes = st.columns(6)

for i, (domaine, params) in enumerate(modeles.items()):
    with colonnes[i]:
        valeur_defaut = float(params["max"]) * 0.8
        st.number_input(
            f"{domaine} (/{params['max']})", 
            min_value=0.0, 
            max_value=float(params['max']), 
            value=float(int(valeur_defaut)), 
            step=1.0,
            key=f"score_{domaine}" # Sauvegarde sécurisée
        )

# 6. Fonction de Classification Clinique
def classifier_cliniquement(z_score):
    if z_score <= -1.645:
        return "🔴 Déficit Clinique"
    elif z_score <= -1.28:
        return "🟠 Risque (Borderline)"
    else:
        return "🟢 Normal"

# 7. Moteur de calcul et Affichage
st.markdown("---")
if st.button("Exécuter l'Analyse Normative", type="primary"):
    resultats = []
    
    for domaine, params in modeles.items():
        score_brut = st.session_state[f"score_{domaine}"]
        
        moyenne_attendue = params["B0"] + (params["B_age"] * age) + (params["B_edu"] * scolarite)
        
        if moyenne_attendue > params["max"]:
            moyenne_attendue = params["max"]
            
        z_score = (score_brut - moyenne_attendue) / params["RSE"]
        classification = classifier_cliniquement(z_score)
        
        resultats.append({
            "Domaine Cognitif": domaine,
            "Score Obtenu": score_brut,
            "Moyenne Attendue": f"{moyenne_attendue:.1f}",
            "Z-Score (Écart)": f"{z_score:.2f}",
            "Interprétation Clinique": classification
        })
        
    df_resultats = pd.DataFrame(resultats)
    
    st.subheader("📝 Rapport Neuropsychologique")
    st.dataframe(
        df_resultats, 
        use_container_width=True,
        hide_index=True
    )
    
    st.caption("*Note : Le Z-Score représente le nombre d'Erreurs Standards Résiduelles (RSE) séparant le patient de la moyenne attendue pour son profil démographique.*")